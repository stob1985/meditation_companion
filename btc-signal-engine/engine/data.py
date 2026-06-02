"""
Data layer.

Ways to get OHLCV:
  1) load_live()      -> pulls real klines from a PUBLIC exchange API. Tries several
                         exchanges in order and uses the first that answers, so it
                         keeps working when one venue is geo-blocked / rate-limited.
  2) load_csv(path)   -> reads a CSV you already have.
  3) make_synthetic() -> generates fake-but-realistic data so the engine can be
                         tested fully offline.

The DataFrame returned always has a UTC DatetimeIndex and columns:
  open, high, low, close, volume

Exchange notes
--------------
Bybit is 403-blocked from some clouds, so it is NOT in the default chain.
The default chain (OKX, Hyperliquid, Binance.US, Coinbase, Kraken) is reachable
from most regions. Override with cfg["data"]["exchange"] or the EXCHANGE arg
("auto" = try the whole chain).
"""
from __future__ import annotations
import datetime as dt
import time
import numpy as np
import pandas as pd

# interval token (config) -> per-exchange interval string. None = unsupported.
_INTERVAL_MAP = {
    "okx":        {"D": "1D",  "60": "1H",  "120": "2H",  "240": "4H"},
    "hyperliquid":{"D": "1d",  "60": "1h",  "120": None,  "240": "4h"},
    "binanceus":  {"D": "1d",  "60": "1h",  "120": "2h",  "240": "4h"},
    "coinbase":   {"D": 86400, "60": 3600,  "120": 7200,  "240": 14400},
    "kraken":     {"D": 1440,  "60": 60,    "120": None,  "240": 240},
    "bybit":      {"D": "D",   "60": "60",  "120": "120", "240": "240"},
}

# config symbol -> per-exchange instrument id
_SYMBOL_MAP = {
    "okx":        {"BTCUSDT": "BTC-USDT", "ETHUSDT": "ETH-USDT"},
    "hyperliquid":{"BTCUSDT": "BTC",      "ETHUSDT": "ETH"},
    "binanceus":  {"BTCUSDT": "BTCUSDT",  "ETHUSDT": "ETHUSDT"},
    "coinbase":   {"BTCUSDT": "BTC-USD",  "ETHUSDT": "ETH-USD"},
    "kraken":     {"BTCUSDT": "XBTUSD",   "ETHUSDT": "ETHUSD"},
    "bybit":      {"BTCUSDT": "BTCUSDT",  "ETHUSDT": "ETHUSDT"},
}

_DEFAULT_CHAIN = ["okx", "hyperliquid", "binanceus", "coinbase", "kraken"]


# ---------------------------------------------------------------- live fetch
def load_live(symbol: str = "BTCUSDT", interval: str = "D", limit: int = 1000,
              exchange: str = "auto", verbose: bool = True) -> pd.DataFrame:
    """Pull real klines from a public exchange.

    exchange: "auto" tries the default chain; or name one of
              okx / hyperliquid / binanceus / coinbase / kraken / bybit.
    """
    chain = _DEFAULT_CHAIN if exchange in (None, "auto") else [exchange]
    errors = []
    for ex in chain:
        bar = _INTERVAL_MAP.get(ex, {}).get(str(interval))
        inst = _SYMBOL_MAP.get(ex, {}).get(symbol)
        if bar is None or inst is None:
            errors.append(f"{ex}: interval {interval}/symbol {symbol} unsupported")
            continue
        try:
            df = _FETCHERS[ex](inst, bar, limit)
            if df is not None and len(df):
                if verbose:
                    print(f"   data: {ex} {inst} {interval}  ({len(df)} bars, "
                          f"{df.index[0].date()} -> {df.index[-1].date()})")
                return df
            errors.append(f"{ex}: empty response")
        except Exception as e:                                    # noqa: BLE001
            errors.append(f"{ex}: {type(e).__name__} {e}")
    raise RuntimeError("live fetch failed on all venues:\n   " + "\n   ".join(errors))


