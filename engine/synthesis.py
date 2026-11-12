"""Cross-system synthesis.

Each placement or number emits a 'signal': a weighted vote over the shared trait vocabulary for
a set of life domains. Votes from each system are normalised separately, so no system can drown
out the others, then compared. Where systems agree the theme is 'strong'; where they point
different ways, that difference is reported rather than averaged away.
"""
from __future__ import annotations

from content.traits import TRAIT_KEYS
from content.vedic import NAKSHATRA_INFO
from . import astro as A

DOMAINS = ["character", "career", "relationships", "inner", "mind"]
SYSTEMS = ["western", "vedic", "numerology", "bazi"]
PRIOR = 8.0
SUPPORT = 1.4
# numerology counts more because the app owner and many users weight it heavily; change here to rebalance
SYSTEM_WEIGHT = {"western": 1.0, "vedic": 1.0, "numerology": 1.5, "bazi": 1.0}

SIGN_VEC = {
    "Aries": {"initiative": 1.0, "radiance": .3},
    "Taurus": {"steadiness": 1.0, "harmony": .3},
    "Gemini": {"curiosity": 1.0, "precision": .2, "originality": .1},
    "Cancer": {"empathy": 1.0, "steadiness": .3, "imagination": .2},
    "Leo": {"radiance": 1.0, "initiative": .3},
    "Virgo": {"precision": 1.0, "discipline": .3, "introspection": .1},
    "Libra": {"harmony": 1.0, "curiosity": .2},
    "Scorpio": {"intensity": 1.0, "introspection": .5},
    "Sagittarius": {"exploration": 1.0, "curiosity": .3},
    "Capricorn": {"discipline": 1.0, "steadiness": .3, "introspection": .1},
    "Aquarius": {"originality": 1.0, "curiosity": .3},
    "Pisces": {"imagination": 1.0, "empathy": .4, "introspection": .2},
}
NUM_VEC = {
    1: {"initiative": 1.0},
    2: {"harmony": 1.0, "empathy": .4},
    3: {"radiance": .7, "curiosity": .6, "imagination": .3},
    4: {"discipline": .8, "steadiness": .8},
    5: {"exploration": .8, "curiosity": .6},
    6: {"empathy": .7, "harmony": .5, "steadiness": .4},
    7: {"introspection": 1.0, "precision": .4, "imagination": .2},
    8: {"discipline": .6, "intensity": .5, "initiative": .4},
    9: {"imagination": .5, "empathy": .5, "exploration": .4},
    11: {"imagination": .7, "originality": .6, "introspection": .3},
    22: {"discipline": .7, "originality": .5, "steadiness": .4},
    33: {"empathy": .8, "imagination": .5, "harmony": .3},
}

# body -> weight per domain
def _w(character=0, career=0, relationships=0, inner=0, mind=0):
    return {"character": character, "career": career, "relationships": relationships, "inner": inner, "mind": mind}

W_WEIGHTS = {
    "Sun": _w(3, 2, .8, 1, .5), "Moon": _w(3, .6, 2.5, 3, .5), "Asc": _w(2.5, 1, 1, .5, .3),
    "Mercury": _w(1.5, 1.5, .8, .4, 3), "Venus": _w(1.5, .7, 3, .8, .2), "Mars": _w(1.5, 2.2, 1.3, .4, .2),
    "Jupiter": _w(1, 1.4, .5, .3, .3), "Saturn": _w(1, 1.8, .6, .5, .2),
    "Uranus": _w(.4), "Neptune": _w(.4), "Pluto": _w(.4),
    "MC": _w(.8, 3), "Dsc": _w(0, 0, 2.2), "North Node": _w(.6, .4, .3),
}
V_WEIGHTS = {
    "Sun": _w(2.5, 2, .8, 1, .5), "Moon": _w(3.5, .8, 2.5, 3.2, .5), "Lagna": _w(2.5, 1, 1, .5, .3),
    "Mercury": _w(1.5, 1.5, .8, .4, 3), "Venus": _w(1.5, .7, 3, .8, .2), "Mars": _w(1.5, 2.2, 1.3, .4, .2),
    "Jupiter": _w(1.2, 1.4, .6, .3, .3), "Saturn": _w(1.2, 1.8, .6, .5, .2),
    "Rahu": _w(.5, .5, .2), "Ketu": _w(.4, .2, .2, .4),
    "H10": _w(.5, 2.5), "H7": _w(0, 0, 2.2), "Nakshatra": _w(2, 1, 1.5, 2.5, .8),
}
N_WEIGHTS = {
    "life_path": _w(3, 2.5, 1, 1, .5), "expression": _w(2.5, 3, .8, .5, 1.5),
    "soul_urge": _w(1.5, .6, 2.5, 3, .3), "personality": _w(1, .8, 1, .3, .3),
    "birthday": _w(1, .5, .3, .3, .2), "maturity": _w(.7, 1, .3, .3, .2),
    "expression_chaldean": _w(1.2, 1.5, .4, .2, .7),
    # Indian numerology
    "mulank": _w(3, 1.5, 1.5, 2, .5), "bhagyank": _w(2, 2.5, 1, .5, .5), "namank": _w(1.2, 1.5, .5, .2, 1),
}

