/* Combined analysis (mirror of engine/enrich.py: keep both identical). */
(function (root) {
  "use strict";
  const A = root.AB, D = A.D, X = D.NUMBER_EXTRA, NUMBERS = D.NUMBERS, TRAITS = D.TRAITS, SIGN_TEXT = D.SIGN_TEXT, C = D.COMPAT;
  const ucfirst = (t) => t.charAt(0).toUpperCase() + t.slice(1);
  const kw = (sign) => SIGN_TEXT[sign].kw.join(", ");
  const blk = (h, text, src, kind = "text", items = null, time = false) => { const b = { h, src, time, kind }; if (items) b.items = items; else b.text = text; return b; };

  function rel1(p1, p2) { if (p1 === p2) return "same"; const [fr, en] = C.FRIENDS[p1]; return fr.includes(p2) ? "friend" : en.includes(p2) ? "enemy" : "neutral"; }
  function planetRelation(p1, p2) {
    if (p1 === p2) return "same";
    if (!C.FRIENDS[p1] || !C.FRIENDS[p2]) return null;
    const r1 = rel1(p1, p2), r2 = rel1(p2, p1);
    if (r1 === "enemy" || r2 === "enemy") return "enemy";
    return r1 === "friend" && r2 === "friend" ? "friend" : "neutral";
  }
  function indianItems(n) {
    const items = [];
    for (const [key, name] of [["mulank", "Mulank"], ["bhagyank", "Bhagyank"], ["namank", "Namank"]]) if (n[key]) {
      const num = n[key].number, pl = D.MULANK_PLANET[num];
      items.push({ label: `${name} ${num} (${pl})`, text: D.INDIAN_INTRO[key].replace("{planet}", pl).replace("{theme}", D.PLANET_THEME[pl]) + ` Strengths: ${NUMBERS[num].strength}.` });
    }
    const m = n.mulank.number, b = n.bhagyank.number;
    const rel = m === b ? "same" : planetRelation(D.MULANK_PLANET[m], D.MULANK_PLANET[b]);
    if (rel) items.push({ label: "Together", text: D.RELATION_TEXT[rel] });
    return items;
  }

  function enrich(report, prof, synth) {
    const n = prof.numerology, snap = report.snapshot, todayY = +prof.meta.today.slice(0, 4), first = root.AB.firstSentences;
    const secs = Object.fromEntries(report.sections.map((s) => [s.id, s])), py = n.pythagorean, lp = n.life_path.number;
    const mul = n.mulank.number, bha = n.bhagyank.number, exp = py ? py.expression : null, soul = py ? py.soul_urge : null, pers = py ? py.personality : null;
    const mpl = D.MULANK_PLANET[mul];
    const ins = (sid, block, after = null, before = null) => {
      const bl = secs[sid].blocks;
      if (after !== null) { const i = bl.findIndex((b) => b.h.startsWith(after)); if (i >= 0) { bl.splice(i + 1, 0, block); return; } }
      if (before !== null) { const i = bl.findIndex((b) => b.h.startsWith(before)); if (i >= 0) { bl.splice(i, 0, block); return; } }
      bl.push(block);
    };
    const ch = A.top(synth, "character", 4), car = A.top(synth, "career", 3), rel = A.top(synth, "relationships", 3);
    const c0 = ch[0].trait, r0 = rel[0].trait, k0 = car[0].trait;

    // combined picture
    const sun = snap.sun_western.sign, moon = snap.moon_western.sign, rise = snap.rising_western ? snap.rising_western.sign : null;
    const merged = `Your Sun in ${sun} (${kw(sun)}), Moon in ${moon} (${kw(moon)})` + (rise ? `, Rising ${rise} (${kw(rise)})` : "") + `, Mulank ${mul} (${mpl}) and Life Path ${lp} come together here.`;
    const pic = [{ label: "Who you are", text: `${TRAITS[c0].tag} ${first(TRAITS[c0].strength)} ${merged}` }];
    pic.push({ label: "What you need inside", text: first(SIGN_TEXT[moon].moon) + (soul ? ` Your Soul Urge ${soul} adds a need for ${X[soul].soul}.` : "") });
    const merc = prof.western.planets.Mercury.sign;
    pic.push({ label: "How you think and speak", text: first(SIGN_TEXT[merc].mercury) + (exp ? ` With Expression ${exp}, ${X[exp].mind}.` : "") });
    pic.push({ label: "Work and purpose", text: `${TRAITS[k0].work} Your Bhagyank ${bha} and Life Path ${lp} point toward ${NUMBERS[bha].career}.` });
    pic.push({ label: "Love and closeness", text: first(TRAITS[r0].love) + (soul ? ` In love, Soul Urge ${soul} means you need ${X[soul].soul}.` : "") });
    pic.push({ label: "Under pressure", text: `${first(TRAITS[c0].stress)} With Mulank ${mul}, ${X[mul].stress}.` });
    const pyYear = n.personal.year, pr = prof.timing.profection;
    pic.push({ label: "Right now", text: `Personal Year ${pyYear}: ${first(NUMBERS[pyYear].year)}` + (pr ? ` Your year's focus is ${pr.house_name.toLowerCase()}.` : "") });
    secs.overview.blocks.unshift(blk("Your full picture", null, ["All four systems combined: Western, Vedic, numerology (including Mulank) and Chinese BaZi"], "list", pic));
    secs.overview.blocks.splice(1, 0, blk("Indian numerology: Mulank, Bhagyank, Namank", null, ["Indian numerology: birth day, birth date and name"], "list", indianItems(n)));

    // numerology in every section
    if (exp && exp !== lp) ins("watchouts", blk(`Expression ${exp} watch-outs`, `Watch for ${NUMBERS[exp].watch}.`, [`Expression ${exp} · Numerology`]), `Life Path ${lp} watch-outs`);
    if (mul !== lp) ins("watchouts", blk(`Mulank ${mul} watch-outs`, `Watch for ${NUMBERS[mul].watch}.`, [`Mulank ${mul} · Numerology`]), `Life Path ${lp} watch-outs`);
    if (soul) ins("inner", blk("What you quietly need", `Deep down you are looking for ${X[soul].soul}.`, [`Soul Urge ${soul} · Numerology`]), "What you want underneath it all");
    ins("inner", blk(`Mulank ${mul}: your emotional core`, `Ruled by ${mpl}, Mulank ${mul} brings ${D.PLANET_THEME[mpl]}. Its strengths are ${NUMBERS[mul].strength}; its watch-outs are ${NUMBERS[mul].watch}.`, [`Mulank ${mul} · Indian numerology`]), "What you need to feel safe");
    if (exp) ins("mind", blk(`How you communicate (Expression ${exp})`, `With Expression ${exp}, ${X[exp].mind}.`, [`Expression ${exp} · Numerology`]), "How your mind works");
    if (pers) ins("mind", blk(`First impression (Personality ${pers})`, `People often see you as ${X[pers].pers}.`, [`Personality ${pers} · Numerology`]), "How your mind works");
    const eOrL = exp || lp;
    ins("career", blk("Money and numbers", `With your numbers, ${X[eOrL].money}.`, [`Expression ${eOrL} · Numerology`]), "What your numbers point to");
    ins("career", blk(`Bhagyank ${bha}: the path you tend to follow`, `Your Bhagyank ${bha} points toward ${NUMBERS[bha].career}. ${ucfirst(NUMBERS[bha].strength)}.`, [`Bhagyank ${bha} · Indian numerology`]), "What your numbers point to");
    ins("hobbies", blk("Because of your numbers", `Mulank ${mul} and Life Path ${lp} suggest ${X[mul].hobbies}.`, [`Mulank ${mul} · Numerology`]), null, "Because of your");
    if (soul) ins("relationships", blk("What your numbers say about love", `With Soul Urge ${soul}, what you need most is ${X[soul].soul}.` + (pers ? ` People first see you as ${X[pers].pers}.` : ""), [`Soul Urge ${soul} · Numerology`]), `Life Path ${lp} in love`);
    ins("wellbeing", blk("Under pressure: your numbers", `With Mulank ${mul}, ${X[mul].stress}.`, [`Mulank ${mul} · Numerology`]), "Under pressure:");
    ins("purpose", blk(`Your practice (Life Path ${lp})`, `The practice for Life Path ${lp}: ${X[lp].growth}.`, [`Life Path ${lp} · Numerology`]));
    const cy = n.cycles, age = todayY - +prof.meta.date.slice(0, 4);
    let idx = cy.pinnacles.findIndex((p) => age >= p.from && (p.to === null || age < p.to)); if (idx < 0) idx = 3;
    const chal = cy.challenges[idx];
    if (chal && X[chal]) ins("purpose", blk("Your current challenge number", `Your current challenge number is ${chal} (${NUMBERS[chal].title}). The practice: ${X[chal].growth}.`, ["Challenge number · Numerology"]));

    // more insights
    const blocks = [];
    let outer = pers ? `People often see you as ${X[pers].pers}` : `People first meet your ${sun} Sun`;
    outer += rise ? `, and your Rising sign ${rise} adds ${kw(rise)}` : "";
    const inner = soul ? `Inside, you are looking for ${X[soul].soul}, and your Moon in ${moon} feels ${kw(moon)}` : `Inside, your Moon in ${moon} feels ${kw(moon)}`;
    blocks.push(blk("Outside and inside", `${outer}. ${inner}.`, ["Personality, Soul Urge, Rising and Moon"]));
    blocks.push(blk("Your superpower", first(TRAITS[c0].strength, 2), ["Strongest theme across all four systems"]));
    blocks.push(blk("Your blind spot", first(TRAITS[c0].watch, 2), ["The shadow side of your strongest theme"]));
    const lo = A.lowest(synth, "character", 1)[0].trait;
    blocks.push(blk(`One thing to build: ${TRAITS[lo].name.toLowerCase()}`, TRAITS[lo].develop, ["Least-emphasised character trait across systems"]));
    blocks.push(blk("Friends and family", `With Life Path ${lp}, you are ${X[lp].friends}.`, [`Life Path ${lp} · Numerology`]));
    blocks.push(blk("Your money mindset", TRAITS[k0].money + ` With your numbers, ${X[eOrL].money}.`, ["Career traits and Expression · Numerology"]));
    const m = +prof.meta.date.slice(5, 7), d = +prof.meta.date.slice(8, 10);
    const py2 = A.reduceNum(A.reduceNum(m) + A.reduceNum(d) + A.reduceNum(String(todayY + 1).split("").reduce((a, c) => a + +c, 0)), false);
    let nxt = `Personal Year ${py2} (${todayY + 1}): ${first(NUMBERS[py2].year)}`;
    if (pr) { const h2 = pr.house % 12; nxt += ` Your year's focus then moves to ${D.EXTRA.HOUSE_NAME[h2].toLowerCase()}: ${D.EXTRA.HOUSE_THEME[h2]}.`; }
    blocks.push(blk("Next year at a glance", nxt, ["Personal Year · Numerology; annual profection · Western"]));
    const pm = n.personal.month;
    blocks.push(blk("Three things to try this month", null, ["Your top traits and Personal Month · Numerology"], "list", [
      { label: `Lean on your ${TRAITS[c0].name.toLowerCase()}`, text: first(TRAITS[c0].work) },
      { label: `Practise ${TRAITS[lo].name.toLowerCase()}`, text: TRAITS[lo].develop },
      { label: "In love", text: first(TRAITS[r0].seek) },
      { label: `This month (Personal Month ${pm})`, text: `The tone is ${NUMBERS[pm].title.toLowerCase()}: ${NUMBERS[pm].strength}.` }]));
    report.sections.splice(1, 0, { id: "insights", title: "More insights", icon: "spark", blocks });
    return report;
  }
  root.AB.enrich = enrich;
})(typeof window !== "undefined" ? window : globalThis);
