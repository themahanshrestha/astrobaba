"""Compatibility between two profiles: Western synastry, Vedic Ashtakoota (Guna Milan),
numerology resonance and a trait-level comparison. Scores are transparent heuristics: each
output lists what produced it. Relationship type shifts which factors matter most."""
from __future__ import annotations

from content.misc import (DIMENSION_TEXT, DIMENSION_TITLE, RELATION_TIPS, RELATION_TYPES)
from content.traits import TRAITS
from content.vedic import NAKSHATRA_INFO
from . import astro as A
from . import synthesis as S

# aspect value for a pair type (harmonious +, tense -, conjunction depends on bodies)
VAL = {"trine": 1.0, "sextile": 0.7, "conjunction": 0.8, "square": -0.6, "opposition": -0.2}

DIMENSIONS = {
    "emotional": [("Moon", "Moon", 1.0), ("Sun", "Moon", 1.0), ("Moon", "Venus", 0.8), ("Moon", "Saturn", 0.4)],
    "communication": [("Mercury", "Mercury", 1.0), ("Mercury", "Moon", 0.7), ("Mercury", "Sun", 0.7), ("Mercury", "Venus", 0.5)],
    "values": [("Venus", "Venus", 1.0), ("Venus", "Sun", 0.7), ("Venus", "Moon", 0.7), ("Venus", "Jupiter", 0.5)],
    "drive": [("Mars", "Mars", 0.8), ("Sun", "Mars", 0.9), ("Venus", "Mars", 1.0), ("Sun", "Sun", 0.8)],
    "stability": [("Saturn", "Sun", 0.9), ("Saturn", "Moon", 0.9), ("Saturn", "Venus", 0.7), ("Jupiter", "Sun", 0.7), ("Jupiter", "Moon", 0.7)],
}
WEIGHTS = {
    "romantic": {"emotional": .25, "communication": .15, "values": .25, "drive": .15, "stability": .20},
    "business": {"emotional": .05, "communication": .30, "values": .10, "drive": .25, "stability": .30},
    "family": {"emotional": .35, "communication": .20, "values": .15, "drive": .05, "stability": .25},
    "friends": {"emotional": .20, "communication": .30, "values": .25, "drive": .15, "stability": .10},
}
METHOD_WEIGHTS = {
    "romantic": {"western": .30, "vedic": .30, "numerology": .08, "bazi": .12, "traits": .20},
    "business": {"western": .30, "vedic": .18, "numerology": .12, "bazi": .10, "traits": .30},
    "family": {"western": .27, "vedic": .27, "numerology": .08, "bazi": .10, "traits": .28},
    "friends": {"western": .30, "vedic": .22, "numerology": .08, "bazi": .10, "traits": .30},
}
ANIMAL_SCORE = {"harmony": 92, "trine": 84, "same": 66, "neutral": 60, "clash": 34}
ANIMAL_NOTE = {"harmony": "your year animals form a classic 'secret friend' pairing",
               "trine": "your year animals belong to the same trine of allies",
               "same": "you share the same year animal",
               "neutral": "your year animals have no special pairing",
               "clash": "your year animals sit opposite each other, which tradition reads as friction"}
ELEMENT_SCORE = {"supportive": 82, "same": 72, "neutral": 62, "controlling": 48}
ELEMENT_NOTE = {"supportive": "your Day Master elements nourish each other", "same": "your Day Masters share an element",
                "neutral": "your Day Master elements are neutral to each other", "controlling": "one Day Master element controls the other, which can feel like pressure"}


def bazi_resonance(a: dict, b: dict) -> dict:
    from . import bazi as BZ
    ba, bb = a["bazi"], b["bazi"]
    ar = BZ.animal_relation(ba["year"]["animal"], bb["year"]["animal"])
    er = BZ.element_relation(ba["day_master"].split()[1], bb["day_master"].split()[1])
    score = round(0.5 * ANIMAL_SCORE[ar] + 0.5 * ELEMENT_SCORE[er])
    return {"score": score, "notes": [f"In Chinese astrology, {ANIMAL_NOTE[ar]} ({ba['year']['animal']} and {bb['year']['animal']}).",
                                      f"{ELEMENT_NOTE[er].capitalize()} ({ba['day_master']} and {bb['day_master']})."]}
ELEMENT_FRIEND = {("fire", "air"), ("air", "fire"), ("earth", "water"), ("water", "earth")}


def _angle(a, b):
    return A.angular_diff(a, b)


def _aspect_value(l1, l2, p1, p2):
    d = _angle(l1, l2)
    for name, (ang, orb) in A.ASPECTS.items():
        lum = p1 in ("Sun", "Moon") or p2 in ("Sun", "Moon")
        o = orb + (1 if lum else 0) - (2 if ("Saturn" == p1 or "Saturn" == p2) and name == "conjunction" else 0)
        if abs(d - ang) <= o:
            tight = 1 - abs(d - ang) / o
            v = VAL[name]
            if name == "conjunction" and ("Saturn" in (p1, p2) or "Mars" in (p1, p2)):
                v = 0.3
            return v * (0.5 + 0.5 * tight), name
    return 0.0, None