DM_VEC = {
    "Yang Wood": {"initiative": .6, "discipline": .4, "steadiness": .3},
    "Yin Wood": {"harmony": .6, "curiosity": .3, "empathy": .3},
    "Yang Fire": {"radiance": 1.0, "exploration": .3},
    "Yin Fire": {"empathy": .5, "introspection": .4, "precision": .3},
    "Yang Earth": {"steadiness": 1.0, "discipline": .3},
    "Yin Earth": {"empathy": .5, "precision": .4, "steadiness": .3},
    "Yang Metal": {"initiative": .5, "discipline": .5, "intensity": .3},
    "Yin Metal": {"precision": .6, "harmony": .3, "radiance": .3},
    "Yang Water": {"exploration": .6, "originality": .4, "curiosity": .4},
    "Yin Water": {"imagination": .6, "introspection": .5, "empathy": .3},
}
ANIMAL_VEC = {
    "Rat": {"curiosity": .6, "precision": .3}, "Ox": {"steadiness": .8, "discipline": .5},
    "Tiger": {"initiative": .7, "intensity": .4}, "Rabbit": {"harmony": .7, "empathy": .4},
    "Dragon": {"radiance": .6, "initiative": .4, "originality": .3}, "Snake": {"introspection": .6, "intensity": .5},
    "Horse": {"exploration": .6, "radiance": .4}, "Goat": {"imagination": .6, "empathy": .5},
    "Monkey": {"curiosity": .6, "originality": .5}, "Rooster": {"precision": .7, "radiance": .3},
    "Dog": {"empathy": .4, "discipline": .4, "steadiness": .4}, "Pig": {"empathy": .5, "exploration": .3, "harmony": .3},
}
ELEMENT_VEC = {
    "Wood": {"initiative": .5, "exploration": .4}, "Fire": {"radiance": .6, "initiative": .3},
    "Earth": {"steadiness": .6, "harmony": .3}, "Metal": {"discipline": .5, "precision": .5},
    "Water": {"imagination": .4, "introspection": .4, "curiosity": .3},
}
B_WEIGHTS = {
    "day_master": _w(3, 1.5, 1, 1.5, .5), "year_animal": _w(1.2, .5, 1.5, .5, .3),
    "month_animal": _w(1.5, 2.5, .5, .3, .5), "hour_animal": _w(1, .3, .8, 1.5, .2),
    "element": _w(1.5, .5, .3, .8, .3),
}

ABBR = {"western": "Western", "vedic": "Vedic", "numerology": "Numerology", "bazi": "Chinese BaZi"}


def _sign_signals(system, body, label, dist, weights, tag, needs_time=False, dignity=None):
    out = []
    mult = 1.15 if dignity in ("domicile", "exalted") else 1.0
    for sign, prob in dist.items():
        out.append({"system": system, "body": body, "key": sign, "prob": prob, "vec": SIGN_VEC[sign],
                    "w": {d: v * mult for d, v in weights.items()}, "needs_time": needs_time,
                    "source": f"{label} in {sign}" + (f" ({int(prob*100)}% likely)" if prob < 0.99 else "") + f" · {tag}"})
    return out


