"""Builds a full profile from birth input, handling exact / approximate / unknown birth times.

Time-sensitive facts (Rising sign, houses, Lagna, Moon sign near a boundary, dasha dates) are
computed over a set of sample moments inside the plausible window. Each distinct outcome keeps
its probability, which later scales the weight of every signal derived from it.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from dataclasses import dataclass

from zoneinfo import ZoneInfo

import swisseph as swe

from . import astro as A
from . import bazi as BZ
from . import numerology as N
from . import timing as T


@dataclass
class Birth:
    name: str
    date: dt.date
    time_mode: str          # exact | approx | unknown
    hour: int = 12
    minute: int = 0
    window_min: int = 120   # +- minutes for approx
    lat: float = 0.0
    lon: float = 0.0
    tz: str = "UTC"
    place: str = ""
    current_name: str | None = None


def _samples(b: Birth) -> list[tuple[dt.datetime, float]]:
    """(utc_datetime, weight) samples covering the plausible birth window."""
    if b.time_mode == "exact":
        return [(A.to_utc(b.date, b.hour, b.minute, b.tz), 1.0)]
    if b.time_mode == "approx":
        w = max(5, min(b.window_min, 720))
        centre = b.hour * 60 + b.minute
        step = max(5, w // 12)
        offs = list(range(-w, w + 1, step))
        out = []
        for o in offs:
            t = centre + o
            day = b.date + dt.timedelta(days=t // 1440)
            t %= 1440
            out.append((A.to_utc(day, t // 60, t % 60, b.tz), 1.0))
        return [(u, 1.0 / len(out)) for u, _ in out]
    # unknown: every hour of the local day
    out = [(A.to_utc(b.date, h, 0, b.tz), 1.0 / 24) for h in range(24)]
    return out


def _dist(values: list[tuple[str, float]]) -> dict[str, float]:
    c: Counter = Counter()
    for v, w in values:
        c[v] += w
    tot = sum(c.values())
    return {k: round(v / tot, 3) for k, v in sorted(c.items(), key=lambda kv: -kv[1])}


def build(b: Birth, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    samples = _samples(b)
    has_time = b.time_mode in ("exact", "approx")
    ref_utc = A.to_utc(b.date, b.hour if b.time_mode != "unknown" else 12,
                       b.minute if b.time_mode != "unknown" else 0, b.tz)
    ref_jd = A.jd_ut(ref_utc)
    houses_ok = b.time_mode == "exact"

    ref_w = A.western(ref_jd, b.lat, b.lon, with_houses=houses_ok)
    ref_v = A.vedic(ref_jd, b.lat, b.lon, with_houses=houses_ok)

    # distributions for time-sensitive items
    dist = {"w": {}, "v": {}, "dasha": None}
    if b.time_mode != "exact":
        wl, vl, rise_w, rise_v, mc_w, dsc_w, nak, dasha_lords = [], [], [], [], [], [], [], []
        mahas = []
        for utc, wt in samples:
            jd = A.jd_ut(utc)
            ww = A.western(jd, b.lat, b.lon, with_houses=has_time)
            vv = A.vedic(jd, b.lat, b.lon, with_houses=has_time)
            wl.append((ww["planets"]["Moon"]["sign"], wt))
            vl.append((vv["planets"]["Moon"]["sign"], wt))
            nak.append((vv["planets"]["Moon"]["nakshatra"], wt))
            if has_time:
                rise_w.append((ww["asc"]["sign"], wt)); mc_w.append((ww["mc"]["sign"], wt))
                dsc_w.append((ww["dsc"]["sign"], wt)); rise_v.append((vv["lagna"]["sign"], wt))
            per = A.vimshottari(vv["planets"]["Moon"]["lon"], utc)
            cd = A.current_dasha(per, dt.datetime.combine(today, dt.time(12), tzinfo=dt.timezone.utc))
            if cd:
                dasha_lords.append((cd["maha"]["lord"], wt))
                mahas.append((cd, wt))
        dist["w"] = {"moon": _dist(wl), "asc": _dist(rise_w) if has_time else {}, "mc": _dist(mc_w) if has_time else {},
                     "dsc": _dist(dsc_w) if has_time else {}}
        dist["v"] = {"moon": _dist(vl), "lagna": _dist(rise_v) if has_time else {}, "nakshatra": _dist(nak)}
        dist["dasha"] = _dist(dasha_lords)
    else:
        dist["w"] = {"moon": {ref_w["planets"]["Moon"]["sign"]: 1.0}, "asc": {ref_w["asc"]["sign"]: 1.0},
                     "mc": {ref_w["mc"]["sign"]: 1.0}, "dsc": {ref_w["dsc"]["sign"]: 1.0}}
        dist["v"] = {"moon": {ref_v["planets"]["Moon"]["sign"]: 1.0}, "lagna": {ref_v["lagna"]["sign"]: 1.0},
                     "nakshatra": {ref_v["planets"]["Moon"]["nakshatra"]: 1.0}}

    # Sun sign can change on the cusp day: check across the window too
    sun_w = _dist([(A.western(A.jd_ut(u), b.lat, b.lon, False)["planets"]["Sun"]["sign"], wt) for u, wt in samples])
    sun_v = _dist([(A.vedic(A.jd_ut(u), b.lat, b.lon, False)["planets"]["Sun"]["sign"], wt) for u, wt in samples])
    dist["w"]["sun"] = sun_w
    dist["v"]["sun"] = sun_v

    # Vedic dasha from the reference chart (display) + current dasha now
    moon_v = ref_v["planets"]["Moon"]
    periods = A.vimshottari(moon_v["lon"], ref_utc)
    now = dt.datetime.combine(today, dt.time(12), tzinfo=dt.timezone.utc)
    cur = A.current_dasha(periods, now)

    aspects = A.find_aspects({k: p["lon"] for k, p in ref_w["planets"].items()} |
                             ({"Asc": ref_w["asc"]["lon"], "MC": ref_w["mc"]["lon"]} if houses_ok else {}),
                             only_with={"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Asc", "MC"})
    elem_counts = {"fire": 0.0, "earth": 0.0, "air": 0.0, "water": 0.0}
    mod_counts = {"cardinal": 0.0, "fixed": 0.0, "mutable": 0.0}
    wts = {"Sun": 3, "Moon": 3, "Mercury": 2, "Venus": 2, "Mars": 2, "Jupiter": 1.5, "Saturn": 1.5,
           "Uranus": 0.5, "Neptune": 0.5, "Pluto": 0.5}
    for p, w in wts.items():
        s = ref_w["planets"][p]["sign"]
        elem_counts[A.ELEMENT[s]] += w
        mod_counts[A.MODALITY[s]] += w
    if houses_ok:
        s = ref_w["asc"]["sign"]
        elem_counts[A.ELEMENT[s]] += 3
        mod_counts[A.MODALITY[s]] += 3

    # Yogas (simple, time-light)
    yogas = []
    vp = ref_v["planets"]
    ms = A.sign_idx(vp["Moon"]["lon"])
    if (A.sign_idx(vp["Jupiter"]["lon"]) - ms) % 12 in (0, 3, 6, 9):
        yogas.append("Gaja Kesari")
    if vp["Sun"]["sign"] == vp["Mercury"]["sign"]:
        yogas.append("Budha-Aditya")
    if vp["Moon"]["sign"] == vp["Mars"]["sign"]:
        yogas.append("Chandra-Mangala")
    if houses_ok:
        li = A.SIGNS.index(ref_v["lagna"]["sign"])
        for planet, name in (("Mars", "Ruchaka"), ("Mercury", "Bhadra"), ("Jupiter", "Hamsa"),
                             ("Venus", "Malavya"), ("Saturn", "Shasha")):
            p = vp[planet]
            if p["dignity"] in ("domicile", "exalted") and (A.sign_idx(p["lon"]) - li) % 12 in (0, 3, 6, 9):
                yogas.append(name)

    # Saturn transit (Sade Sati)
    ss = A.saturn_sade_sati(A.sign_idx(moon_v["lon"]), now)
    dist_sade = None
    if b.time_mode != "exact":
        # Only meaningful if the Moon sign is certain
        dist_sade = ss if max(dist["v"]["moon"].values()) >= 0.95 else None
    sade = ss if b.time_mode == "exact" or dist_sade else None

    # birth-time reliability notes
    notes = []
    if b.time_mode == "unknown":
        notes.append("Birth time unknown: Rising sign, houses and Lagna are left out. Moon-based readings are weighted by how likely each Moon sign is across the day.")
    elif b.time_mode == "approx":
        notes.append(f"Birth time approximate (±{b.window_min} minutes): time-sensitive items are weighted by probability across that window.")
    moon_w = dist["w"]["moon"]
    if len(moon_w) > 1:
        notes.append("Your Moon sign could be " + " or ".join(f"{k} ({int(v*100)}%)" for k, v in moon_w.items()) + " depending on exact time.")
    nak_d = dist["v"]["nakshatra"]
    if len(nak_d) > 1:
        notes.append("Your Moon nakshatra could be " + " or ".join(f"{k} ({int(v*100)}%)" for k, v in nak_d.items()) + ".")
    if len(sun_w) > 1:
        notes.append("Your Sun was near a sign boundary on this day: " + " or ".join(f"{k} ({int(v*100)}%)" for k, v in sun_w.items()) + " (tropical).")
    if len(sun_v) > 1:
        notes.append("Your sidereal Sun was near a sign boundary: " + " or ".join(f"{k} ({int(v*100)}%)" for k, v in sun_v.items()) + ".")

    num = N.compute(b.name, b.date, today, b.current_name) if b.name.strip() else N.compute("", b.date, today)

    # ---- BaZi: pillars over the plausible window ---------------------------------------
    tz = ZoneInfo(b.tz)
    with_hour = b.time_mode == "exact"
    pil_counts = {k: Counter() for k in ("year", "month", "day")}
    pil_obj: dict = {}
    for utc, wt in samples:
        sun = A._calc(A.jd_ut(utc), swe.SUN, A.F_TROP)[0]
        loc = utc.astimezone(tz).replace(tzinfo=None)
        pl = BZ.pillars(sun, loc, with_hour)
        for k in pil_counts:
            key = (pl[k]["stem"], pl[k]["branch"])
            pil_counts[k][key] += wt
            pil_obj[(k,) + key] = pl[k]
        if with_hour:
            pil_obj["hour"] = pl["hour"]
    modal = {k: pil_obj[(k,) + pil_counts[k].most_common(1)[0][0]] for k in pil_counts}
    modal["hour"] = pil_obj.get("hour")
    tot = {k: sum(pil_counts[k].values()) for k in pil_counts}
    bz_dist = {
        "day_master": _dist([(f"{pil_obj[(k_,)+key]['polarity']} {pil_obj[(k_,)+key]['stem_el']}", v) for k_ in ("day",) for key, v in pil_counts[k_].items()]),
        "year_animal": _dist([(pil_obj[("year",) + key]["animal"], v) for key, v in pil_counts["year"].items()]),
        "month_animal": _dist([(pil_obj[("month",) + key]["animal"], v) for key, v in pil_counts["month"].items()]),
        "hour_animal": {modal["hour"]["animal"]: 1.0} if modal["hour"] else {},
    }
    bz_notes = [f"Your Chinese {k} pillar could be {' or '.join(f'{a} {b_} ({int(v/tot[k]*100)}%)' for (a, b_), v in pil_counts[k].most_common())}."
                for k in pil_counts if len(pil_counts[k]) > 1]
    notes += bz_notes
    bazi_out = {**BZ.public(modal), "dist": bz_dist}

    # ---- timing techniques ----------------------------------------------------------------
    asc_for_timing = None
    if dist["w"].get("asc"):
        top_asc, top_p = max(dist["w"]["asc"].items(), key=lambda kv: kv[1])
        asc_for_timing = top_asc if top_p >= 0.6 else None
    natal_sun = ref_w["planets"]["Sun"]["lon"]
    timing = T.compute(b.date, ref_jd, natal_sun, asc_for_timing, b.lat, b.lon, today, houses_ok)

    # ---- birth-time helper: Rising sign across the plausible window ----------------------------
    timeline = []
    if b.time_mode != "exact":
        pts = samples if b.time_mode == "approx" else [(A.to_utc(b.date, h, 0, b.tz), 0) for h in range(24)]
        for utc, _ in pts:
            jd = A.jd_ut(utc)
            ww = A.western(jd, b.lat, b.lon, True)["asc"]["sign"]
            vv = A.vedic(jd, b.lat, b.lon, True)["lagna"]["sign"]
            lt = utc.astimezone(tz).strftime("%H:%M")
            if timeline and timeline[-1]["western"] == ww and timeline[-1]["vedic"] == vv:
                timeline[-1]["to"] = lt
            else:
                timeline.append({"from": lt, "to": lt, "western": ww, "vedic": vv})

    return {
        "meta": {"name": b.name, "date": b.date.isoformat(), "time_mode": b.time_mode,
                 "time": f"{b.hour:02d}:{b.minute:02d}" if b.time_mode != "unknown" else None,
                 "window_min": b.window_min if b.time_mode == "approx" else None,
                 "place": b.place, "lat": b.lat, "lon": b.lon, "tz": b.tz,
                 "ref_utc": ref_utc.isoformat(), "today": today.isoformat(),
                 "houses_known": houses_ok},
        "western": {**ref_w, "aspects": aspects, "elements": elem_counts, "modalities": mod_counts},
        "vedic": {**ref_v, "yogas": yogas, "sade_sati": sade, "ayanamsa_name": "Lahiri (Chitrapaksha)"},
        "numerology": num,
        "dist": dist,
        "dasha": _dasha_out(periods, cur, b, dist, now),
        "bazi": bazi_out,
        "timing": timing,
        "rising_timeline": timeline,
        "notes": notes,
    }


def _dasha_out(periods, cur, b, dist, now):
    def iso(d): return d.date().isoformat()
    timeline = []
    for p in periods:
        if p["end"].year > b.date.year and p["start"].year < b.date.year + 100:
            timeline.append({"lord": p["lord"], "start": iso(p["start"]), "end": iso(p["end"])})
    out = {"timeline": timeline, "current": None}
    if cur:
        out["current"] = {"maha": cur["maha"]["lord"], "maha_start": iso(cur["maha"]["start"]),
                          "maha_end": iso(cur["maha"]["end"]),
                          "antar": cur["antar"]["lord"] if cur["antar"] else None,
                          "antar_start": iso(cur["antar"]["start"]) if cur["antar"] else None,
                          "antar_end": iso(cur["antar"]["end"]) if cur["antar"] else None}
        out["uncertain"] = b.time_mode != "exact"
        if dist.get("dasha") and len(dist["dasha"]) > 1:
            out["alternatives"] = dist["dasha"]
    return out
