"""Numerology: Pythagorean and Chaldean systems."""
from __future__ import annotations

import datetime as dt
import re
import unicodedata

MASTER = {11, 22, 33}
KARMIC = {13, 14, 16, 19}

PYTH = {c: (i % 9) + 1 for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
CHALDEAN = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                    [1, 2, 3, 4, 5, 8, 3, 5, 1, 1, 2, 3, 4, 5, 7, 8, 1, 2, 3, 4, 6, 6, 6, 5, 1, 7]))
VOWELS = set("AEIOU")


def reduce_num(n: int, keep_master: bool = True) -> int:
    while n > 9 and not (keep_master and n in MASTER):
        n = sum(int(c) for c in str(n))
    return n


def reduction_trail(n: int) -> list[int]:
    """All intermediate values (for karmic debt detection)."""
    trail = [n]
    while n > 9 and n not in MASTER:
        n = sum(int(c) for c in str(n))
        trail.append(n)
    return trail


def clean_name(name: str) -> str:
    n = unicodedata.normalize("NFKD", name)
    n = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z ]", "", n).upper()


def _letters(word: str) -> list[tuple[str, bool]]:
    """(letter, is_vowel) with Y treated as a vowel only when the word has no other vowel
    and W/Y rules kept simple/documented."""
    has_vowel = any(c in VOWELS for c in word)
    out = []
    for i, c in enumerate(word):
        v = c in VOWELS or (c == "Y" and not has_vowel)
        out.append((c, v))
    return out


def name_numbers(name: str, table: dict[str, int]) -> dict:
    tot = vow = con = 0
    counts = {i: 0 for i in range(1, 10)}
    for w in clean_name(name).split():
        for c, is_v in _letters(w):
            v = table[c]
            tot += v
            counts[v] += 1
            if is_v:
                vow += v
            else:
                con += v
    return {"total": tot, "vowels": vow, "consonants": con, "counts": counts}


def _pack(raw: int, keep_master=True) -> dict:
    return {"raw": raw, "number": reduce_num(raw, keep_master),
            "karmic": next((t for t in reduction_trail(raw) if t in KARMIC), None)}


def life_path(d: dt.date) -> dict:
    m, dd, y = reduce_num(d.month), reduce_num(d.day), reduce_num(sum(int(c) for c in str(d.year)))
    raw = m + dd + y
    r = _pack(raw)
    # karmic debt also from unreduced birth-day / sum trail
    kd = r["karmic"] or (d.day if d.day in KARMIC else None)
    return {"number": r["number"], "raw": raw, "karmic": kd, "parts": [m, dd, y]}


def pinnacles(d: dt.date, lp: int) -> dict:
    m, dd, y = reduce_num(d.month), reduce_num(d.day), reduce_num(sum(int(c) for c in str(d.year)))
    base = {11: 2, 22: 4, 33: 6}.get(lp, lp)
    p1, p2 = reduce_num(m + dd), reduce_num(dd + y)
    p3 = reduce_num(p1 + p2)
    p4 = reduce_num(m + y)
    c1, c2 = abs(m - dd), abs(dd - y)
    c3, c4 = abs(c1 - c2), abs(m - y)
    a1 = 36 - base
    return {"pinnacles": [{"n": p1, "from": 0, "to": a1}, {"n": p2, "from": a1, "to": a1 + 9},
                          {"n": p3, "from": a1 + 9, "to": a1 + 18}, {"n": p4, "from": a1 + 18, "to": None}],
            "challenges": [reduce_num(c, False) for c in (c1, c2, c3, c4)]}


def personal_year(d: dt.date, today: dt.date) -> dict:
    py = reduce_num(reduce_num(d.month) + reduce_num(d.day) + reduce_num(sum(int(c) for c in str(today.year))), False)
    pm = reduce_num(py + today.month, False)
    pd = reduce_num(pm + today.day, False)
    return {"year": py, "month": pm, "day": pd}


def compute(birth_name: str, d: dt.date, today: dt.date, current_name: str | None = None) -> dict:
    lp = life_path(d)
    out = {"life_path": lp, "birthday": reduce_num(d.day),
           "birthday_raw": d.day, "personal": personal_year(d, today),
           "cycles": pinnacles(d, lp["number"])}
    for key, table in (("pythagorean", PYTH), ("chaldean", CHALDEAN)):
        if not clean_name(birth_name).strip():
            continue
        nn = name_numbers(birth_name, table)
        exp = _pack(nn["total"])
        out[key] = {"expression": exp["number"], "expression_raw": nn["total"], "karmic": exp["karmic"],
                    "soul_urge": reduce_num(nn["vowels"]), "personality": reduce_num(nn["consonants"]),
                    "counts": nn["counts"]}
    if "pythagorean" in out:
        p = out["pythagorean"]
        mat = reduce_num(lp["number"] + p["expression"], True)
        out["maturity"] = mat
        out["missing"] = [n for n, c in p["counts"].items() if c == 0]
        out["dominant"] = [n for n, c in p["counts"].items() if c == max(p["counts"].values()) and c > 1]
        # Pythagorean sums for karmic detection on soul urge / personality
        nn = name_numbers(birth_name, PYTH)
        out["karmic_debts"] = sorted({k for k in (lp["karmic"], p["karmic"],
                                                   _pack(nn["vowels"])["karmic"],
                                                   _pack(nn["consonants"])["karmic"]) if k})
    else:
        out["karmic_debts"] = [lp["karmic"]] if lp["karmic"] else []
    if current_name and clean_name(current_name).strip() and clean_name(current_name) != clean_name(birth_name):
        nn = name_numbers(current_name, PYTH)
        out["current_name"] = {"expression": reduce_num(nn["total"]), "soul_urge": reduce_num(nn["vowels"]),
                               "personality": reduce_num(nn["consonants"])}
    return out