def collect_signals(prof: dict) -> list[dict]:
    sig: list[dict] = []
    w, v, n, dist = prof["western"], prof["vedic"], prof["numerology"], prof["dist"]
    for body, p in w["planets"].items():
        if body == "South Node" or body not in W_WEIGHTS:
            continue
        d = dist["w"].get(body.lower()) if body in ("Sun", "Moon") else None
        d = d or {p["sign"]: 1.0}
        sig += _sign_signals("western", body, body, d, W_WEIGHTS[body], "Western", dignity=p.get("dignity"))
    for key, label in (("asc", "Rising"), ("mc", "Midheaven"), ("dsc", "Descendant")):
        d = dist["w"].get(key)
        wkey = {"asc": "Asc", "mc": "MC", "dsc": "Dsc"}[key]
        if d:
            sig += _sign_signals("western", wkey, label, d, W_WEIGHTS[wkey], "Western", needs_time=True)
    for body, p in v["planets"].items():
        if body not in V_WEIGHTS:
            continue
        d = dist["v"].get(body.lower()) if body in ("Sun", "Moon") else None
        d = d or {p["sign"]: 1.0}
        sig += _sign_signals("vedic", body, body, d, V_WEIGHTS[body], "Vedic", dignity=p.get("dignity"))
    lag = dist["v"].get("lagna")
    if lag:
        sig += _sign_signals("vedic", "Lagna", "Lagna", lag, V_WEIGHTS["Lagna"], "Vedic", needs_time=True)
        h10 = {A.SIGNS[(A.SIGNS.index(s) + 9) % 12]: pr for s, pr in lag.items()}
        h7 = {A.SIGNS[(A.SIGNS.index(s) + 6) % 12]: pr for s, pr in lag.items()}
        sig += _sign_signals("vedic", "H10", "10th house", h10, V_WEIGHTS["H10"], "Vedic", needs_time=True)
        sig += _sign_signals("vedic", "H7", "7th house", h7, V_WEIGHTS["H7"], "Vedic", needs_time=True)
    for nk, prob in dist["v"]["nakshatra"].items():
        vec = {t: 1.0 if i == 0 else .7 for i, t in enumerate(NAKSHATRA_INFO[nk][0])}
        sig.append({"system": "vedic", "body": "Nakshatra", "key": nk, "prob": prob, "vec": vec,
                    "w": V_WEIGHTS["Nakshatra"], "needs_time": False,
                    "source": f"Moon in {nk} nakshatra" + (f" ({int(prob*100)}% likely)" if prob < .99 else "") + " · Vedic"})
    # numerology
    def num(key, value, label, weights):
        if value in NUM_VEC:
            sig.append({"system": "numerology", "body": key, "key": value, "prob": 1.0, "vec": NUM_VEC[value],
                        "w": weights, "needs_time": False, "source": f"{label} {value} · Numerology"})
    num("life_path", n["life_path"]["number"], "Life Path", N_WEIGHTS["life_path"])
    num("mulank", n["mulank"]["number"], "Mulank", N_WEIGHTS["mulank"])
    num("bhagyank", n["bhagyank"]["number"], "Bhagyank", N_WEIGHTS["bhagyank"])
    if "namank" in n:
        num("namank", n["namank"]["number"], "Namank", N_WEIGHTS["namank"])
    num("birthday", n["birthday"], "Birthday number", N_WEIGHTS["birthday"])
    if "pythagorean" in n:
        p = n["pythagorean"]
        num("expression", p["expression"], "Expression", N_WEIGHTS["expression"])
        num("soul_urge", p["soul_urge"], "Soul Urge", N_WEIGHTS["soul_urge"])
        num("personality", p["personality"], "Personality", N_WEIGHTS["personality"])
        num("maturity", n["maturity"], "Maturity", N_WEIGHTS["maturity"])
        c = n.get("chaldean")
        if c and c["expression"] != p["expression"]:
            num("expression_chaldean", c["expression"], "Expression (Chaldean)", N_WEIGHTS["expression_chaldean"])
    bz = prof.get("bazi")
    if bz:
        d = bz["dist"]
        for key, label, vec, dd in (("day_master", "Day Master", DM_VEC, d["day_master"]),
                                    ("year_animal", "Year animal", ANIMAL_VEC, d["year_animal"]),
                                    ("month_animal", "Month animal", ANIMAL_VEC, d["month_animal"]),
                                    ("hour_animal", "Hour animal", ANIMAL_VEC, d["hour_animal"])):
            for k, pr in dd.items():
                sig.append({"system": "bazi", "body": key, "key": k, "prob": pr, "vec": vec[k], "w": B_WEIGHTS[key],
                            "needs_time": key == "hour_animal",
                            "source": f"{label}: {k}" + (f" ({int(pr*100)}% likely)" if pr < .99 else "") + " · Chinese BaZi"})
        tot = sum(bz["elements"].values()) or 1
        for el, c in bz["elements"].items():
            if c:
                sig.append({"system": "bazi", "body": "element", "key": el, "prob": c / tot * 5 / 5, "vec": ELEMENT_VEC[el],
                            "w": B_WEIGHTS["element"], "needs_time": False,
                            "source": f"{el} element ({c:g} of {tot:g}) · Chinese BaZi"})
    return sig


