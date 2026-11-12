"""Combined analysis. Weaves all four systems, including numerology (Mulank, Bhagyank, Namank, Life Path,
Expression, Soul Urge, Personality), into one 'full picture', adds numerology lines to every section, and builds a
'More insights' section. Mirrors js/enrich.js: keep both identical. Runs before simplify()."""
from __future__ import annotations

from content.extra import HOUSE_NAME, HOUSE_THEME
from content.misc import PAIR_ASPECTS  # noqa: F401  (kept for symmetry with the JS module)
from content.numbers import NUMBERS
from content.numbers_extra import INDIAN_INTRO, MULANK_PLANET, NUMBER_EXTRA, PLANET_THEME, RELATION_TEXT
from content.signs import SIGN_TEXT
from content.traits import TRAITS
from . import compat as C
from . import numerology as N
from . import synthesis as S
from .simplify import first_sentences

X = NUMBER_EXTRA


def _blk(h, text, src, kind="text", items=None, time=False):
    b = {"h": h, "src": src, "time": time, "kind": kind}
    if items is not None:
        b["items"] = items
    else:
        b["text"] = text
    return b


def planet_relation(p1, p2):
    if p1 == p2:
        return "same"
    if p1 not in C.FRIENDS or p2 not in C.FRIENDS:
        return None                       # Rahu / Ketu are not in the planet friendship table
    r1, r2 = C._rel(p1, p2), C._rel(p2, p1)
    if r1 == "enemy" or r2 == "enemy":
        return "enemy"
    return "friend" if (r1 == "friend" and r2 == "friend") else "neutral"


def ucfirst(t):
    return t[:1].upper() + t[1:]


def indian_items(n):
    """Mulank, Bhagyank and Namank as list items, plus how Mulank and Bhagyank relate."""
    items = []
    for key, name in (("mulank", "Mulank"), ("bhagyank", "Bhagyank"), ("namank", "Namank")):
        if key in n:
            num = n[key]["number"]; pl = MULANK_PLANET[num]
            items.append({"label": f"{name} {num} ({pl})", "text": INDIAN_INTRO[key].format(planet=pl, theme=PLANET_THEME[pl]) + f" Strengths: {NUMBERS[num]['strength']}."})
    rel = "same" if n["mulank"]["number"] == n["bhagyank"]["number"] else planet_relation(MULANK_PLANET[n["mulank"]["number"]], MULANK_PLANET[n["bhagyank"]["number"]])
    if rel:
        items.append({"label": "Together", "text": RELATION_TEXT[rel]})
    return items


