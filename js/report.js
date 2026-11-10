/* Report builder: port of engine/report.py. Every sentence comes from the curated content library. */
(function (root) {
  "use strict";
  const A = root.AB, D = A.D, X = D.EXTRA, SIGNS = A.SIGNS, S = A;
  const SIGN_TEXT = D.SIGN_TEXT, TRAITS = D.TRAITS, NUMBERS = D.NUMBERS;
  const ROLE = { Sun: "sense of self and vitality", Moon: "emotional life", Mercury: "thinking and communication", Venus: "way of loving and valuing",
    Mars: "drive and way of acting", Jupiter: "growth and judgement", Saturn: "discipline and responsibility" };
  const SYS_NAME = { western: "Western", vedic: "Vedic", numerology: "Numerology", bazi: "BaZi" };
  const lc1 = (s) => s.charAt(0).toLowerCase() + s.slice(1);
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
  const fmt = (tpl, o) => tpl.replace(/\{(\w+)\}/g, (_, k) => o[k]);
  const pct = (p) => Math.floor(p * 100);

  function levelLabel(r) {
    const n = r.supporters.length, names = r.supporters.map((x) => SYS_NAME[x]).join(", ");
    if (n >= 3) return `Strong theme · ${n} of 4 systems agree (${names})`;
    if (n === 2) return `Supported · ${names} agree`;
    if (n === 1) return `Emphasised by ${names}`;
    return "";
  }
  function opts(d, minP = 0.2) { const it = Object.entries(d).filter(([, v]) => v >= minP); return it.length ? it : Object.entries(d).slice(0, 1); }
  function block(h, o = {}) {
    const b = { h, src: o.src || [], time: o.time || false, kind: o.kind || "text" };
    if (o.text !== undefined) b.text = o.text;
    if (o.items !== undefined) b.items = o.items;
    return b;
  }
  function signView(h, field, wDist, vDist, wLabel, vLabel, time = false) {
    const ws = opts(wDist), vs = opts(vDist);
    if (ws.length === 1 && vs.length === 1 && ws[0][0] === vs[0][0]) {
      const s = ws[0][0];
      return block(h, { text: SIGN_TEXT[s][field], time, src: [`${wLabel} in ${s} · Western`, `${vLabel} in ${s} · Vedic`, "Both traditions agree on this placement"] });
    }
    const items = [];
    for (const [s, p] of ws) items.push({ label: `Western · ${s}` + (p < 0.95 ? ` (${pct(p)}% likely)` : ""), text: SIGN_TEXT[s][field] });
    for (const [s, p] of vs) items.push({ label: `Vedic · ${s}` + (p < 0.95 ? ` (${pct(p)}% likely)` : ""), text: SIGN_TEXT[s][field] });
    return block(h, { items, kind: "views", time, src: [`${wLabel} · Western (tropical)`, `${vLabel} · Vedic (sidereal, Lahiri)`] });
  }
  function planetDists(prof, planet) {
    const k = planet.toLowerCase(), w = prof.dist.w[k], v = prof.dist.v[k];
    return [w && Object.keys(w).length ? w : { [prof.western.planets[planet].sign]: 1 }, v && Object.keys(v).length ? v : { [prof.vedic.planets[planet].sign]: 1 }];
  }
  const traitChip = (r) => { const t = TRAITS[r.trait]; return { key: r.trait, name: t.title, tag: t.tag, level: r.level, level_label: levelLabel(r), score: r.score, per_system: r.per_system }; };
  const traitBlock = (r, field, heading) => block(heading || TRAITS[r.trait].title, { text: TRAITS[r.trait][field], src: r.evidence.map((e) => e.source), time: r.evidence.some((e) => e.needs_time) });
  const asp = (prof, a, b) => prof.western.aspects.find((x) => (x.a === a && x.b === b) || (x.a === b && x.b === a)) || null;
  const best = (d) => { const es = Object.entries(d || {}); if (!es.length) return [null, 0]; return es.reduce((m, e) => (e[1] > m[1] ? e : m)); };
  const maxKey = (o) => Object.keys(o).reduce((m, k) => (o[k] > o[m] ? k : m));
  const minKey = (o) => Object.keys(o).reduce((m, k) => (o[k] < o[m] ? k : m));

  function buildReport(prof, synth) {
    const n = prof.numerology, w = prof.western, v = prof.vedic, dist = prof.dist, sections = [];
    const today = A.dateOf(prof.meta.today), hasTime = Object.keys(dist.w.asc || {}).length > 0;
    const ch = A.top(synth, "character", 4), car = A.top(synth, "career", 3), rel = A.top(synth, "relationships", 3), inn = A.top(synth, "inner", 2), mnd = A.top(synth, "mind", 2);

    const [sunW, sunWp] = best(dist.w.sun), [moonW, moonWp] = best(dist.w.moon), [ascW, ascWp] = best(dist.w.asc);
    const [sunV] = best(dist.v.sun), [moonV] = best(dist.v.moon), [lag, lagP] = best(dist.v.lagna), [nak, nakP] = best(dist.v.nakshatra);
    const py = n.pythagorean || {};
    const snap = { sun_western: { sign: sunW, prob: sunWp }, moon_western: { sign: moonW, prob: moonWp }, rising_western: ascW ? { sign: ascW, prob: ascWp } : null,
      sun_vedic: { sign: sunV }, moon_vedic: { sign: moonV, nakshatra: nak, pada: v.planets.Moon.pada, prob: nakP }, lagna_vedic: lag ? { sign: lag, prob: lagP } : null,
      life_path: n.life_path.number, expression: py.expression ?? null, soul_urge: py.soul_urge ?? null, personality: py.personality ?? null,
      birthday: n.birthday, maturity: n.maturity ?? null, north_node: w.planets["North Node"].sign };

    // overview
    let blocks = [block("Your defining themes", { items: ch.slice(0, 3).map(traitChip), kind: "traits", src: ["Weighted combination of Western, Vedic, numerology and Chinese BaZi (see 'Where your systems agree')"] })];
    blocks.push(signView("Your core self (Sun)", "sun", ...planetDists(prof, "Sun"), "Sun", "Sun"));
    const lp = n.life_path.number;
    blocks.push(block("Your life path", { src: [`Life Path ${lp} · Numerology`], text: fmt(D.CATEGORY_INTRO.life_path, { n: lp, core: NUMBERS[lp].core }) }));
    if (ascW) blocks.push(signView("How others meet you (Rising)", "rising", dist.w.asc, dist.v.lagna, "Rising sign", "Lagna", true));
    else blocks.push(block("How others meet you (Rising)", { kind: "locked", text: "Your Rising sign and Lagna need a birth time. Add an exact or approximate time and this section unlocks." }));
    const agree = synth.domains.character.filter((r) => r.level === "strong").slice(0, 3);
    if (agree.length) blocks.push(block("Where most systems agree", { src: ["Cross-system comparison"],
      text: `At least three of the four systems (Western, Vedic, numerology, Chinese BaZi) independently emphasise: ${agree.map((r) => TRAITS[r.trait].title.replace("The ", "")).join(", ")}. Treat these as the most reliable themes in your profile.` }));
    sections.push({ id: "overview", title: "Your core self", icon: "sun", blocks });

    // strengths
    blocks = ch.map((r) => traitBlock(r, "strength"));
    const pk = Object.entries(w.planets).filter(([p, d]) => ROLE[p] && (d.dignity === "domicile" || d.dignity === "exalted")).slice(0, 3);
    for (const [p, d] of pk) { const word = d.dignity === "domicile" ? "at home" : "exalted";
      blocks.push(block(`${p} is ${word}`, { src: [`${p} in ${d.sign} · Western`], text: `${p} in ${d.sign} is ${word}: your ${ROLE[p]} works with unusual ease and confidence.` })); }
    for (const y of v.yogas.slice(0, 3)) blocks.push(block(`${y} yoga`, { text: D.YOGAS[y], src: [`${y} yoga · Vedic`] }));
    const jw = w.planets.Jupiter.sign, jv = v.planets.Jupiter.sign;
    blocks.push(block("Where your luck tends to grow", { src: [`Jupiter in ${jw} · Western`, `Jupiter in ${jv} · Vedic`],
      text: `With Jupiter in ${jw} (Western)${jw === jv ? "" : ` and ${jv} (Vedic)`}, you tend to find ${X.JUPITER_SIGN[jw]}` + (jw === jv ? "." : `; the Vedic view adds ${X.JUPITER_SIGN[jv]}.`) }));
    const numS = [[`Life Path`, n.life_path.number], [`Expression`, py.expression]].filter(([, val]) => val).map(([label, val]) => `${label} ${val}: ${NUMBERS[val].strength}`);
    if (numS.length) blocks.push(block("Your numbers add", { text: numS.join("; ") + ".", src: ["Numerology"] }));
    sections.push({ id: "strengths", title: "Your strengths", icon: "star", blocks });

    // watch-outs
    blocks = ch.map((r) => traitBlock(r, "watch", `${TRAITS[r.trait].title}: the shadow side`));
    const strong = new Set(synth.domains.character.filter((r) => r._raw >= 1.15).map((r) => r.trait));
    for (const [key, text] of Object.entries(D.TENSIONS)) { const [a, b] = key.split("|");
      if (strong.has(a) && strong.has(b)) blocks.push(block("An inner tension", { text, src: [`${TRAITS[a].title} and ${TRAITS[b].title} both prominent`] })); }
    for (const [p, d] of Object.entries(w.planets)) if (ROLE[p] && (d.dignity === "detriment" || d.dignity === "fall")) {
      blocks.push(block(`${p} works against the grain`, { text: `${p} in ${d.sign} is in a challenging sign: your ${ROLE[p]} takes conscious effort and often becomes a place of growth.`, src: [`${p} in ${d.sign} · Western`] })); break; }
    for (const x of w.aspects) if (((x.a === "Sun" && x.b === "Moon") || (x.a === "Moon" && x.b === "Sun")) && (x.type === "square" || x.type === "opposition"))
      blocks.push(block("Head vs heart", { text: D.PAIR_ASPECTS["Sun|Moon"][x.type], src: [`Sun ${x.type} Moon · Western`] }));
    if (n.karmic_debts.length) blocks.push(block("Karmic debt numbers", { text: n.karmic_debts.map((k) => D.KARMIC_DEBT[k]).join(" "), src: [`Karmic debt ${n.karmic_debts.join(", ")} · Numerology`] }));
    const ex = w.elements, totE = Object.values(ex).reduce((a, b) => a + b, 0), lowE = minKey(ex);
    if (ex[lowE] / totE < 0.1) blocks.push(block(`A light element: ${lowE}`, { text: D.ELEMENT_TEXT[lowE].low, src: ["Element balance · Western"] }));
    blocks.push(block(`Life Path ${lp} watch-outs`, { text: `Watch for ${NUMBERS[lp].watch}.`, src: ["Numerology"] }));
    sections.push({ id: "watchouts", title: "What to be wary of", icon: "shield", blocks });

    // inner world
    blocks = [signView("What you need to feel safe (Moon)", "moon", ...planetDists(prof, "Moon"), "Moon", "Moon")];
    const ninfo = D.NAKSHATRA_INFO[nak];
    blocks.push(block(`Your Moon nakshatra: ${nak}`, { text: `${ninfo[3]} (Pada ${v.planets.Moon.pada}, ${ninfo[1]} temperament, ${ninfo[2]} yoni).`, src: [`Moon in ${nak} · Vedic`] }));
    if (n.pythagorean) { const su = py.soul_urge;
      blocks.push(block("What you want underneath it all", { src: [`Soul Urge ${su} · Numerology`], text: fmt(D.CATEGORY_INTRO.soul_urge, { n: su, core: NUMBERS[su].core }) })); }
    for (const pair of [["Sun", "Moon"], ["Moon", "Saturn"]]) { const x = asp(prof, ...pair);
      if (x) blocks.push(block(`${pair[0]} – ${pair[1]}`, { text: D.PAIR_ASPECTS[pair.join("|")][x.type], src: [`${pair[0]} ${x.type} ${pair[1]} · Western`] })); }
    for (const r of inn) blocks.push(block(`How stress shows up: ${TRAITS[r.trait].title}`, { text: TRAITS[r.trait].stress, src: r.evidence.map((e) => e.source) }));
    sections.push({ id: "inner", title: "Inner world & emotions", icon: "moon", blocks });

    // mind
    blocks = [signView("How your mind works (Mercury)", "mercury", ...planetDists(prof, "Mercury"), "Mercury", "Mercury")];
    let x = asp(prof, "Mercury", "Mars");
    if (x) blocks.push(block("Mercury – Mars", { text: D.PAIR_ASPECTS["Mercury|Mars"][x.type], src: [`Mercury ${x.type} Mars · Western`] }));
    for (const r of mnd) blocks.push(block(`Mental style: ${TRAITS[r.trait].title}`, { text: TRAITS[r.trait].tag + " " + TRAITS[r.trait].strength, src: r.evidence.map((e) => e.source) }));
    for (const r of A.lowest(synth, "mind", 1)) blocks.push(block(`To round out your thinking: ${TRAITS[r.trait].name.toLowerCase()}`, { text: TRAITS[r.trait].develop, src: ["Least-emphasised mental trait across systems"] }));
    sections.push({ id: "mind", title: "Mind & communication", icon: "mind", blocks });

    // career
    blocks = [block("Your professional signature", { items: car.map(traitChip), kind: "traits", src: ["Career-weighted view: Midheaven/10th house, Sun, Mars, Saturn, Mercury, Life Path, Expression"] })];
    for (const r of car) { const t = TRAITS[r.trait];
      blocks.push(block(`${t.title} at work`, { text: `${t.work} Environments that fit: ${lc1(t.career)}`, src: r.evidence.map((e) => e.source), time: r.evidence.some((e) => e.needs_time) })); }
    if (hasTime) {
      const h10 = {}; for (const [s, p] of Object.entries(dist.v.lagna || {})) h10[SIGNS[(SIGNS.indexOf(s) + 9) % 12]] = p;
      blocks.push(signView("Your public calling (Midheaven / 10th house)", "career", dist.w.mc, h10, "Midheaven", "10th house", true));
    } else blocks.push(block("Your public calling", { kind: "locked", text: "The Midheaven and 10th house need a birth time. Add one to unlock a sharper career read." }));
    blocks.push(signView("How you pursue goals (Mars)", "mars", ...planetDists(prof, "Mars"), "Mars", "Mars"));
    const nums = [`Life Path ${lp} (${NUMBERS[lp].title}): ${NUMBERS[lp].career}`];
    if (n.pythagorean) nums.push(`Expression ${py.expression} (${NUMBERS[py.expression].title}): ${NUMBERS[py.expression].career}`);
    blocks.push(block("What your numbers point to", { items: nums.map((t) => ({ label: "", text: t })), kind: "list", src: ["Numerology"] }));
    blocks.push(block("Money temperament", { text: car.slice(0, 2).map((r) => TRAITS[r.trait].money).join(" "), src: car[0].evidence.map((e) => e.source) }));
    const lo = A.lowest(synth, "career", 1)[0], lt = TRAITS[lo.trait];
    blocks.push(block("Where you'll have to work harder", { src: ["Least-emphasised career trait"],
      text: `Roles that lean heavily on ${lt.name.toLowerCase()} (${lt.career.split(",")[0]}, for example) are less natural for you. If your job demands it: ${lt.develop}` }));
    sections.push({ id: "career", title: "Career & purpose", icon: "briefcase", blocks });

    // hobbies
    blocks = [];
    const venW = w.planets.Venus.sign, venV = v.planets.Venus.sign, marsW = w.planets.Mars.sign;
    for (const [label, sign, tag] of [["Moon (what restores you)", best(dist.w.moon)[0], "Moon · Western"], ["Venus (what you enjoy)", venW, "Venus · Western"], ["Mars (how you like to move)", marsW, "Mars · Western"]])
      blocks.push(block(label, { text: SIGN_TEXT[sign].hobbies, src: [`${tag} in ${sign}`] }));
    if (venV !== venW) blocks.push(block("Venus, Vedic view", { text: SIGN_TEXT[venV].hobbies, src: [`Venus in ${venV} · Vedic`] }));
    for (const r of ch.slice(0, 3)) blocks.push(block(`Because of your ${TRAITS[r.trait].name.toLowerCase()}`, { text: TRAITS[r.trait].hobbies, src: r.evidence.map((e) => e.source) }));
    sections.push({ id: "hobbies", title: "Hobbies & recharging", icon: "palette", blocks });

    // relationships
    blocks = [block("Your relationship signature", { items: rel.map(traitChip), kind: "traits", src: ["Relationship-weighted view: Venus, Moon, Descendant/7th house, Soul Urge"] })];
    blocks.push(signView("How you love (Venus)", "venus", ...planetDists(prof, "Venus"), "Venus", "Venus"));
    for (const r of rel.slice(0, 2)) blocks.push(block(`Your love style: ${TRAITS[r.trait].title}`, { text: TRAITS[r.trait].love, src: r.evidence.map((e) => e.source) }));
    x = asp(prof, "Venus", "Mars");
    if (x) blocks.push(block("Romance and desire (Venus – Mars)", { text: D.PAIR_ASPECTS["Venus|Mars"][x.type], src: [`Venus ${x.type} Mars · Western`] }));
    if (hasTime) { const h7 = {}; for (const [s, p] of Object.entries(dist.v.lagna)) h7[SIGNS[(SIGNS.indexOf(s) + 6) % 12]] = p;
      blocks.push(signView("Who you tend to be drawn to", "partner", dist.w.dsc, h7, "Descendant", "7th house", true)); }
    blocks.push(block("What to look for in a partner", { items: rel.map((r) => ({ label: TRAITS[r.trait].title, text: TRAITS[r.trait].seek })), kind: "list", src: ["Derived from your relationship traits across all four systems"] }));
    blocks.push(block("Someone who complements you", { kind: "list", src: ["Your least-emphasised relationship traits"],
      items: A.lowest(synth, "relationships", 2).map((r) => ({ label: TRAITS[r.trait].name, text: `A partner naturally strong in ${TRAITS[r.trait].name.toLowerCase()} brings ${TRAITS[r.trait].gives}. This is the quality that fills a gap in you without competing with you.` })) }));
    blocks.push(block("Patterns to be wary of", { items: rel.slice(0, 2).map((r) => ({ label: TRAITS[r.trait].title, text: TRAITS[r.trait].avoid })), kind: "list", src: ["Derived from your relationship traits"] }));
    blocks.push(block(`Life Path ${lp} in love`, { text: NUMBERS[lp].love, src: [`Life Path ${lp} · Numerology`] }));
    sections.push({ id: "relationships", title: "Love & relationships", icon: "heart", blocks });

    // wellbeing
    blocks = ch.slice(0, 3).map((r) => block(`Under pressure: ${TRAITS[r.trait].title}`, { text: TRAITS[r.trait].stress, src: r.evidence.map((e) => e.source) }));
    const domE = maxKey(ex);
    blocks.push(block(`Your dominant element: ${domE}`, { text: D.ELEMENT_TEXT[domE].dom, src: ["Element balance · Western"] }));
    const domM = maxKey(w.modalities);
    blocks.push(block(`Your dominant mode: ${domM}`, { text: D.MODALITY_TEXT[domM].dom, src: ["Modality balance · Western"] }));
    blocks.push(block("A note", { text: "These are lifestyle and temperament patterns, not medical information. For health concerns, speak with a qualified professional.", kind: "note" }));
    sections.push({ id: "wellbeing", title: "Stress & recovery", icon: "leaf", blocks });

    // purpose
    const nn = w.planets["North Node"].sign;
    blocks = [block(`Your growth direction (North Node in ${nn})`, { text: SIGN_TEXT[nn].node, src: [`North Node in ${nn} · Western`] })];
    const sw = w.planets.Saturn.sign, sv = v.planets.Saturn.sign;
    blocks.push(block("Your slow-burn lessons (Saturn)", { src: [`Saturn in ${sw} · Western`, `Saturn in ${sv} · Vedic`],
      text: `Saturn in ${sw} (Western)${sw === sv ? "" : ` and ${sv} (Vedic)`} points to ${X.SATURN_SIGN[sw]}` + (sw === sv ? "." : `; the Vedic view adds ${X.SATURN_SIGN[sv]}.`) + " These are not punishments: they are where patience becomes mastery." }));
    blocks.push(block(`Life Path ${lp}: your central lesson`, { text: `${NUMBERS[lp].title}: ${NUMBERS[lp].core}`, src: ["Numerology"] }));
    if (n.maturity) blocks.push(block("What emerges later in life", { text: fmt(D.CATEGORY_INTRO.maturity, { n: n.maturity, core: NUMBERS[n.maturity].core }), src: [`Maturity ${n.maturity} · Numerology`] }));
    for (const r of A.lowest(synth, "character", 2)) blocks.push(block(`A growth edge: ${TRAITS[r.trait].name.toLowerCase()}`, { text: TRAITS[r.trait].develop, src: ["Least-emphasised character trait across systems"] }));
    const cy = n.cycles.pinnacles, age = today.y - A.dateOf(prof.meta.date).y;
    const cur = cy.find((p) => age >= p.from && (p.to === null || age < p.to)) || cy[cy.length - 1];
    blocks.push(block(`Current life chapter (pinnacle ${cur.n})`, { src: ["Pinnacle cycle · Numerology"], text: `Ages ${cur.from}–${cur.to || "onward"}: ${NUMBERS[cur.n].title}, centred on ${NUMBERS[cur.n].core}` }));
    sections.push({ id: "purpose", title: "Growth & life lessons", icon: "compass", blocks });

    // timing
    const d = prof.dasha; blocks = [];
    if (d.current) { const c = d.current;
      let txt = `${D.MAHA_TEXT[c.maha]} You are in ${c.maha} period until ${c.maha_end}.`;
      if (c.antar) txt += ` Within it, ${c.antar} sub-period (${D.ANTAR_FLAVOR[c.antar]}) runs from ${c.antar_start} to ${c.antar_end}.`;
      if (d.uncertain) txt += " Because your birth time is not exact, dates may shift.";
      blocks.push(block("Your current Vimshottari period", { text: txt, src: [`Vimshottari dasha from Moon in ${nak} · Vedic`], time: !!d.uncertain })); }
    const pyr = n.personal.year;
    blocks.push(block(`Personal Year ${pyr} (${today.y})`, { text: NUMBERS[pyr].year, src: ["Personal Year · Numerology"] }));
    const pm = n.personal.month;
    blocks.push(block(`This month: Personal Month ${pm}`, { text: `${NUMBERS[pm].title}: ${NUMBERS[pm].core}`, src: ["Personal Month · Numerology"] }));
    if (v.sade_sati) blocks.push(block("Saturn and your Moon (Sade Sati)", { text: D.SADE_SATI[v.sade_sati], src: ["Saturn transit · Vedic"] }));
    const tm = prof.timing, pr = tm.profection;
    if (pr) blocks.push(block(`Your year at a glance: ${A.ordinal(pr.house)}-house profection (age ${pr.age})`, { time: true,
      text: `Hellenistic astrology activates one house per year of life. This year's focus is ${pr.house_name.toLowerCase()}: ${pr.house_theme}. The ruler of the year is ${X.YEAR_LORD[pr.lord]}`,
      src: [`Annual profection from ${pr.sign} Rising · Western (Hellenistic)`] }));
    const pmoon = tm.progressed.moon_sign;
    blocks.push(block(`Your emotional chapter: progressed Moon in ${pmoon}`, { src: [`Secondary progression · Moon in ${pmoon} · Western`],
      text: `Your progressed Moon changes sign about every two and a half years and sets the emotional tone of the current chapter. In ${pmoon}: ` + SIGN_TEXT[pmoon].moon }));
    if (tm.progressed.sun_sign !== snap.sun_western.sign) { const ps = tm.progressed.sun_sign;
      blocks.push(block(`A longer chapter: progressed Sun in ${ps}`, { src: [`Secondary progression · Sun in ${ps} · Western`],
        text: `Your progressed Sun has moved into ${ps}, a roughly thirty-year chapter that adds the qualities of ${SIGN_TEXT[ps].kw.join(", ")} to your sense of self.` })); }
    const sr = tm.solar_return;
    blocks.push(block("Your solar-return year", { src: ["Solar return · Western"], time: !!sr.asc_sign,
      text: `Your most recent solar return was on ${sr.date}. Its Moon was in ${sr.moon_sign}, colouring the emotional tone of the year with ${SIGN_TEXT[sr.moon_sign].kw.join(", ")} qualities.`
        + (sr.asc_sign ? ` Its Rising sign was ${sr.asc_sign}: the year asks you to meet life with ${SIGN_TEXT[sr.asc_sign].kw.join(", ")} energy.` : "") }));
    for (const planet of ["Jupiter", "Saturn"]) { const t = tm.transits[planet];
      const base = `${planet} is currently in ${t.sign}${t.retro ? " (retrograde)" : ""}`; let text;
      if (t.house) text = `${base}, moving through your ${A.ordinal(t.house)} house (${X.HOUSE_NAME[t.house - 1].toLowerCase()}): ${X.HOUSE_THEME[t.house - 1]}. ` + (planet === "Jupiter" ? "A period of growth and opportunity in that area." : "A period of responsibility and steady building in that area.");
      else text = base + ". Add a birth time to see which area of life this touches.";
      blocks.push(block(`${planet} now`, { text, src: [`Transit of ${planet} · Western`], time: !!t.house })); }
    sections.push({ id: "timing", title: "Your current season", icon: "clock", blocks });

    // life areas
    blocks = [];
    if (prof.meta.time_mode === "exact") {
      for (const [planet, [heading, lead]] of Object.entries(X.PLANET_HOUSE_LEAD)) { const h = w.planets[planet].house;
        blocks.push(block(`${heading}: ${planet} in your ${A.ordinal(h)} house`, { src: [`${planet} in house ${h} · Western (Placidus)`], text: `${cap(lead)}. This house covers ${X.HOUSE_THEME[h - 1]}.` })); }
      const lg = v.lagna.sign;
      for (const pl of ["Moon", "Venus"]) { const h = v.planets[pl].house;
        blocks.push(block(`Vedic view: ${pl} in the ${A.ordinal(h)} house`, { src: [`${pl} in house ${h} from ${lg} Lagna · Vedic (whole sign)`], text: `From your ${lg} Lagna, the ${pl} sits in the ${A.ordinal(h)} house, which covers ${X.HOUSE_THEME[h - 1]}.` })); }
    } else blocks.push(block("Life areas need an exact birth time", { kind: "locked", text: "Which house each planet lives in depends on your exact birth time. With an exact time, this section shows where you shine, feel at home, find love, spend energy, grow and build." }));
    sections.splice(sections.findIndex((s) => s.id === "wellbeing"), 0, { id: "houses", title: "Life areas", icon: "home", blocks });

    // BaZi
    const bz = prof.bazi, dm = bz.day_master, pnames = { year: "Year", month: "Month", day: "Day", hour: "Hour" };
    const pillars = ["year", "month", "day", "hour"].filter((k) => bz[k]).map((k) => Object.assign({ name: pnames[k] }, bz[k]));
    blocks = [block("Your Four Pillars", { kind: "pillars", items: pillars, src: ["Chinese BaZi: year changes at Lichun, month by solar term, day by the 60-day cycle, hour by two-hour branch"] })];
    if (!bz.hour) blocks.push(block("The Hour pillar", { kind: "locked", text: "The Hour pillar needs an exact birth time. The three other pillars are shown." }));
    const [dmt, dmx] = X.DAY_MASTER[dm];
    blocks.push(block(`Your Day Master: ${dm} · ${dmt}`, { text: dmx, src: ["Day pillar stem · Chinese BaZi"] }));
    const ya = bz.year.animal, ma = bz.month.animal;
    blocks.push(block(`Your Year animal: ${ya}`, { text: X.ANIMAL_TEXT[ya] + " (How others often see you, and your family or social background.)", src: ["Year pillar branch · Chinese BaZi"] }));
    blocks.push(block(`Your Month animal: ${ma}`, { text: X.ANIMAL_TEXT[ma] + " (Often linked with career style.)", src: ["Month pillar branch · Chinese BaZi"] }));
    const el = bz.elements, totB = Object.values(el).reduce((a, b) => a + b, 0), domB = maxKey(el), lowB = minKey(el);
    blocks.push(block(`Dominant element: ${domB}`, { text: X.ELEMENT_BALANCE[domB].dom, src: ["Element count across pillars · Chinese BaZi"] }));
    if (el[lowB] === 0 || el[lowB] / totB < 0.08) blocks.push(block(`Missing or weak element: ${lowB}`, { text: X.ELEMENT_BALANCE[lowB].low, src: ["Element count across pillars · Chinese BaZi"] }));
    blocks.push(block("About this reading", { kind: "note", text: "This is a simplified Four Pillars reading (main stems and branches; hidden stems and luck pillars are not used). The hour pillar uses clock time and the day changes at 11pm." }));
    sections.push({ id: "bazi", title: "Chinese Four Pillars", icon: "yin", blocks });

    return { snapshot: snap, sections, disclaimer: D.DISCLAIMER };
  }
  root.AB.buildReport = buildReport; root.AB.levelLabel = levelLabel;
})(typeof window !== "undefined" ? window : globalThis);