import json as _json
from pathlib import Path as _Path

_BASE_FILE = _Path(__file__).with_name("baseline.json")
BASELINE = _json.loads(_BASE_FILE.read_text()) if _BASE_FILE.exists() else {}


def synthesize(prof: dict, calibrate: bool = True) -> dict:
    signals = collect_signals(prof)
    n = len(TRAIT_KEYS)
    idx = {t: i for i, t in enumerate(TRAIT_KEYS)}
    raw = {s: {d: [0.0] * n for d in DOMAINS} for s in SYSTEMS}
    contrib: dict[tuple[str, str], list] = {}
    for sg in signals:
        for d, wt in sg["w"].items():
            if not wt:
                continue
            for t, tv in sg["vec"].items():
                c = wt * sg["prob"] * tv
                raw[sg["system"]][d][idx[t]] += c
                contrib.setdefault((d, t), []).append((c, sg))
    norm = {}
    for s in SYSTEMS:
        norm[s] = {}
        for d in DOMAINS:
            tot = sum(raw[s][d])
            # shrink toward 'average' in proportion to how little evidence the system has, so a
            # sparse system (a handful of numbers) cannot out-shout a full chart
            norm[s][d] = [(x + PRIOR / n) / (tot + PRIOR) * n for x in raw[s][d]]
    if calibrate and BASELINE:
        # Divide by the population-average vote for each trait so that no trait is favoured just
        # because more signs/numbers happen to point at it (see tools/calibrate.py).
        for sy in SYSTEMS:
            for d in DOMAINS:
                norm[sy][d] = [norm[sy][d][i] / BASELINE[sy][d][i] for i in range(n)]
    out = {}
    for d in DOMAINS:
        rows = []
        for t in TRAIT_KEYS:
            i = idx[t]
            per = {s: round(norm[s][d][i], 2) for s in SYSTEMS}
            total_w = sum(SYSTEM_WEIGHT.values())
            score = sum(per[s] * SYSTEM_WEIGHT[s] for s in SYSTEMS) / total_w
            supporters = [s for s in SYSTEMS if per[s] >= SUPPORT]
            ev = sorted(contrib.get((d, t), []), key=lambda x: -x[0])[:4]
            rows.append({"trait": t, "score": round(score, 2), "_raw": score, "per_system": per, "supporters": supporters,
                         "level": ("strong" if len(supporters) >= 3 else "supported" if len(supporters) == 2
                                   else "single" if len(supporters) == 1 else "none"),
                         "evidence": [{"source": sg["source"], "system": sg["system"], "needs_time": sg["needs_time"]}
                                      for _, sg in ev]})
        # rank on the unrounded score; exact ties (common, since per-system values are 2-dp) fall back to
        # trait order, so the result is identical in every implementation
        rows.sort(key=lambda r: (-round(r["_raw"], 6), idx[r["trait"]]))
        out[d] = rows
    return {"domains": out, "signal_count": len(signals), "_norm": norm}


def top(synth: dict, domain: str, k: int = 3, min_score: float = 1.15) -> list[dict]:
    rows = [r for r in synth["domains"][domain][:k] if r["_raw"] >= min_score]
    return rows or synth["domains"][domain][:1]


def lowest(synth: dict, domain: str, k: int = 2) -> list[dict]:
    order = {t: i for i, t in enumerate(TRAIT_KEYS)}
    return sorted(synth["domains"][domain], key=lambda r: (round(r["_raw"], 6), order[r["trait"]]))[:k]


def system_disagreements(synth: dict, domain: str = "character") -> list[dict]:
    """Traits where one system strongly points the other way."""
    res = []
    for r in synth["domains"][domain]:
        ps = r["per_system"]
        hi = max(ps, key=ps.get); lo = min(ps, key=ps.get)
        if ps[hi] >= 1.8 and ps[lo] <= 0.5:
            res.append({"trait": r["trait"], "high": hi, "low": lo, "per_system": ps})
    return sorted(res, key=lambda r: -(r["per_system"][r["high"]] - r["per_system"][r["low"]]))[:3]
