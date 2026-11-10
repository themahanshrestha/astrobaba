"""BaZi (Chinese Four Pillars). Year changes at Lichun (Sun at 315 deg), months follow the twelve
solar terms (Sun longitude), the day pillar is the 60-day cycle, and the hour pillar is a two-hour
branch. Conventions: clock time is used for the hour pillar (no solar-time correction); the day
rolls over at 23:00 (late Zi hour counts toward the next day). Hidden stems are not used."""
from __future__ import annotations

import datetime as dt

from content.extra import (ANIMALS, BRANCH_ELEMENT, BRANCHES, CLASHES, SIX_HARMONY, STEM_ELEMENT, STEMS, TRINES)

ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
PRODUCES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROLS = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}


def pillar_from_index(idx: int) -> dict:
    s, b = idx % 10, idx % 12
    return stem_branch(s, b)


def stem_branch(s: int, b: int) -> dict:
    return {"stem": STEMS[s], "branch": BRANCHES[b], "animal": ANIMALS[b], "stem_el": STEM_ELEMENT[s],
            "branch_el": BRANCH_ELEMENT[b], "polarity": "Yang" if s % 2 == 0 else "Yin", "_s": s, "_b": b}


def day_index(d: dt.date) -> int:
    jdn = d.toordinal() + 1721425
    return (jdn - 2451545 + 54) % 60   # 2000-01-01 = Wu-Wu (index 54)


def pillars(sun_lon: float, local: dt.datetime, with_hour: bool) -> dict:
    y = local.year
    if local.month <= 2 and 270 <= sun_lon < 315:
        y -= 1
    ys = (y - 4) % 10
    year = stem_branch(ys, (y - 4) % 12)
    m = int(((sun_lon - 315) % 360) // 30)
    month = stem_branch(((ys % 5) * 2 + 2 + m) % 10, (2 + m) % 12)
    day_date = local.date() + (dt.timedelta(days=1) if local.hour >= 23 else dt.timedelta())
    di = day_index(day_date)
    day = pillar_from_index(di)
    out = {"year": year, "month": month, "day": day, "hour": None}
    if with_hour:
        hb = ((local.hour + 1) // 2) % 12
        out["hour"] = stem_branch(((day["_s"] % 5) * 2 + hb) % 10, hb)
    return out


def day_master(p: dict) -> str:
    d = p["day"]
    return f"{d['polarity']} {d['stem_el']}"


def element_counts(p: dict) -> dict:
    c = {e: 0.0 for e in ELEMENTS}
    for k, pl in p.items():
        if not pl:
            continue
        c[pl["stem_el"]] += 1.0
        c[pl["branch_el"]] += 1.5 if k == "month" else 1.0
    return c


def public(p: dict) -> dict:
    out = {}
    for k, pl in p.items():
        out[k] = None if not pl else {x: v for x, v in pl.items() if not x.startswith("_")}
    out["day_master"] = day_master(p)
    out["elements"] = element_counts(p)
    return out


def element_relation(a: str, b: str) -> str:
    if a == b:
        return "same"
    if PRODUCES[a] == b or PRODUCES[b] == a:
        return "supportive"
    if CONTROLS[a] == b or CONTROLS[b] == a:
        return "controlling"
    return "neutral"


def animal_relation(a: str, b: str) -> str:
    if a == b:
        return "same"
    if frozenset((a, b)) in SIX_HARMONY:
        return "harmony"
    if any(a in t and b in t for t in TRINES):
        return "trine"
    if frozenset((a, b)) in CLASHES:
        return "clash"
    return "neutral"