def _planet_lon(prof, p):
    return prof["western"]["planets"][p]["lon"]


def synastry(a: dict, b: dict) -> dict:
    dims, hits = {}, []
    for dim, pairs in DIMENSIONS.items():
        total = wsum = 0.0
        for p1, p2, wt in pairs:
            best = None
            for x, y in {(p1, p2), (p2, p1)}:
                val, name = _aspect_value(_planet_lon(a, x), _planet_lon(b, y), x, y)
                if name and (best is None or abs(val) > abs(best[0])):
                    best = (val, name, x, y)
            if best:
                total += best[0] * wt
                hits.append({"dim": dim, "a": best[2], "b": best[3], "type": best[1], "value": round(best[0] * wt, 2)})
            wsum += wt
        # element bonus for lights on emotional dimension
        if dim == "emotional":
            ea = A.ELEMENT[a["western"]["planets"]["Moon"]["sign"]]; eb = A.ELEMENT[b["western"]["planets"]["Moon"]["sign"]]
            if ea == eb or (ea, eb) in ELEMENT_FRIEND:
                total += 0.5
            elif {ea, eb} in ({"fire", "water"}, {"earth", "air"}):
                total -= 0.3
        dims[dim] = round(max(10, min(95, 52 + 30 * total / max(wsum, 1) * 2.2)))
    return {"dimensions": dims, "aspects": hits}


# ----- Ashtakoota -----------------------------------------------------------------
YONI_ANIMAL = {n: info[2] for n, info in NAKSHATRA_INFO.items()}
YONI_ORDER = ["Horse", "Elephant", "Sheep", "Serpent", "Dog", "Cat", "Rat", "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"]
YONI_M = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4],
]
GANA_SCORE = {("Deva", "Deva"): 6, ("Manushya", "Manushya"): 6, ("Rakshasa", "Rakshasa"): 6,
              ("Deva", "Manushya"): 5, ("Deva", "Rakshasa"): 1, ("Manushya", "Rakshasa"): 0}
FRIENDS = {
    "Sun": ({"Moon", "Mars", "Jupiter"}, {"Venus", "Saturn"}),
    "Moon": ({"Sun", "Mercury"}, set()),
    "Mars": ({"Sun", "Moon", "Jupiter"}, {"Mercury"}),
    "Mercury": ({"Sun", "Venus"}, {"Moon"}),
    "Jupiter": ({"Sun", "Moon", "Mars"}, {"Mercury", "Venus"}),
    "Venus": ({"Mercury", "Saturn"}, {"Sun", "Moon"}),
    "Saturn": ({"Mercury", "Venus"}, {"Sun", "Moon", "Mars"}),
}
VARNA_RANK = {"water": 3, "fire": 2, "earth": 1, "air": 0}   # Brahmin, Kshatriya, Vaishya, Shudra
VASHYA = {0: "quad", 1: "quad", 2: "human", 3: "water", 4: "wild", 5: "human", 6: "human", 7: "scorpion",
          8: "human_quad", 9: "quad_water", 10: "human", 11: "water"}


def _rel(p1, p2):
    if p1 == p2:
        return "same"
    fr, en = FRIENDS[p1]
    return "friend" if p2 in fr else "enemy" if p2 in en else "neutral"


def _vashya_group(sign_idx, lon):
    d = lon % 30
    g = VASHYA[sign_idx]
    if g == "human_quad":
        return "human" if d < 15 else "quad"
    if g == "quad_water":
        return "quad" if d < 15 else "water"
    return g


