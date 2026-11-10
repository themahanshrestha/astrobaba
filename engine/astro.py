"""Astronomical core: Western (tropical) and Vedic (sidereal, Lahiri) calculations.

Positions come from the Swiss Ephemeris. Without ephemeris files the built-in
Moshier ephemeris is used (sub-arcminute accuracy for all bodies we use). Set
ASTROBABA_EPHE_PATH to a folder with the .se1 files for full precision.
"""
from __future__ import annotations

import datetime as dt
import math
import os
from zoneinfo import ZoneInfo

import swisseph as swe

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
ELEMENT = {s: e for s, e in zip(SIGNS, ["fire", "earth", "air", "water"] * 3)}
MODALITY = {s: m for s, m in zip(SIGNS, ["cardinal", "fixed", "mutable"] * 4)}

NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
              "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
              "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
              "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
              "Uttara Bhadrapada", "Revati"]
NAK_SPAN = 360.0 / 27

DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18,
               "Jupiter": 16, "Saturn": 19, "Mercury": 17}
YEAR_DAYS = 365.25

W_BODIES = {"Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
            "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
            "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO}
V_BODIES = {k: W_BODIES[k] for k in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}

DOMICILE = {"Sun": ["Leo"], "Moon": ["Cancer"], "Mercury": ["Gemini", "Virgo"],
            "Venus": ["Taurus", "Libra"], "Mars": ["Aries", "Scorpio"],
            "Jupiter": ["Sagittarius", "Pisces"], "Saturn": ["Capricorn", "Aquarius"]}
EXALT = {"Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo", "Venus": "Pisces",
         "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra"}
SIGN_LORD = {s: p for p, ss in DOMICILE.items() for s in ss}

swe.set_sid_mode(swe.SIDM_LAHIRI)
_EPHE = os.environ.get("ASTROBABA_EPHE_PATH")
if _EPHE:
    swe.set_ephe_path(_EPHE)
    _BASE = swe.FLG_SWIEPH
else:
    _BASE = swe.FLG_MOSEPH
F_TROP = _BASE | swe.FLG_SPEED
F_SID = F_TROP | swe.FLG_SIDEREAL


def sign_of(lon: float) -> str:
    return SIGNS[int(lon % 360 // 30)]


def sign_idx(lon: float) -> int:
    return int(lon % 360 // 30)


def deg_in_sign(lon: float) -> float:
    return lon % 30


def fmt_deg(lon: float) -> str:
    d = deg_in_sign(lon)
    return f"{int(d)}°{int(round((d % 1) * 60)):02d}'"


def dignity(planet: str, sign: str) -> str | None:
    if planet in DOMICILE and sign in DOMICILE[planet]:
        return "domicile"
    if EXALT.get(planet) == sign:
        return "exalted"
    if planet in DOMICILE:
        opp = SIGNS[(SIGNS.index(DOMICILE[planet][0]) + 6) % 12]
        opp2 = SIGNS[(SIGNS.index(DOMICILE[planet][-1]) + 6) % 12]
        if sign in (opp, opp2):
            return "detriment"
    if planet in EXALT and SIGNS[(SIGNS.index(EXALT[planet]) + 6) % 12] == sign:
        return "fall"
    return None


def to_utc(date: dt.date, hour: int, minute: int, tzname: str) -> dt.datetime:
    local = dt.datetime(date.year, date.month, date.day, hour, minute, tzinfo=ZoneInfo(tzname))
    return local.astimezone(dt.timezone.utc)


def jd_ut(utc: dt.datetime) -> float:
    utc = utc.astimezone(dt.timezone.utc)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60 + utc.second / 3600)


def _calc(jd: float, body: int, flags: int) -> tuple[float, float]:
    r = swe.calc_ut(jd, body, flags)[0]
    return r[0] % 360, r[3]


def house_of(lon: float, cusps: list[float]) -> int:
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        span = (b - a) % 360
        if (lon - a) % 360 < span:
            return i + 1
    return 1


def _houses(jd: float, lat: float, lon: float, system: bytes, flags: int = 0):
    try:
        return swe.houses_ex(jd, lat, lon, system, flags)
    except Exception:  # Placidus fails at extreme latitudes -> Porphyry
        return swe.houses_ex(jd, lat, lon, b"O", flags)


def western(jd: float, lat: float, lon: float, with_houses: bool = True) -> dict:
    pos = {}
    for name, b in W_BODIES.items():
        l, spd = _calc(jd, b, F_TROP)
        pos[name] = {"lon": l, "sign": sign_of(l), "deg": fmt_deg(l), "retro": spd < 0,
                     "dignity": dignity(name, sign_of(l))}
    nn, _ = _calc(jd, swe.TRUE_NODE, F_TROP)
    pos["North Node"] = {"lon": nn, "sign": sign_of(nn), "deg": fmt_deg(nn), "retro": True, "dignity": None}
    sn = (nn + 180) % 360
    pos["South Node"] = {"lon": sn, "sign": sign_of(sn), "deg": fmt_deg(sn), "retro": True, "dignity": None}
    out = {"planets": pos, "asc": None, "mc": None, "cusps": None}
    if with_houses:
        cusps, ascmc = _houses(jd, lat, lon, b"P")
        cusps = [c % 360 for c in cusps]
        out["cusps"] = cusps
        out["asc"] = {"lon": ascmc[0] % 360, "sign": sign_of(ascmc[0]), "deg": fmt_deg(ascmc[0])}
        out["mc"] = {"lon": ascmc[1] % 360, "sign": sign_of(ascmc[1]), "deg": fmt_deg(ascmc[1])}
        dsc = (ascmc[0] + 180) % 360
        out["dsc"] = {"lon": dsc, "sign": sign_of(dsc)}
        for n, p in pos.items():
            p["house"] = house_of(p["lon"], cusps)
    return out


def vedic(jd: float, lat: float, lon: float, with_houses: bool = True) -> dict:
    pos = {}
    for name, b in V_BODIES.items():
        l, spd = _calc(jd, b, F_SID)
        pos[name] = _vplanet(name, l, spd < 0)
    rahu, _ = _calc(jd, swe.MEAN_NODE, F_SID)
    pos["Rahu"] = _vplanet("Rahu", rahu, True)
    pos["Ketu"] = _vplanet("Ketu", (rahu + 180) % 360, True)
    out = {"planets": pos, "lagna": None, "ayanamsa": swe.get_ayanamsa_ut(jd)}
    if with_houses:
        _, ascmc = _houses(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
        la = ascmc[0] % 360
        li = sign_idx(la)
        out["lagna"] = {"lon": la, "sign": SIGNS[li], "deg": fmt_deg(la),
                        "navamsa": SIGNS[navamsa_idx(la)], "dasamsa": SIGNS[dasamsa_idx(la)]}
        for p in pos.values():
            p["house"] = (sign_idx(p["lon"]) - li) % 12 + 1
        out["house_signs"] = [SIGNS[(li + i) % 12] for i in range(12)]
    return out


def _vplanet(name: str, l: float, retro: bool) -> dict:
    nk = int(l // NAK_SPAN)
    pada = int((l % NAK_SPAN) // (NAK_SPAN / 4)) + 1
    return {"lon": l, "sign": sign_of(l), "deg": fmt_deg(l), "retro": retro,
            "nakshatra": NAKSHATRAS[nk], "nak_idx": nk, "pada": pada,
            "navamsa": SIGNS[navamsa_idx(l)], "dignity": dignity(name, sign_of(l))}


def navamsa_idx(lon: float) -> int:
    si = sign_idx(lon)
    start = {0: 0, 1: 9, 2: 6, 3: 3}[si % 4]  # fire->Aries, earth->Capricorn, air->Libra, water->Cancer
    return (start + int(deg_in_sign(lon) // (30 / 9))) % 12


def dasamsa_idx(lon: float) -> int:
    si = sign_idx(lon)
    start = si if si % 2 == 0 else (si + 8) % 12  # odd signs (Aries=idx0) start same sign; even from 9th
    return (start + int(deg_in_sign(lon) // 3)) % 12


# ---- aspects ---------------------------------------------------------------
ASPECTS = {"conjunction": (0, 8), "sextile": (60, 5), "square": (90, 7), "trine": (120, 7),
           "opposition": (180, 8)}
OUTER = {"Uranus", "Neptune", "Pluto"}


def find_aspects(items: dict[str, float], only_with: set[str] | None = None) -> list[dict]:
    names = list(items)
    res = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if (a in OUTER and b in OUTER) or ("Node" in a and "Node" in b):
                continue
            if only_with and a not in only_with and b not in only_with:
                continue
            diff = abs(items[a] - items[b]) % 360
            diff = min(diff, 360 - diff)
            for aname, (ang, orb) in ASPECTS.items():
                lum = a in ("Sun", "Moon") or b in ("Sun", "Moon")
                o = orb + (1 if lum else 0) - (2 if (a in OUTER or b in OUTER or "Node" in a + b) else 0)
                if abs(diff - ang) <= o:
                    res.append({"a": a, "b": b, "type": aname, "orb": round(abs(diff - ang), 2),
                                "max": o, "_ratio": abs(diff - ang) / o})
                    break
    res.sort(key=lambda r: (round(r["_ratio"], 6), r["a"], r["b"]))
    for r in res:
        del r["_ratio"]
    return res


# ---- Vimshottari -----------------------------------------------------------
def _add_years(d: dt.datetime, years: float) -> dt.datetime:
    return d + dt.timedelta(days=years * YEAR_DAYS)


def vimshottari(moon_sid_lon: float, birth_utc: dt.datetime) -> list[dict]:
    nk = int(moon_sid_lon // NAK_SPAN)
    elapsed = (moon_sid_lon % NAK_SPAN) / NAK_SPAN
    first = nk % 9
    lord0 = DASHA_ORDER[first]
    start = _add_years(birth_utc, -DASHA_YEARS[lord0] * elapsed)  # virtual start of first dasha
    periods = []
    for i in range(9 + 3):  # covers >120 years
        lord = DASHA_ORDER[(first + i) % 9]
        end = _add_years(start, DASHA_YEARS[lord])
        antars, s = [], start
        for j in range(9):
            sub = DASHA_ORDER[(DASHA_ORDER.index(lord) + j) % 9]
            e = _add_years(s, DASHA_YEARS[lord] * DASHA_YEARS[sub] / 120)
            antars.append({"lord": sub, "start": s, "end": e})
            s = e
        periods.append({"lord": lord, "start": start, "end": end, "antars": antars})
        start = end
    return periods


def current_dasha(periods: list[dict], when: dt.datetime) -> dict | None:
    for p in periods:
        if p["start"] <= when < p["end"]:
            ant = next((a for a in p["antars"] if a["start"] <= when < a["end"]), None)
            return {"maha": p, "antar": ant}
    return None


def saturn_sade_sati(moon_sign_idx: int, when: dt.datetime) -> str | None:
    l, _ = _calc(jd_ut(when), swe.SATURN, F_SID)
    d = (sign_idx(l) - moon_sign_idx) % 12
    return {11: "rising", 0: "peak", 1: "setting"}.get(d)


def transit_signs(when: dt.datetime) -> dict:
    jd = jd_ut(when)
    return {n: sign_of(_calc(jd, b, F_SID)[0]) for n, b in
            {"Saturn": swe.SATURN, "Jupiter": swe.JUPITER}.items()}


def angular_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)