def enrich(report: dict, prof: dict, synth: dict) -> dict:
    n = prof["numerology"]; snap = report["snapshot"]; today_y = int(prof["meta"]["today"][:4])
    secs = {s["id"]: s for s in report["sections"]}
    py = n.get("pythagorean"); lp = n["life_path"]["number"]
    mul, bha = n["mulank"]["number"], n["bhagyank"]["number"]
    exp = py["expression"] if py else None; soul = py["soul_urge"] if py else None; pers = py["personality"] if py else None
    mpl = MULANK_PLANET[mul]
    NUM_SRC = "Numerology (Mulank, Life Path, Expression, Soul Urge)"

    def ins(sid, block, after=None, before=None):
        bl = secs[sid]["blocks"]
        if after is not None:
            for i, b in enumerate(bl):
                if b["h"].startswith(after):
                    bl.insert(i + 1, block); return
        if before is not None:
            for i, b in enumerate(bl):
                if b["h"].startswith(before):
                    bl.insert(i, block); return
        bl.append(block)

    ch = S.top(synth, "character", 4); car = S.top(synth, "career", 3); rel = S.top(synth, "relationships", 3)
    c0, r0, k0 = ch[0]["trait"], rel[0]["trait"], car[0]["trait"]
    kw = lambda sign: ", ".join(SIGN_TEXT[sign]["kw"])  # noqa: E731

    # ---------- the combined picture (overview) -------------------------------------------------------
    sun, moon = snap["sun_western"]["sign"], snap["moon_western"]["sign"]
    rise = snap["rising_western"]["sign"] if snap["rising_western"] else None
    merged = f"Your Sun in {sun} ({kw(sun)}), Moon in {moon} ({kw(moon)})" + (f", Rising {rise} ({kw(rise)})" if rise else "") + \
             f", Mulank {mul} ({mpl}) and Life Path {lp} come together here."
    pic = [{"label": "Who you are", "text": f"{TRAITS[c0]['tag']} {first_sentences(TRAITS[c0]['strength'])} {merged}"}]
    pic.append({"label": "What you need inside", "text": first_sentences(SIGN_TEXT[moon]["moon"]) +
                (f" Your Soul Urge {soul} adds a need for {X[soul]['soul']}." if soul else "")})
    merc = prof["western"]["planets"]["Mercury"]["sign"]
    pic.append({"label": "How you think and speak", "text": first_sentences(SIGN_TEXT[merc]["mercury"]) +
                (f" With Expression {exp}, {X[exp]['mind']}." if exp else "")})
    pic.append({"label": "Work and purpose", "text": f"{TRAITS[k0]['work']} Your Bhagyank {bha} and Life Path {lp} point toward {NUMBERS[bha]['career']}."})
    pic.append({"label": "Love and closeness", "text": first_sentences(TRAITS[r0]["love"]) +
                (f" In love, Soul Urge {soul} means you need {X[soul]['soul']}." if soul else "")})
    pic.append({"label": "Under pressure", "text": f"{first_sentences(TRAITS[c0]['stress'])} With Mulank {mul}, {X[mul]['stress']}."})
    py_year = n["personal"]["year"]; pr = prof["timing"]["profection"]
    pic.append({"label": "Right now", "text": f"Personal Year {py_year}: {first_sentences(NUMBERS[py_year]['year'])}" +
                (f" Your year's focus is {pr['house_name'].lower()}." if pr else "")})
    secs["overview"]["blocks"].insert(0, _blk("Your full picture", None, ["All four systems combined: Western, Vedic, numerology (including Mulank) and Chinese BaZi"],
                                              kind="list", items=pic))
    # Indian numerology in one place
    secs["overview"]["blocks"].insert(1, _blk("Indian numerology: Mulank, Bhagyank, Namank", None, ["Indian numerology: birth day, birth date and name"],
                                              kind="list", items=indian_items(n)))

    # ---------- numerology in every section ---------------------------------------------------------------
    if exp and exp != lp:
        ins("watchouts", _blk(f"Expression {exp} watch-outs", f"Watch for {NUMBERS[exp]['watch']}.", [f"Expression {exp} · Numerology"]), after=f"Life Path {lp} watch-outs")
    if mul != lp:
        ins("watchouts", _blk(f"Mulank {mul} watch-outs", f"Watch for {NUMBERS[mul]['watch']}.", [f"Mulank {mul} · Numerology"]), after=f"Life Path {lp} watch-outs")
    if soul:
        ins("inner", _blk("What you quietly need", f"Deep down you are looking for {X[soul]['soul']}.", [f"Soul Urge {soul} · Numerology"]), after="What you want underneath it all")
    ins("inner", _blk(f"Mulank {mul}: your emotional core", f"Ruled by {mpl}, Mulank {mul} brings {PLANET_THEME[mpl]}. Its strengths are {NUMBERS[mul]['strength']}; its watch-outs are {NUMBERS[mul]['watch']}.",
                      [f"Mulank {mul} · Indian numerology"]), after="What you need to feel safe")
    if exp:
        ins("mind", _blk(f"How you communicate (Expression {exp})", f"With Expression {exp}, {X[exp]['mind']}.", [f"Expression {exp} · Numerology"]), after="How your mind works")
    if pers:
        ins("mind", _blk(f"First impression (Personality {pers})", f"People often see you as {X[pers]['pers']}.", [f"Personality {pers} · Numerology"]), after="How your mind works")
    e_or_l = exp or lp
    ins("career", _blk("Money and numbers", f"With your numbers, {X[e_or_l]['money']}.", [f"Expression {e_or_l} · Numerology"]), after="What your numbers point to")
    ins("career", _blk(f"Bhagyank {bha}: the path you tend to follow", f"Your Bhagyank {bha} points toward {NUMBERS[bha]['career']}. {ucfirst(NUMBERS[bha]['strength'])}.", [f"Bhagyank {bha} · Indian numerology"]),
        after="What your numbers point to")
    ins("hobbies", _blk("Because of your numbers", f"Mulank {mul} and Life Path {lp} suggest {X[mul]['hobbies']}.", [f"Mulank {mul} · Numerology"]), before="Because of your")
    if soul:
        ins("relationships", _blk("What your numbers say about love", f"With Soul Urge {soul}, what you need most is {X[soul]['soul']}."
            + (f" People first see you as {X[pers]['pers']}." if pers else ""), [f"Soul Urge {soul} · Numerology"]), after=f"Life Path {lp} in love")
    ins("wellbeing", _blk("Under pressure: your numbers", f"With Mulank {mul}, {X[mul]['stress']}.", [f"Mulank {mul} · Numerology"]), after="Under pressure:")
    ins("purpose", _blk(f"Your practice (Life Path {lp})", f"The practice for Life Path {lp}: {X[lp]['growth']}.", [f"Life Path {lp} · Numerology"]))
    cy = n["cycles"]; age = today_y - int(prof["meta"]["date"][:4])
    idx = next((i for i, p in enumerate(cy["pinnacles"]) if age >= p["from"] and (p["to"] is None or age < p["to"])), 3)
    chal = cy["challenges"][idx]
    if chal and chal in X:
        ins("purpose", _blk("Your current challenge number", f"Your current challenge number is {chal} ({NUMBERS[chal]['title']}). The practice: {X[chal]['growth']}.", ["Challenge number · Numerology"]))

    # ---------- more insights ----------------------------------------------------------------------------------
    blocks = []
    outer = (f"People often see you as {X[pers]['pers']}" if pers else f"People first meet your {sun} Sun")
    outer += (f", and your Rising sign {rise} adds {kw(rise)}" if rise else "")
    inner = (f"Inside, you are looking for {X[soul]['soul']}, and your Moon in {moon} feels {kw(moon)}" if soul else f"Inside, your Moon in {moon} feels {kw(moon)}")
    blocks.append(_blk("Outside and inside", f"{outer}. {inner}.", ["Personality, Soul Urge, Rising and Moon"]))
    blocks.append(_blk("Your superpower", first_sentences(TRAITS[c0]["strength"], 2), ["Strongest theme across all four systems"]))
    blocks.append(_blk("Your blind spot", first_sentences(TRAITS[c0]["watch"], 2), ["The shadow side of your strongest theme"]))
    lo = S.lowest(synth, "character", 1)[0]["trait"]
    blocks.append(_blk(f"One thing to build: {TRAITS[lo]['name'].lower()}", TRAITS[lo]["develop"], ["Least-emphasised character trait across systems"]))
    blocks.append(_blk("Friends and family", f"With Life Path {lp}, you are {X[lp]['friends']}.", [f"Life Path {lp} · Numerology"]))
    money = TRAITS[k0]["money"] + f" With your numbers, {X[e_or_l]['money']}."
    blocks.append(_blk("Your money mindset", money, ["Career traits and Expression · Numerology"]))
    m, d = int(prof["meta"]["date"][5:7]), int(prof["meta"]["date"][8:10])
    py2 = N.reduce_num(N.reduce_num(m) + N.reduce_num(d) + N.reduce_num(sum(int(c) for c in str(today_y + 1))), False)
    nxt = f"Personal Year {py2} ({today_y + 1}): {first_sentences(NUMBERS[py2]['year'])}"
    if pr:
        h2 = pr["house"] % 12
        nxt += f" Your year's focus then moves to {HOUSE_NAME[h2].lower()}: {HOUSE_THEME[h2]}."
    blocks.append(_blk("Next year at a glance", nxt, ["Personal Year · Numerology; annual profection · Western"]))
    pm = n["personal"]["month"]
    blocks.append(_blk("Three things to try this month", None, ["Your top traits and Personal Month · Numerology"], kind="list", items=[
        {"label": f"Lean on your {TRAITS[c0]['name'].lower()}", "text": first_sentences(TRAITS[c0]["work"])},
        {"label": f"Practise {TRAITS[lo]['name'].lower()}", "text": TRAITS[lo]["develop"]},
        {"label": "In love", "text": first_sentences(TRAITS[r0]["seek"])},
        {"label": f"This month (Personal Month {pm})", "text": f"The tone is {NUMBERS[pm]['title'].lower()}: {NUMBERS[pm]['strength']}."}]))
    report["sections"].insert(1, {"id": "insights", "title": "More insights", "icon": "spark", "blocks": blocks})
    return report