def ashtakoota(a: dict, b: dict) -> dict:
    ma, mb = a["vedic"]["planets"]["Moon"], b["vedic"]["planets"]["Moon"]
    sa, sb = A.sign_idx(ma["lon"]), A.sign_idx(mb["lon"])
    na, nb = ma["nak_idx"], mb["nak_idx"]
    sign_a, sign_b = A.SIGNS[sa], A.SIGNS[sb]
    kootas = []
    # Varna (1)
    ra, rb = VARNA_RANK[A.ELEMENT[sign_a]], VARNA_RANK[A.ELEMENT[sign_b]]
    varna = 1 if abs(ra - rb) <= 1 else 0
    kootas.append(("Varna", varna, 1, "Natural temperament and ego compatibility"))
    # Vashya (2)
    ga, gb = _vashya_group(sa, ma["lon"]), _vashya_group(sb, mb["lon"])
    vashya = 2 if ga == gb else 1 if {ga, gb} <= {"human", "quad", "water"} else 0.5
    kootas.append(("Vashya", vashya, 2, "Mutual attraction and influence"))
    # Tara (3)
    def bad(x, y):
        return (((y - x) % 27) + 1) % 9 in (3, 5, 7)
    tara = 3 - 1.5 * (bad(na, nb) + bad(nb, na))
    kootas.append(("Tara", tara, 3, "Fortune and wellbeing together"))
    # Yoni (4)
    ya, yb = YONI_ORDER.index(YONI_ANIMAL[a["vedic"]["planets"]["Moon"]["nakshatra"]]), YONI_ORDER.index(YONI_ANIMAL[b["vedic"]["planets"]["Moon"]["nakshatra"]])
    yoni = YONI_M[ya][yb]
    kootas.append(("Yoni", yoni, 4, "Instinctive and physical compatibility"))
    # Graha Maitri (5)
    la, lb = A.SIGN_LORD[sign_a], A.SIGN_LORD[sign_b]
    r1, r2 = _rel(la, lb), _rel(lb, la)
    pair = {r1, r2}
    if la == lb or pair <= {"friend", "same"}:
        gm = 5
    elif pair == {"friend", "neutral"} or pair == {"friend", "same"}:
        gm = 4
    elif pair == {"neutral"}:
        gm = 3
    elif pair == {"friend", "enemy"}:
        gm = 1
    elif pair == {"neutral", "enemy"}:
        gm = 0.5
    else:
        gm = 0
    kootas.append(("Graha Maitri", gm, 5, "Mental and intellectual friendship"))
    # Gana (6)
    gana_a, gana_b = NAKSHATRA_INFO[ma["nakshatra"]][1], NAKSHATRA_INFO[mb["nakshatra"]][1]
    gana = GANA_SCORE.get((gana_a, gana_b), GANA_SCORE.get((gana_b, gana_a)))
    kootas.append(("Gana", gana, 6, "Temperament match"))
    # Bhakoot (7)
    d = (sb - sa) % 12
    bhakoot = 0 if d in (1, 11, 4, 8, 5, 7) else 7
    kootas.append(("Bhakoot", bhakoot, 7, "Emotional and family harmony"))
    # Nadi (8)
    def nadi(i): return {0: "Adi", 5: "Adi", 1: "Madhya", 4: "Madhya", 2: "Antya", 3: "Antya"}[i % 6]
    nad = 0 if nadi(na) == nadi(nb) else 8
    kootas.append(("Nadi", nad, 8, "Constitutional and health compatibility"))
    total = sum(k[1] for k in kootas)
    return {"total": total, "max": 36, "kootas": [{"name": k[0], "score": k[1], "max": k[2], "meaning": k[3]} for k in kootas],
            "moon_a": f"{sign_a} / {ma['nakshatra']}", "moon_b": f"{sign_b} / {mb['nakshatra']}"}


# ----- numerology ------------------------------------------------------------------------
def numerology_resonance(a: dict, b: dict) -> dict:
    def lp(x): return x["numerology"]["life_path"]["number"]
    def base(n): return {11: 2, 22: 4, 33: 6}.get(n, n)
    groups = [{1, 5, 7}, {2, 4, 8}, {3, 6, 9}]
    la, lb = base(lp(a)), base(lp(b))
    same_group = any(la in g and lb in g for g in groups)
    score = 70 if same_group else 55
    if la == lb:
        score = 72
    # soul urge / expression closeness
    notes = []
    pa, pb = a["numerology"].get("pythagorean"), b["numerology"].get("pythagorean")
    if pa and pb:
        if pa["soul_urge"] == pb["soul_urge"]:
            score += 8; notes.append("You share a Soul Urge number: similar inner motivations.")
        if base(pa["expression"]) == base(pb["expression"]):
            score += 4; notes.append("You share an Expression number: a similar way of acting in the world.")
    if (la + lb) % 9 == 0 and la != lb:
        score += 3
    score = max(30, min(92, score))
    notes.insert(0, f"Life Paths {lp(a)} and {lp(b)} " + ("sit in the same natural group, so you tend to see life similarly." if same_group else "come from different groups, so you can complement each other but will need to translate between your instincts."))
    return {"score": score, "notes": notes}


