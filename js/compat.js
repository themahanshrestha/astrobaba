/* Compatibility: port of engine/compat.py (synastry, Ashtakoota, numerology, BaZi and trait comparison). */
(function (root) {
  "use strict";
  const A = root.AB, D = A.D, C = D.COMPAT, TRAITS = D.TRAITS, SIGNS = A.SIGNS;
  const ELEMENT_FRIEND = new Set(["fire|air", "air|fire", "earth|water", "water|earth"]);
  const sameSet = (a, b, x, y) => (a === x && b === y) || (a === y && b === x);

  function aspectValue(l1, l2, p1, p2) {
    const d = A.angDiff(l1, l2);
    for (const [name, [ang, orb]] of Object.entries(A.ASPECTS)) {
      const lum = p1 === "Sun" || p1 === "Moon" || p2 === "Sun" || p2 === "Moon";
      const o = orb + (lum ? 1 : 0) - ((p1 === "Saturn" || p2 === "Saturn") && name === "conjunction" ? 2 : 0);
      if (Math.abs(d - ang) <= o) {
        const tight = 1 - Math.abs(d - ang) / o; let v = C.VAL[name];
        if (name === "conjunction" && (p1 === "Saturn" || p2 === "Saturn" || p1 === "Mars" || p2 === "Mars")) v = 0.3;
        return [v * (0.5 + 0.5 * tight), name];
      }
    }
    return [0, null];
  }
  const planetLon = (prof, p) => prof.western.planets[p].lon;
  function synastry(a, b) {
    const dims = {}, hits = [];
    for (const [dim, pairs] of Object.entries(C.DIMENSIONS)) {
      let total = 0, wsum = 0;
      for (const [p1, p2, wt] of pairs) {
        let best = null;
        const combos = p1 === p2 ? [[p1, p2]] : [[p1, p2], [p2, p1]];
        for (const [x, y] of combos) {
          const [val, name] = aspectValue(planetLon(a, x), planetLon(b, y), x, y);
          if (name && (best === null || Math.abs(val) > Math.abs(best[0]))) best = [val, name, x, y];
        }
        if (best) { total += best[0] * wt; hits.push({ dim, a: best[2], b: best[3], type: best[1], value: A.pyround(best[0] * wt, 2) }); }
        wsum += wt;
      }
      if (dim === "emotional") {
        const ea = A.ELEMENT[a.western.planets.Moon.sign], eb = A.ELEMENT[b.western.planets.Moon.sign];
        if (ea === eb || ELEMENT_FRIEND.has(ea + "|" + eb)) total += 0.5;
        else if (sameSet(ea, eb, "fire", "water") || sameSet(ea, eb, "earth", "air")) total -= 0.3;
      }
      dims[dim] = A.pyround(Math.max(10, Math.min(95, 52 + 30 * total / Math.max(wsum, 1) * 2.2)));
    }
    return { dimensions: dims, aspects: hits };
  }

  // ---- Ashtakoota --------------------------------------------------------------------------------------
  const YONI_ANIMAL = Object.fromEntries(Object.entries(D.NAKSHATRA_INFO).map(([n, i]) => [n, i[2]]));
  const VARNA = C.VARNA_RANK;
  function rel(p1, p2) { if (p1 === p2) return "same"; const [fr, en] = C.FRIENDS[p1]; return fr.includes(p2) ? "friend" : en.includes(p2) ? "enemy" : "neutral"; }
  function vashyaGroup(si, lon) { const d = lon % 30, g = C.VASHYA[si]; if (g === "human_quad") return d < 15 ? "human" : "quad"; if (g === "quad_water") return d < 15 ? "quad" : "water"; return g; }
  function ashtakoota(a, b) {
    const ma = a.vedic.planets.Moon, mb = b.vedic.planets.Moon, sa = A.signIdx(ma.lon), sb = A.signIdx(mb.lon), na = ma.nak_idx, nb = mb.nak_idx;
    const signA = SIGNS[sa], signB = SIGNS[sb], k = [];
    k.push(["Varna", Math.abs(VARNA[A.ELEMENT[signA]] - VARNA[A.ELEMENT[signB]]) <= 1 ? 1 : 0, 1, "Natural temperament and ego compatibility"]);
    const ga = vashyaGroup(sa, ma.lon), gb = vashyaGroup(sb, mb.lon), set3 = ["human", "quad", "water"];
    k.push(["Vashya", ga === gb ? 2 : (set3.includes(ga) && set3.includes(gb)) ? 1 : 0.5, 2, "Mutual attraction and influence"]);
    const bad = (x, y) => [3, 5, 7].includes((A.mod(y - x, 27) + 1) % 9) ? 1 : 0;
    k.push(["Tara", 3 - 1.5 * (bad(na, nb) + bad(nb, na)), 3, "Fortune and wellbeing together"]);
    const ya = C.YONI_ORDER.indexOf(YONI_ANIMAL[ma.nakshatra]), yb = C.YONI_ORDER.indexOf(YONI_ANIMAL[mb.nakshatra]);
    k.push(["Yoni", C.YONI_M[ya][yb], 4, "Instinctive and physical compatibility"]);
    const la = A.SIGN_LORD[signA], lb = A.SIGN_LORD[signB], r1 = rel(la, lb), r2 = rel(lb, la), pair = new Set([r1, r2]);
    const subset = (set, arr) => [...set].every((x) => arr.includes(x)), eq = (set, arr) => set.size === arr.length && arr.every((x) => set.has(x));
    let gm;
    if (la === lb || subset(pair, ["friend", "same"])) gm = 5;
    else if (eq(pair, ["friend", "neutral"]) || eq(pair, ["friend", "same"])) gm = 4;
    else if (eq(pair, ["neutral"])) gm = 3;
    else if (eq(pair, ["friend", "enemy"])) gm = 1;
    else if (eq(pair, ["neutral", "enemy"])) gm = 0.5;
    else gm = 0;
    k.push(["Graha Maitri", gm, 5, "Mental and intellectual friendship"]);
    const gana1 = D.NAKSHATRA_INFO[ma.nakshatra][1], gana2 = D.NAKSHATRA_INFO[mb.nakshatra][1];
    k.push(["Gana", C.GANA_SCORE[gana1 + "|" + gana2] ?? C.GANA_SCORE[gana2 + "|" + gana1], 6, "Temperament match"]);
    const d = A.mod(sb - sa, 12);
    k.push(["Bhakoot", [1, 11, 4, 8, 5, 7].includes(d) ? 0 : 7, 7, "Emotional and family harmony"]);
    const nadi = (i) => ({ 0: "Adi", 5: "Adi", 1: "Madhya", 4: "Madhya", 2: "Antya", 3: "Antya" })[i % 6];
    k.push(["Nadi", nadi(na) === nadi(nb) ? 0 : 8, 8, "Constitutional and health compatibility"]);
    const total = k.reduce((s, x) => s + x[1], 0);
    return { total, max: 36, kootas: k.map((x) => ({ name: x[0], score: x[1], max: x[2], meaning: x[3] })), moon_a: `${signA} / ${ma.nakshatra}`, moon_b: `${signB} / ${mb.nakshatra}` };
  }

  function numerologyResonance(a, b) {
    const lp = (x) => x.numerology.life_path.number, base = (n) => ({ 11: 2, 22: 4, 33: 6 })[n] || n;
    const groups = [[1, 5, 7], [2, 4, 8], [3, 6, 9]], la = base(lp(a)), lb = base(lp(b));
    const same = groups.some((g) => g.includes(la) && g.includes(lb));
    let score = same ? 70 : 55; if (la === lb) score = 72;
    const notes = [], pa = a.numerology.pythagorean, pb = b.numerology.pythagorean;
    if (pa && pb) {
      if (pa.soul_urge === pb.soul_urge) { score += 8; notes.push("You share a Soul Urge number: similar inner motivations."); }
      if (base(pa.expression) === base(pb.expression)) { score += 4; notes.push("You share an Expression number: a similar way of acting in the world."); }
    }
    if ((la + lb) % 9 === 0 && la !== lb) score += 3;
    score = Math.max(30, Math.min(92, score));
    notes.unshift(`Life Paths ${lp(a)} and ${lp(b)} ` + (same ? "sit in the same natural group, so you tend to see life similarly." : "come from different groups, so you can complement each other but will need to translate between your instincts."));
    return { score, notes };
  }
  function baziResonance(a, b) {
    const ba = a.bazi, bb = b.bazi, ar = A.animalRelation(ba.year.animal, bb.year.animal), er = A.elementRelation(ba.day_master.split(" ")[1], bb.day_master.split(" ")[1]);
    const score = A.pyround(0.5 * C.ANIMAL_SCORE[ar] + 0.5 * C.ELEMENT_SCORE[er]);
    const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
    return { score, notes: [`In Chinese astrology, ${C.ANIMAL_NOTE[ar]} (${ba.year.animal} and ${bb.year.animal}).`, `${cap(C.ELEMENT_NOTE[er])} (${ba.day_master} and ${bb.day_master}).`] };
  }
  function traitCompare(sa, sb, domain = "character") {
    const ra = Object.fromEntries(sa.domains[domain].map((r) => [r.trait, r._raw])), rb = Object.fromEntries(sb.domains[domain].map((r) => [r.trait, r._raw]));
    const keys = Object.keys(ra);
    const shared = keys.filter((t) => ra[t] >= 1.3 && rb[t] >= 1.3).sort((x, y) => (ra[y] + rb[y]) - (ra[x] + rb[x]));
    const compA = keys.filter((t) => ra[t] >= 1.4 && rb[t] <= 0.8).sort((x, y) => (ra[y] - rb[y]) - (ra[x] - rb[x]));
    const compB = Object.keys(rb).filter((t) => rb[t] >= 1.4 && ra[t] <= 0.8).sort((x, y) => (rb[y] - ra[y]) - (rb[x] - ra[x]));
    const friction = [];
    for (const [key, text] of Object.entries(D.TENSIONS)) { const [x, y] = key.split("|");
      if ((ra[x] >= 1.3 && rb[y] >= 1.3) || (ra[y] >= 1.3 && rb[x] >= 1.3)) friction.push({ pair: [x, y], text }); }
    const va = keys.map((t) => ra[t]), vb = keys.map((t) => rb[t]);
    const cos = va.reduce((s, x, i) => s + x * vb[i], 0) / (Math.sqrt(va.reduce((s, x) => s + x * x, 0)) * Math.sqrt(vb.reduce((s, y) => s + y * y, 0)));
    const score = 50 + 22 * (cos - 0.7) / 0.3 * 0.8 + 6 * Math.min(compA.length + compB.length, 3) - 6 * Math.min(friction.length, 3);
    return { score: A.pyround(Math.max(25, Math.min(92, score))), shared: shared.slice(0, 3), a_brings: compA.slice(0, 2), b_brings: compB.slice(0, 2), friction: friction.slice(0, 2) };
  }
  function compare(pa, pb, sa, sb, relation, nameA, nameB) {
    if (!D.RELATION_TYPES[relation]) relation = "romantic";
    const syn = synastry(pa, pb), dims = syn.dimensions, W = C.WEIGHTS[relation];
    const westernScore = A.pyround(Object.keys(dims).reduce((s, d) => s + dims[d] * W[d], 0));
    const ash = ashtakoota(pa, pb), vedicScore = A.pyround(ash.total / 36 * 100), num = numerologyResonance(pa, pb), tc = traitCompare(sa, sb), bz = baziResonance(pa, pb);
    const mw = C.METHOD_WEIGHTS[relation];
    const overall = A.pyround(westernScore * mw.western + vedicScore * mw.vedic + num.score * mw.numerology + bz.score * mw.bazi + tc.score * mw.traits);
    const level = (x) => (x >= 65 ? "high" : x < 45 ? "low" : "mid"), overallLevel = (x) => (x >= 72 ? "high" : x < 52 ? "low" : "mid");
    const dimOut = Object.keys(dims).map((d) => ({ key: d, title: D.DIMENSION_TITLE[d], score: dims[d], text: D.DIMENSION_TEXT[d][level(dims[d])] }));
    const strengths = dimOut.slice().sort((x, y) => y.score - x.score).slice(0, 2);
    const care = dimOut.slice().sort((x, y) => x.score - y.score).slice(0, 2).filter((d) => d.score < 60);
    const fs = [];
    if (Math.abs(westernScore - vedicScore) >= 25) { const [hi, lo] = westernScore > vedicScore ? ["Western", "Vedic"] : ["Vedic", "Western"];
      fs.push(`${hi} indicators are noticeably warmer than ${lo} ones. Treat the ${lo} view as the part of the relationship that needs conscious attention.`); }
    const summary = { high: "A strong overall match, with natural ease in several areas.", mid: "A workable match with real strengths and a few areas that need conscious effort.", low: "A challenging match on paper. It can still work with awareness, but expect to put in deliberate effort." }[overallLevel(overall)];
    return { relation, relation_label: D.RELATION_TYPES[relation], names: [nameA, nameB], overall, summary,
      methods: [{ name: "Western synastry", score: westernScore, how: "Planet-to-planet aspects between both charts, weighted for this type of relationship." },
        { name: "Vedic Guna Milan", score: vedicScore, how: `Ashtakoota ${ash.total}/36 from Moon sign and nakshatra (gender-neutral modern version).` },
        { name: "Numerology resonance", score: num.score, how: "Life Path, Soul Urge and Expression compared." },
        { name: "Chinese BaZi", score: bz.score, how: "Year-animal relationship and Day Master elements." },
        { name: "Trait compatibility", score: tc.score, how: "Overlap, complement and friction between your combined trait profiles." }],
      dimensions: dimOut, strengths, care, ashtakoota: ash, numerology_notes: num.notes, bazi_notes: bz.notes, friction_systems: fs,
      shared: tc.shared.map((t) => ({ key: t, title: TRAITS[t].title, text: TRAITS[t].tag })),
      complement: tc.a_brings.map((t) => ({ who: nameA, key: t, title: TRAITS[t].title, text: TRAITS[t].gives })).concat(tc.b_brings.map((t) => ({ who: nameB, key: t, title: TRAITS[t].title, text: TRAITS[t].gives }))),
      friction: tc.friction, tips: D.RELATION_TIPS[relation], aspects: syn.aspects };
  }
  root.AB.compare = compare;
})(typeof window !== "undefined" ? window : globalThis);
