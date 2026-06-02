"""
Phase 2 - Astro module (pyephem based, no network needed).

Computes, for any date:
  - moon illumination %  (Full Moon event)
  - ecliptic longitudes of Sun..Saturn
  - pairwise aspects (conjunction/sextile/square/trine/opposition) within an orb
  - an UP/DN bias from aspect "polarity" (harmonic vs hard aspects), weighted

This mirrors the "PHASE 2 - PLANETARY ASPECTS" / "PLANET COMPOSITE" panels.

NOTE: planetary aspects have no proven predictive power on markets. This module
exists to reproduce the reference indicator's logic, not to endorse it. You can
turn it off in config (astro.enabled: false).
"""
from __future__ import annotations
import datetime as dt
import math
import ephem

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
GLYPH = {"Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
         "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa"}

# aspect angle -> (name, symbol, polarity)  polarity: +harmonic / -hard / 0 neutral
# Conjunction polarity is NOT fixed: it depends on the two bodies' nature
# (benefic vs malefic) - see _conj_polarity. This matches the reference engine,
# where e.g. a Mars-Saturn conjunction reads strongly bearish.
ASPECTS = {
    0:   ("Conjunction", "\u260c", None),    # None -> resolved per body nature
    60:  ("Sextile",     "\u26b9", +1.0),
    90:  ("Square",      "\u25a1", -1.0),
    120: ("Trine",       "\u25b3", +1.0),
    180: ("Opposition",  "\u260d", -1.0),
}

# classical benefic (+) / malefic (-) nature for conjunction polarity
NATURE = {"Sun": +0.3, "Moon": +0.3, "Mercury": 0.0, "Venus": +1.0,
          "Mars": -1.0, "Jupiter": +1.0, "Saturn": -1.0}


def _conj_polarity(p: str, q: str) -> float:
    """Conjunction polarity = average nature of the two bodies.
    Mars+Saturn -> -1 (bearish); Venus+Jupiter -> +1 (bullish)."""
    return (NATURE.get(p, 0.0) + NATURE.get(q, 0.0)) / 2.0


def _lon_deg(name: str, when) -> float:
    b = getattr(ephem, name)()
    b.compute(when)
    return math.degrees(float(ephem.Ecliptic(b).lon)) % 360.0


def moon_illumination(date: dt.date) -> float:
    m = ephem.Moon()
    m.compute(ephem.Date(dt.datetime(date.year, date.month, date.day)))
    return float(m.phase)        # 0..100 %


def positions(date: dt.date) -> dict[str, float]:
    when = ephem.Date(dt.datetime(date.year, date.month, date.day))
    return {p: _lon_deg(p, when) for p in PLANETS}


def _sep(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360 - d)


def aspects(date: dt.date, orb: float = 6.0, weights: dict | None = None) -> dict:
    """Return active aspects + a composite UP/DN bias.

    weights: optional pair-weight dict like {'Jupiter-Saturn': 2.0, ...}
    """
    weights = weights or {}
    pos = positions(date)
    active = []
    score = 0.0           # +up / -down
    wsum = 0.0
    names = PLANETS
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p, q = names[i], names[j]
            sep = _sep(pos[p], pos[q])
            for ang, (aname, sym, pol) in ASPECTS.items():
                if abs(sep - ang) <= orb:
                    if pol is None:                                # conjunction
                        pol = _conj_polarity(p, q)
                    w = weights.get(f"{p}-{q}", 1.0)
                    tightness = 1 - abs(sep - ang) / orb          # 1 exact .. 0 edge
                    active.append(dict(pair=f"{GLYPH[p]}{sym}{GLYPH[q]}",
                                       p=p, q=q, aspect=aname, symbol=sym,
                                       arc=round(sep, 1), polarity=pol,
                                       weight=w, tightness=round(tightness, 2)))
                    score += pol * w * tightness
                    wsum += abs(w)
                    break
    # squash score -> probability-ish
    up = 0.5 + 0.5 * math.tanh(score / 3.0) if wsum else 0.5
    return dict(positions=pos,
                active=active,
                up=round(up * 100, 1),
                dn=round((1 - up) * 100, 1),
                bias="UP" if up > 0.52 else "DOWN" if up < 0.48 else "FLAT",
                n_aspects=len(active))


if __name__ == "__main__":
    a = aspects(dt.date(2026, 5, 30))
    print("moon illum %:", round(moon_illumination(dt.date(2026, 5, 30)), 1))
    for k, v in a["positions"].items():
        print(f"  {k:8s} {v:6.1f}")
    print("aspects:", [x["pair"] + f"({x['arc']})" for x in a["active"]])
    print("planet composite UP/DN:", a["up"], a["dn"], a["bias"])
