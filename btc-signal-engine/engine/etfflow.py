"""
US spot-ETF flow (live, best-effort) - the strongest medium-term DEMAND signal.
====================================================================
Since Jan 2024 the daily net creations/redemptions of the US spot Bitcoin ETFs
(IBIT, FBTC, ...) are the cleanest public read on real institutional demand.
Multi-week trends in price tend to follow multi-day trends in net flow.

Source: farside.co.uk public flow table (scraped, no key). Everything degrades
to None when offline/blocked - the engine never breaks (same contract as
realflow.py). Units: USD millions per day.

  build(cfg) -> dict(last=(date,total), sum5, sum10, prev5, trend, bias, n_days)
"""
from __future__ import annotations
import re


_URL = "https://farside.co.uk/btc/"
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}


def _num(cell: str) -> float | None:
    """Parse a farside number cell: '1,234.5', '(123.4)' = negative, '-' = 0."""
    t = re.sub(r"<[^>]+>", "", cell).replace("&nbsp;", " ").strip()
    if t in ("", "-", "–"):
        return 0.0
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()").replace(",", "")
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def fetch_rows(limit: int = 40) -> list[tuple[str, float]] | None:
    """[(date_str, total_flow_musd)] most-recent-last; None if unreachable."""
    try:
        import requests
        r = requests.get(_URL, headers=_UA, timeout=15)
        r.raise_for_status()
        html = r.text
    except Exception:                                       # noqa: BLE001
        return None
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)
        if len(cells) < 3:
            continue
        d = re.sub(r"<[^>]+>", "", cells[0]).strip()
        if not re.match(r"^\d{1,2}\s+\w{3}\s+\d{4}$", d):   # e.g. '17 Jul 2026'
            continue
        total = _num(cells[-1])                              # last column = Total
        if total is None:
            continue
        rows.append((d, total))
    return rows[-limit:] if rows else None


def build(cfg: dict) -> dict | None:
    ec = cfg.get("etfflow", {})
    if not ec.get("enabled", True):
        return None
    rows = fetch_rows()
    if not rows:
        return None
    vals = [v for _, v in rows]
    sum5 = sum(vals[-5:])
    prev5 = sum(vals[-10:-5]) if len(vals) >= 10 else None
    sum10 = sum(vals[-10:]) if len(vals) >= 10 else None
    trend = ("n/a" if prev5 is None else
             "improving" if sum5 > prev5 else "fading" if sum5 < prev5 else "flat")
    # bias: the 5-day net flow sign, softened by the trend
    if sum5 > 0:
        bias = "UP" if trend != "fading" else "UP-fading"
    elif sum5 < 0:
        bias = "DOWN" if trend != "improving" else "DOWN-improving"
    else:
        bias = "NEUTRAL"
    return dict(last=rows[-1], sum5=round(sum5, 1), sum10=(round(sum10, 1) if sum10 is not None else None),
                prev5=(round(prev5, 1) if prev5 is not None else None),
                trend=trend, bias=bias, n_days=len(rows))