# ----- traits ---------------------------------------------------------------------------------
def trait_compare(sa: dict, sb: dict, domain: str = "character") -> dict:
    ra = {r["trait"]: r["score"] for r in sa["domains"][domain]}
    rb = {r["trait"]: r["score"] for r in sb["domains"][domain]}
    shared = sorted([t for t in ra if ra[t] >= 1.3 and rb[t] >= 1.3], key=lambda t: -(ra[t] + rb[t]))
    comp_a = sorted([t for t in ra if ra[t] >= 1.4 and rb[t] <= 0.8], key=lambda t: -(ra[t] - rb[t]))
    comp_b = sorted([t for t in rb if rb[t] >= 1.4 and ra[t] <= 0.8], key=lambda t: -(rb[t] - ra[t]))
    from content.traits import TENSIONS
    friction = []
    for (x, y), text in TENSIONS.items():
        if (ra[x] >= 1.3 and rb[y] >= 1.3) or (ra[y] >= 1.3 and rb[x] >= 1.3):
            friction.append({"pair": [x, y], "text": text})
    # similarity score
    import math
    va = [ra[t] for t in ra]; vb = [rb[t] for t in ra]
    cos = sum(x * y for x, y in zip(va, vb)) / (math.sqrt(sum(x * x for x in va)) * math.sqrt(sum(y * y for y in vb)))
    score = 50 + 22 * (cos - 0.7) / 0.3 * 0.8 + 6 * min(len(comp_a) + len(comp_b), 3) - 6 * min(len(friction), 3)
    return {"score": round(max(25, min(92, score))), "shared": shared[:3], "a_brings": comp_a[:2], "b_brings": comp_b[:2], "friction": friction[:2]}


def compare(pa: dict, pb: dict, sa: dict, sb: dict, relation: str, name_a: str, name_b: str) -> dict:
    relation = relation if relation in RELATION_TYPES else "romantic"
    syn = synastry(pa, pb)
    dims = syn["dimensions"]
    western_score = round(sum(dims[d] * WEIGHTS[relation][d] for d in dims))
    ash = ashtakoota(pa, pb)
    vedic_score = round(ash["total"] / 36 * 100)
    num = numerology_resonance(pa, pb)
    tc = trait_compare(sa, sb)
    bz = bazi_resonance(pa, pb)
    mw = METHOD_WEIGHTS[relation]
    overall = round(western_score * mw["western"] + vedic_score * mw["vedic"] + num["score"] * mw["numerology"]
                    + bz["score"] * mw["bazi"] + tc["score"] * mw["traits"])
    def level(x): return "high" if x >= 65 else "low" if x < 45 else "mid"
    def overall_level(x): return "high" if x >= 72 else "low" if x < 52 else "mid"
    dim_out = [{"key": d, "title": DIMENSION_TITLE[d], "score": dims[d], "text": DIMENSION_TEXT[d][level(dims[d])]} for d in dims]
    strengths = [d for d in sorted(dim_out, key=lambda x: -x["score"])[:2]]
    care = [d for d in sorted(dim_out, key=lambda x: x["score"])[:2] if d["score"] < 60]
    friction_sys = []
    if abs(western_score - vedic_score) >= 25:
        hi, lo = ("Western", "Vedic") if western_score > vedic_score else ("Vedic", "Western")
        friction_sys.append(f"{hi} indicators are noticeably warmer than {lo} ones. Treat the {lo} view as the part of the relationship that needs conscious attention.")
    summary = {
        "high": "A strong overall match, with natural ease in several areas.",
        "mid": "A workable match with real strengths and a few areas that need conscious effort.",
        "low": "A challenging match on paper. It can still work with awareness, but expect to put in deliberate effort.",
    }[overall_level(overall)]
    return {
        "relation": relation, "relation_label": RELATION_TYPES[relation], "names": [name_a, name_b],
        "overall": overall, "summary": summary,
        "methods": [{"name": "Western synastry", "score": western_score, "how": "Planet-to-planet aspects between both charts, weighted for this type of relationship."},
                    {"name": "Vedic Guna Milan", "score": vedic_score, "how": f"Ashtakoota {ash['total']:g}/36 from Moon sign and nakshatra (gender-neutral modern version)."},
                    {"name": "Numerology resonance", "score": num["score"], "how": "Life Path, Soul Urge and Expression compared."},
                    {"name": "Chinese BaZi", "score": bz["score"], "how": "Year-animal relationship and Day Master elements."},
                    {"name": "Trait compatibility", "score": tc["score"], "how": "Overlap, complement and friction between your combined trait profiles."}],
        "dimensions": dim_out, "strengths": strengths, "care": care,
        "ashtakoota": ash, "numerology_notes": num["notes"], "bazi_notes": bz["notes"], "friction_systems": friction_sys,
        "shared": [{"key": t, "title": TRAITS[t]["title"], "text": TRAITS[t]["tag"]} for t in tc["shared"]],
        "complement": ([{"who": name_a, "key": t, "title": TRAITS[t]["title"], "text": TRAITS[t]["gives"]} for t in tc["a_brings"]] +
                       [{"who": name_b, "key": t, "title": TRAITS[t]["title"], "text": TRAITS[t]["gives"]} for t in tc["b_brings"]]),
        "friction": tc["friction"], "tips": RELATION_TIPS[relation],
        "aspects": syn["aspects"],
    }
