"""Timing techniques: annual profections, secondary progressions, solar return, transits."""
from __future__ import annotations

import datetime as dt

import swisseph as swe

from content.extra import HOUSE_NAME, HOUSE_THEME
from . import astro as A

_EPH = swe.FLG_SWIEPH if A._BASE == swe.FLG_SWIEPH else swe.FLG_MOSEPH


def _age(birth: dt.date, today: dt.date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def profection(asc_sign: str | None, age: int) -> dict | None:
    if not asc_sign:
        return None
    h = age % 12
    sign = A.SIGNS[(A.SIGNS.index(asc_sign) + h) % 12]
    return {"age": age, "house": h + 1, "house_name": HOUSE_NAME[h], "house_theme": HOUSE_THEME[h],
            "sign": sign, "lord": A.SIGN_LORD[sign]}


def solar_return(natal_sun: float, birth: dt.date, today: dt.date, lat: float, lon: float, houses: bool) -> dict:
    def jd_of(y):
        return swe.julday(y, birth.month, min(birth.day, 28), 0.0) - 6
    sr = swe.solcross_ut(natal_sun, jd_of(today.year), _EPH)
    today_jd = swe.julday(today.year, today.month, today.day, 12.0)
    if sr > today_jd:
        sr = swe.solcross_ut(natal_sun, jd_of(today.year - 1), _EPH)
    chart = A.western(sr, lat, lon, with_houses=houses)
    y, m, d, h = swe.revjul(sr)
    return {"date": f"{y:04d}-{m:02d}-{d:02d}", "moon_sign": chart["planets"]["Moon"]["sign"],
            "asc_sign": chart["asc"]["sign"] if houses else None}


def progressed(birth_jd: float, today: dt.date) -> dict:
    today_jd = swe.julday(today.year, today.month, today.day, 12.0)
    pjd = birth_jd + (today_jd - birth_jd) / 365.2422
    sun, _ = A._calc(pjd, swe.SUN, A.F_TROP)
    moon, _ = A._calc(pjd, swe.MOON, A.F_TROP)
    return {"sun_sign": A.sign_of(sun), "moon_sign": A.sign_of(moon)}


def transits(today: dt.date, asc_sign: str | None) -> dict:
    jd = swe.julday(today.year, today.month, today.day, 12.0)
    out = {}
    for name, body in (("Saturn", swe.SATURN), ("Jupiter", swe.JUPITER)):
        l, spd = A._calc(jd, body, A.F_TROP)
        s = A.sign_of(l)
        out[name] = {"sign": s, "retro": spd < 0,
                     "house": ((A.SIGNS.index(s) - A.SIGNS.index(asc_sign)) % 12 + 1) if asc_sign else None}
    return out


def compute(birth: dt.date, birth_jd: float, natal_sun: float, asc_sign: str | None, lat: float, lon: float,
            today: dt.date, houses_exact: bool) -> dict:
    age = _age(birth, today)
    return {"age": age, "profection": profection(asc_sign, age), "progressed": progressed(birth_jd, today),
            "solar_return": solar_return(natal_sun, birth, today, lat, lon, houses_exact),
            "transits": transits(today, asc_sign)}