def _finalize(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df = df.sort_index()[["open", "high", "low", "close", "volume"]]
    return df[~df.index.duplicated(keep="last")]


def _fetch_okx(inst: str, bar: str, limit: int) -> pd.DataFrame:
    import requests
    url = "https://www.okx.com/api/v5/market/candles"
    rows, after = [], None
    while len(rows) < limit:
        params = dict(instId=inst, bar=bar, limit=300)
        if after:
            params["after"] = after                # records older than this ts
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        chunk = r.json().get("data", [])
        if not chunk:
            break
        rows.extend(chunk)
        after = chunk[-1][0]                        # oldest ts in chunk
        if len(chunk) < 300:
            break
        time.sleep(0.12)
    rows = rows[:limit]
    df = pd.DataFrame([(c[0], c[1], c[2], c[3], c[4], c[5]) for c in rows],
                      columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms", utc=True)
    return _finalize(df.set_index("ts"))


def _fetch_hyperliquid(inst: str, bar: str, limit: int) -> pd.DataFrame:
    import requests
    secs = {"1d": 86400, "4h": 14400, "1h": 3600}[bar]
    end = int(time.time() * 1000)
    start = end - (limit + 5) * secs * 1000
    r = requests.post("https://api.hyperliquid.xyz/info",
                      json={"type": "candleSnapshot",
                            "req": {"coin": inst, "interval": bar,
                                    "startTime": start, "endTime": end}},
                      timeout=20)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame([(c["t"], c["o"], c["h"], c["l"], c["c"], c["v"]) for c in data],
                      columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms", utc=True)
    return _finalize(df.set_index("ts")).tail(limit)


def _fetch_binanceus(inst: str, bar: str, limit: int) -> pd.DataFrame:
    import requests
    url = "https://api.binance.us/api/v3/klines"
    rows, end = [], None
    while len(rows) < limit:
        params = dict(symbol=inst, interval=bar, limit=1000)
        if end:
            params["endTime"] = end
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        chunk = r.json()
        if not chunk:
            break
        rows = chunk + rows
        end = chunk[0][0] - 1
        if len(chunk) < 1000:
            break
        time.sleep(0.12)
    rows = rows[-limit:]
    df = pd.DataFrame([(c[0], c[1], c[2], c[3], c[4], c[5]) for c in rows],
                      columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms", utc=True)
    return _finalize(df.set_index("ts"))


def _fetch_coinbase(inst: str, gran: int, limit: int) -> pd.DataFrame:
    import requests
    url = f"https://api.exchange.coinbase.com/products/{inst}/candles"
    rows, end = [], dt.datetime.now(dt.timezone.utc)
    headers = {"User-Agent": "btc-signal-engine"}
    for _ in range(max(1, (limit // 300) + 1)):
        start = end - dt.timedelta(seconds=gran * 300)
        params = dict(granularity=gran, start=start.isoformat(), end=end.isoformat())
        r = requests.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()
        chunk = r.json()                            # [time, low, high, open, close, vol]
        if not chunk:
            break
        rows.extend(chunk)
        end = dt.datetime.fromtimestamp(min(c[0] for c in chunk), dt.timezone.utc)
        if len(rows) >= limit:
            break
        time.sleep(0.2)
    df = pd.DataFrame(rows, columns=["ts", "low", "high", "open", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="s", utc=True)
    return _finalize(df.set_index("ts")).tail(limit)


def _fetch_kraken(inst: str, interval: int, limit: int) -> pd.DataFrame:
    import requests
    url = "https://api.kraken.com/0/public/OHLC"
    r = requests.get(url, params=dict(pair=inst, interval=interval), timeout=20)
    r.raise_for_status()
    res = r.json()["result"]
    key = next(k for k in res if k != "last")
    # [time, open, high, low, close, vwap, volume, count]
    df = pd.DataFrame([(c[0], c[1], c[2], c[3], c[4], c[6]) for c in res[key]],
                      columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="s", utc=True)
    return _finalize(df.set_index("ts")).tail(limit)


def _fetch_bybit(inst: str, bar: str, limit: int) -> pd.DataFrame:
    import requests
    url = "https://api.bybit.com/v5/market/kline"
    r = requests.get(url, params=dict(category="linear", symbol=inst,
                                      interval=bar, limit=min(limit, 1000)), timeout=20)
    r.raise_for_status()
    rows = r.json()["result"]["list"]
    df = pd.DataFrame([(c[0], c[1], c[2], c[3], c[4], c[5]) for c in rows],
                      columns=["ts", "open", "high", "low", "close", "volume"])
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="ms", utc=True)
    return _finalize(df.set_index("ts"))


_FETCHERS = {
    "okx": _fetch_okx, "hyperliquid": _fetch_hyperliquid,
    "binanceus": _fetch_binanceus, "coinbase": _fetch_coinbase,
    "kraken": _fetch_kraken, "bybit": _fetch_bybit,
}


# ---------------------------------------------------------------- csv
def load_csv(path: str, ts_col: str = "ts") -> pd.DataFrame:
    df = pd.read_csv(path)
    df[ts_col] = pd.to_datetime(df[ts_col], utc=True)
    return df.set_index(ts_col)[["open", "high", "low", "close", "volume"]].sort_index()


# ---------------------------------------------------------------- synthetic
def make_synthetic(n_days: int = 900, start: str = "2024-01-01",
                   seed: int = 7, start_price: float = 42000.0) -> pd.DataFrame:
    """Geometric random walk with volatility clustering + occasional shocks.
    Good enough to exercise every code path; NOT real data."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=n_days, freq="D", tz="UTC")
    vol = 0.025
    closes, opens, highs, lows, volumes = [], [], [], [], []
    px = start_price
    for i in range(n_days):
        vol = 0.9 * vol + 0.1 * abs(rng.normal(0.025, 0.01))       # GARCH-ish
        if rng.random() < 0.02:                                     # shock day
            vol *= rng.uniform(2, 4)
        ret = rng.normal(0.0006, vol)
        o = px
        c = px * (1 + ret)
        hi = max(o, c) * (1 + abs(rng.normal(0, vol / 2)))
        lo = min(o, c) * (1 - abs(rng.normal(0, vol / 2)))
        v = abs(rng.normal(1.0, 0.4)) * 1e6 * (1 + 3 * (vol > 0.04))
        opens.append(o); closes.append(c); highs.append(hi); lows.append(lo); volumes.append(v)
        px = c
    return pd.DataFrame(dict(open=opens, high=highs, low=lows, close=closes, volume=volumes), index=idx)


if __name__ == "__main__":
    d = make_synthetic()
    print(d.tail())
    print(d.shape)
