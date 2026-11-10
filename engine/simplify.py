"""Makes the report short and plain: adds an 'In short' summary, removes repeated text, keeps only the
most useful blocks per section and moves jargon-heavy detail behind a 'Show more detail' button
(blocks flagged adv=True). Mirrors js/simplify.js: keep both identical."""
from __future__ import annotations

import re

from content.signs import SIGN_TEXT
from content.traits import TRAITS
from content.numbers import NUMBERS

TITLES = {t["title"] for t in TRAITS.values()}

# heading prefixes / substrings that are advanced or jargon-heavy -> hidden until "Show more detail"
ADV_STARTS = ("Your Moon nakshatra", "Sun – Moon", "Moon – Saturn", "Mercury – Mars", "Romance and desire", "Where your luck",
              "Karmic debt", "A light element", "Your slow-burn", "Current life chapter", "Your current Vimshottari",
              "Saturn and your Moon", "Your emotional chapter", "A longer chapter", "Your solar-return", "Your dominant element",
              "Your dominant mode", "Vedic view:", "Missing or weak element", "Your Month animal", "How you pursue goals",
              "Where you spend your energy", "Where growth arrives", "Where you build slowly", "Where you feel at home")
ADV_CONTAINS = (" yoga", " is at home", " is exalted", "works against the grain")


def first_sentences(text: str, n: int = 1) -> str:
    parts = re.findall(r"[^.!?]+[.!?]+(?:\s|$)", text)
    return "".join(parts[:n]).strip() if parts else text


def _keep_first(blocks, pred, n):
    seen, out = 0, []
    for b in blocks:
        if pred(b):
            seen += 1
            if seen > n:
                continue
        out.append(b)
    return out


def simplify(report: dict, prof: dict) -> dict:
    secs = {s["id"]: s for s in report["sections"]}
    snap = report["snapshot"]

    # ---- plain "In short" at the top ------------------------------------------------------------
    def kw(sign): return ", ".join(SIGN_TEXT[sign]["kw"])
    def tag(p): return " (likely)" if p and p < 0.9 else ""
    items = [{"label": f"Sun in {snap['sun_western']['sign']}", "text": kw(snap["sun_western"]["sign"])},
             {"label": f"Moon in {snap['moon_western']['sign']}{tag(snap['moon_western']['prob'])}", "text": kw(snap["moon_western"]["sign"])}]
    if snap["rising_western"]:
        r = snap["rising_western"]
        items.append({"label": f"Rising {r['sign']}{tag(r['prob'])}", "text": kw(r["sign"])})
    lp = snap["life_path"]
    items.append({"label": f"Life Path {lp}", "text": NUMBERS[lp]["title"].lower()})
    secs["overview"]["blocks"].insert(0, {"h": "In short", "src": ["Sun, Moon and Rising (Western) and Life Path (numerology)"], "time": False,
                                          "kind": "list", "items": items})

    for s in report["sections"]:
        sid, blocks = s["id"], s["blocks"]
        if sid == "strengths":
            blocks = _keep_first(blocks, lambda b: b["h"] in TITLES, 3)
        elif sid == "watchouts":
            blocks = _keep_first(blocks, lambda b: b["h"].endswith(": the shadow side"), 3)
            blocks = _keep_first(blocks, lambda b: b["h"] == "An inner tension", 2)
        elif sid == "inner":
            blocks = [b for b in blocks if not b["h"].startswith("How stress shows up")]   # repeated in "Stress & recovery"
        elif sid == "mind":
            blocks = _keep_first(blocks, lambda b: b["h"].startswith("Mental style:"), 1)
        elif sid == "career":
            blocks = _keep_first(blocks, lambda b: b["h"].endswith(" at work"), 2)
        elif sid == "relationships":
            blocks = _keep_first(blocks, lambda b: b["h"].startswith("Your love style:"), 1)
            for b in blocks:
                if b["h"] == "What to look for in a partner":
                    b["items"] = b["items"][:2]
        elif sid == "wellbeing":
            blocks = _keep_first(blocks, lambda b: b["h"].startswith("Under pressure:"), 2)
        elif sid == "purpose":
            blocks = [b for b in blocks if not b["h"].endswith("your central lesson")]      # already in "Your core self"
        elif sid == "hobbies":
            pick = [b for b in blocks if b["h"].startswith(("Moon (what restores", "Venus (what you enjoy", "Because of your"))]
            because = [b for b in pick if b["h"].startswith("Because of your")][:2]
            base = [b for b in pick if not b["h"].startswith("Because of your")]
            labels = {"Moon (what restores you)": "To recharge", "Venus (what you enjoy)": "What you enjoy"}
            its = [{"label": labels[b["h"]], "text": b["text"]} for b in base] + \
                  [{"label": b["h"].replace("Because of your", "Your").strip(), "text": b["text"]} for b in because]
            srcs = []
            for b in pick[:4]:
                srcs += b["src"]
            blocks = [{"h": "Things you may enjoy", "src": srcs, "time": False, "kind": "list", "items": its}]
        elif sid == "timing":
            jup = next((b for b in blocks if b["h"] == "Jupiter now"), None)
            sat = next((b for b in blocks if b["h"] == "Saturn now"), None)
            if jup and sat:
                merged = {"h": "Jupiter and Saturn right now", "src": jup["src"] + sat["src"], "time": jup["time"] or sat["time"], "kind": "text",
                          "text": first_sentences(jup["text"]) + " " + first_sentences(sat["text"])}
                blocks = [b for b in blocks if b["h"] not in ("Jupiter now", "Saturn now")] + [merged]
        # shorten Vedic views: show only the key qualities, the full reading follows the Western sign
        for b in blocks:
            if b["kind"] == "views":
                b["items"] = [({"label": i["label"], "text": "Key qualities: " + kw(i["label"].split("·")[1].split("(")[0].strip()) + "."}
                               if i["label"].startswith("Vedic") else i) for i in b["items"]]
        for b in blocks:
            if b["h"].startswith(ADV_STARTS) or any(c in b["h"] for c in ADV_CONTAINS):
                b["adv"] = True
        s["blocks"] = blocks
    # life areas: show the first four planets, rest is detail
    return report
