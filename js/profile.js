/* Profile building (exact / approximate / unknown birth time) and cross-system synthesis. */
(function (root) {
  "use strict";
  const A = root.AB, D = A.D, E = A.E, SIGNS = A.SIGNS, S = D.SYN;

  function dist(values) {   // [[key, weight]] -> {key: prob} sorted by prob desc (stable), rounded to 3 dp
    const c = new Map();
    for (const [k, w] of values) c.set(k, (c.get(k) || 0) + w);
    const tot = [...c.values()].reduce((a, b) => a + b, 0);
    return Object.fromEntries([...c.entries()].sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, A.pyround(v / tot, 3)]));
  }
  const percent = (v) => Math.floor(v * 100);

  function samples(b) {
    const c = A.dateOf(b.date);
    if (b.time_mode === "exact") return [{ utc: A.toUtc(c, b.hour, b.minute, b.tz), w: 1 }];
    if (b.time_mode === "approx") {
      const w = Math.max(5, Math.min(b.window_min, 720)), centre = b.hour * 60 + b.minute, step = Math.max(5, Math.floor(w / 12));
      const out = [];
      for (let o = -w; o <= w; o += step) {
        const t = centre + o, day = A.addDaysYMD(c, Math.floor(t / 1440)), tt = A.mod(t, 1440);
        out.push(A.toUtc(day, Math.floor(tt / 60), tt % 60, b.tz));
      }
      return out.map((u) => ({ utc: u, w: 1 / out.length }));
    }
    return Array.from({ length: 24 }, (_, h) => ({ utc: A.toUtc(c, h, 0, b.tz), w: 1 / 24 }));
  }
  const best = (o) => Object.entries(o).sort((a, b) => b[1] - a[1])[0];

  function build(b, today) {
    const c = A.dateOf(b.date), sm = samples(b), unknown = b.time_mode === "unknown";
    const hasTime = b.time_mode === "exact" || b.time_mode === "approx", housesOk = b.time_mode === "exact";
    const refUtc = A.toUtc(c, unknown ? 12 : b.hour, unknown ? 0 : b.minute, b.tz), refJd = E.jdUT(refUtc);
    const refW = A.western(refUtc, b.lat, b.lon, housesOk), refV = A.vedic(refUtc, b.lat, b.lon, housesOk);

    const dist_ = { w: {}, v: {}, dasha: null };
    if (b.time_mode !== "exact") {
      const wl = [], vl = [], riseW = [], riseV = [], mcW = [], dscW = [], nak = [], lords = [];
      for (const { utc, w } of sm) {
        const ww = A.western(utc, b.lat, b.lon, hasTime), vv = A.vedic(utc, b.lat, b.lon, hasTime);
        wl.push([ww.planets.Moon.sign, w]); vl.push([vv.planets.Moon.sign, w]); nak.push([vv.planets.Moon.nakshatra, w]);
        if (hasTime) { riseW.push([ww.asc.sign, w]); mcW.push([ww.mc.sign, w]); dscW.push([ww.dsc.sign, w]); riseV.push([vv.lagna.sign, w]); }
        const per = A.vimshottari(vv.planets.Moon.lon, utc.getTime());
        const cd = A.currentDasha(per, Date.UTC(today.y, today.m - 1, today.d, 12));
        if (cd) lords.push([cd.maha.lord, w]);
      }
      dist_.w = { moon: dist(wl), asc: hasTime ? dist(riseW) : {}, mc: hasTime ? dist(mcW) : {}, dsc: hasTime ? dist(dscW) : {} };
      dist_.v = { moon: dist(vl), lagna: hasTime ? dist(riseV) : {}, nakshatra: dist(nak) };
      dist_.dasha = dist(lords);
    } else {
      dist_.w = { moon: { [refW.planets.Moon.sign]: 1 }, asc: { [refW.asc.sign]: 1 }, mc: { [refW.mc.sign]: 1 }, dsc: { [refW.dsc.sign]: 1 } };
      dist_.v = { moon: { [refV.planets.Moon.sign]: 1 }, lagna: { [refV.lagna.sign]: 1 }, nakshatra: { [refV.planets.Moon.nakshatra]: 1 } };
    }
    const sunW = dist(sm.map(({ utc, w }) => [A.signOf(E.tropLon("Sun", utc)), w]));
    const sunV = dist(sm.map(({ utc, w }) => [A.signOf(A.norm(E.tropLon("Sun", utc) - E.ayanamsa(E.jdUT(utc)))), w]));
    dist_.w.sun = sunW; dist_.v.sun = sunV;

    const moonV = refV.planets.Moon, periods = A.vimshottari(moonV.lon, refUtc.getTime());
    const nowMs = Date.UTC(today.y, today.m - 1, today.d, 12), cur = A.currentDasha(periods, nowMs);

    const aspects = A.findAspects(Object.assign({}, ...Object.entries(refW.planets).map(([k, p]) => ({ [k]: p.lon })),
      housesOk ? { Asc: refW.asc.lon, MC: refW.mc.lon } : {}), new Set(["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Asc", "MC"]));
    const elem = { fire: 0, earth: 0, air: 0, water: 0 }, modal = { cardinal: 0, fixed: 0, mutable: 0 };
    const wts = { Sun: 3, Moon: 3, Mercury: 2, Venus: 2, Mars: 2, Jupiter: 1.5, Saturn: 1.5, Uranus: 0.5, Neptune: 0.5, Pluto: 0.5 };
    for (const [p, w] of Object.entries(wts)) { const s = refW.planets[p].sign; elem[A.ELEMENT[s]] += w; modal[A.MODALITY[s]] += w; }
    if (housesOk) { const s = refW.asc.sign; elem[A.ELEMENT[s]] += 3; modal[A.MODALITY[s]] += 3; }

    const yogas = [], vp = refV.planets, ms = A.signIdx(vp.Moon.lon);
    if ([0, 3, 6, 9].includes(A.mod(A.signIdx(vp.Jupiter.lon) - ms, 12))) yogas.push("Gaja Kesari");
    if (vp.Sun.sign === vp.Mercury.sign) yogas.push("Budha-Aditya");
    if (vp.Moon.sign === vp.Mars.sign) yogas.push("Chandra-Mangala");
    if (housesOk) {
      const li = SIGNS.indexOf(refV.lagna.sign);
      for (const [planet, name] of [["Mars", "Ruchaka"], ["Mercury", "Bhadra"], ["Jupiter", "Hamsa"], ["Venus", "Malavya"], ["Saturn", "Shasha"]]) {
        const p = vp[planet];
        if ((p.dignity === "domicile" || p.dignity === "exalted") && [0, 3, 6, 9].includes(A.mod(A.signIdx(p.lon) - li, 12))) yogas.push(name);
      }
    }
    const ss = A.sadeSati(ms, new Date(nowMs));
    const sade = (b.time_mode === "exact" || Math.max(...Object.values(dist_.v.moon)) >= 0.95) ? ss : null;

    const notes = [];
    if (unknown) notes.push("Birth time unknown: Rising sign, houses and Lagna are left out. Moon-based readings are weighted by how likely each Moon sign is across the day.");
    else if (b.time_mode === "approx") notes.push(`Birth time approximate (±${b.window_min} minutes): time-sensitive items are weighted by probability across that window.`);
    const list = (o, f = (k, v) => `${k} (${percent(v)}%)`) => Object.entries(o).map(([k, v]) => f(k, v)).join(" or ");
    if (Object.keys(dist_.w.moon).length > 1) notes.push("Your Moon sign could be " + list(dist_.w.moon) + " depending on exact time.");
    if (Object.keys(dist_.v.nakshatra).length > 1) notes.push("Your Moon nakshatra could be " + list(dist_.v.nakshatra) + ".");
    if (Object.keys(sunW).length > 1) notes.push("Your Sun was near a sign boundary on this day: " + list(sunW) + " (tropical).");
    if (Object.keys(sunV).length > 1) notes.push("Your sidereal Sun was near a sign boundary: " + list(sunV) + ".");

    const num = A.numerology(b.name.trim() ? b.name : "", c, today, b.current_name);

    // BaZi over the plausible window
    const withHour = b.time_mode === "exact", pc = { year: new Map(), month: new Map(), day: new Map() }, pobj = new Map();
    let hourP = null;
    for (const { utc, w } of sm) {
      const sun = E.tropLon("Sun", utc), lp = A.localParts(utc, b.tz), pl = A.baziPillars(sun, lp, withHour);
      for (const k of ["year", "month", "day"]) {
        const key = pl[k].stem + "|" + pl[k].branch; pc[k].set(key, (pc[k].get(key) || 0) + w); pobj.set(k + "|" + key, pl[k]);
      }
      if (withHour) hourP = pl.hour;
    }
    const mostCommon = (m) => [...m.entries()].sort((a, b) => b[1] - a[1]);
    const modalP = {}; for (const k of Object.keys(pc)) modalP[k] = pobj.get(k + "|" + mostCommon(pc[k])[0][0]);
    modalP.hour = hourP;
    const tot = Object.fromEntries(Object.entries(pc).map(([k, m]) => [k, [...m.values()].reduce((a, b) => a + b, 0)]));
    const bzDist = {
      day_master: dist([...pc.day.entries()].map(([key, v]) => { const o = pobj.get("day|" + key); return [`${o.polarity} ${o.stem_el}`, v]; })),
      year_animal: dist([...pc.year.entries()].map(([key, v]) => [pobj.get("year|" + key).animal, v])),
      month_animal: dist([...pc.month.entries()].map(([key, v]) => [pobj.get("month|" + key).animal, v])),
      hour_animal: modalP.hour ? { [modalP.hour.animal]: 1 } : {},
    };
    for (const k of Object.keys(pc)) if (pc[k].size > 1)
      notes.push(`Your Chinese ${k} pillar could be ${mostCommon(pc[k]).map(([key, v]) => `${key.split("|").join(" ")} (${percent(v / tot[k])}%)`).join(" or ")}.`);
    const bazi = Object.assign(A.baziPublic(modalP), { dist: bzDist });

    // timing
    let ascForTiming = null;
    if (Object.keys(dist_.w.asc || {}).length) { const [s, p] = best(dist_.w.asc); ascForTiming = p >= 0.6 ? s : null; }
    const timing = A.timingCompute(c, refJd, refW.planets.Sun.lon, ascForTiming, b.lat, b.lon, today, housesOk);

    // birth-time helper: Rising sign across the window
    const timeline = [];
    if (b.time_mode !== "exact") {
      const pts = b.time_mode === "approx" ? sm.map((s) => s.utc) : Array.from({ length: 24 }, (_, h) => A.toUtc(c, h, 0, b.tz));
      for (const utc of pts) {
        const ww = A.signOf(E.houses(utc, b.lat, b.lon).asc), vv = A.signOf(E.sidAscendant(utc, b.lat, b.lon));
        const lp = A.localParts(utc, b.tz), lt = `${String(lp.h).padStart(2, "0")}:${String(lp.mi).padStart(2, "0")}`;
        const last = timeline[timeline.length - 1];
        if (last && last.western === ww && last.vedic === vv) last.to = lt; else timeline.push({ from: lt, to: lt, western: ww, vedic: vv });
      }
    }

    // dasha output
    const timelineD = [];
    for (const p of periods) if (new Date(p.end).getUTCFullYear() > c.y && new Date(p.start).getUTCFullYear() < c.y + 100)
      timelineD.push({ lord: p.lord, start: A.isoDate(p.start), end: A.isoDate(p.end) });
    const dasha = { timeline: timelineD, current: null };
    if (cur) {
      dasha.current = { maha: cur.maha.lord, maha_start: A.isoDate(cur.maha.start), maha_end: A.isoDate(cur.maha.end),
        antar: cur.antar ? cur.antar.lord : null, antar_start: cur.antar ? A.isoDate(cur.antar.start) : null, antar_end: cur.antar ? A.isoDate(cur.antar.end) : null };
      dasha.uncertain = b.time_mode !== "exact";
      if (dist_.dasha && Object.keys(dist_.dasha).length > 1) dasha.alternatives = dist_.dasha;
    }
    const pad = (n) => String(n).padStart(2, "0");
    return {
      meta: { name: b.name, date: b.date, time_mode: b.time_mode, time: unknown ? null : `${pad(b.hour)}:${pad(b.minute)}`,
        window_min: b.time_mode === "approx" ? b.window_min : null, place: b.place, lat: b.lat, lon: b.lon, tz: b.tz,
        ref_utc: refUtc.toISOString(), today: `${today.y}-${pad(today.m)}-${pad(today.d)}`, houses_known: housesOk },
      western: Object.assign({}, refW, { aspects, elements: elem, modalities: modal }),
      vedic: Object.assign({}, refV, { yogas, sade_sati: sade, ayanamsa_name: "Lahiri (Chitrapaksha)" }),
      numerology: num, dist: dist_, dasha, bazi, timing, rising_timeline: timeline, notes,
    };
  }

  // ---------- synthesis ---------------------------------------------------------------------------------
  const TRAITS = S.TRAIT_KEYS, NT = TRAITS.length, TIDX = Object.fromEntries(TRAITS.map((t, i) => [t, i]));
  function signSignals(system, body, label, d, weights, tag, needsTime = false, dignity = null) {
    const mult = dignity === "domicile" || dignity === "exalted" ? 1.15 : 1;
    return Object.entries(d).map(([sign, prob]) => ({ system, body, key: sign, prob, vec: S.SIGN_VEC[sign],
      w: Object.fromEntries(Object.entries(weights).map(([k, v]) => [k, v * mult])), needs_time: needsTime,
      source: `${label} in ${sign}` + (prob < 0.99 ? ` (${percent(prob)}% likely)` : "") + ` · ${tag}` }));
  }
  function collectSignals(prof) {
    const sig = [], w = prof.western, v = prof.vedic, n = prof.numerology, dist_ = prof.dist;
    for (const [body, p] of Object.entries(w.planets)) {
      if (body === "South Node" || !S.W_WEIGHTS[body]) continue;
      let d = (body === "Sun" || body === "Moon") ? dist_.w[body.toLowerCase()] : null;
      d = d && Object.keys(d).length ? d : { [p.sign]: 1 };
      sig.push(...signSignals("western", body, body, d, S.W_WEIGHTS[body], "Western", false, p.dignity));
    }
    for (const [key, label, wkey] of [["asc", "Rising", "Asc"], ["mc", "Midheaven", "MC"], ["dsc", "Descendant", "Dsc"]]) {
      const d = dist_.w[key];
      if (d && Object.keys(d).length) sig.push(...signSignals("western", wkey, label, d, S.W_WEIGHTS[wkey], "Western", true));
    }
    for (const [body, p] of Object.entries(v.planets)) {
      if (!S.V_WEIGHTS[body]) continue;
      let d = (body === "Sun" || body === "Moon") ? dist_.v[body.toLowerCase()] : null;
      d = d && Object.keys(d).length ? d : { [p.sign]: 1 };
      sig.push(...signSignals("vedic", body, body, d, S.V_WEIGHTS[body], "Vedic", false, p.dignity));
    }
    const lag = dist_.v.lagna;
    if (lag && Object.keys(lag).length) {
      sig.push(...signSignals("vedic", "Lagna", "Lagna", lag, S.V_WEIGHTS.Lagna, "Vedic", true));
      const h10 = {}, h7 = {};
      for (const [s, pr] of Object.entries(lag)) { h10[SIGNS[(SIGNS.indexOf(s) + 9) % 12]] = pr; h7[SIGNS[(SIGNS.indexOf(s) + 6) % 12]] = pr; }
      sig.push(...signSignals("vedic", "H10", "10th house", h10, S.V_WEIGHTS.H10, "Vedic", true));
      sig.push(...signSignals("vedic", "H7", "7th house", h7, S.V_WEIGHTS.H7, "Vedic", true));
    }
    for (const [nk, prob] of Object.entries(dist_.v.nakshatra)) {
      const vec = {}; D.NAKSHATRA_INFO[nk][0].forEach((t, i) => { vec[t] = i === 0 ? 1.0 : 0.7; });
      sig.push({ system: "vedic", body: "Nakshatra", key: nk, prob, vec, w: S.V_WEIGHTS.Nakshatra, needs_time: false,
        source: `Moon in ${nk} nakshatra` + (prob < 0.99 ? ` (${percent(prob)}% likely)` : "") + " · Vedic" });
    }
    const num = (key, value, label, weights) => {
      if (S.NUM_VEC[value]) sig.push({ system: "numerology", body: key, key: value, prob: 1, vec: S.NUM_VEC[value], w: weights, needs_time: false, source: `${label} ${value} · Numerology` });
    };
    num("life_path", n.life_path.number, "Life Path", S.N_WEIGHTS.life_path);
    num("birthday", n.birthday, "Birthday number", S.N_WEIGHTS.birthday);
    if (n.pythagorean) {
      const p = n.pythagorean;
      num("expression", p.expression, "Expression", S.N_WEIGHTS.expression);
      num("soul_urge", p.soul_urge, "Soul Urge", S.N_WEIGHTS.soul_urge);
      num("personality", p.personality, "Personality", S.N_WEIGHTS.personality);
      num("maturity", n.maturity, "Maturity", S.N_WEIGHTS.maturity);
      const ch = n.chaldean;
      if (ch && ch.expression !== p.expression) num("expression_chaldean", ch.expression, "Expression (Chaldean)", S.N_WEIGHTS.expression_chaldean);
    }
    const bz = prof.bazi;
    if (bz) {
      const dd = bz.dist;
      for (const [key, label, vec, d] of [["day_master", "Day Master", S.DM_VEC, dd.day_master], ["year_animal", "Year animal", S.ANIMAL_VEC, dd.year_animal],
        ["month_animal", "Month animal", S.ANIMAL_VEC, dd.month_animal], ["hour_animal", "Hour animal", S.ANIMAL_VEC, dd.hour_animal]])
        for (const [k, pr] of Object.entries(d)) sig.push({ system: "bazi", body: key, key: k, prob: pr, vec: vec[k], w: S.B_WEIGHTS[key], needs_time: key === "hour_animal",
          source: `${label}: ${k}` + (pr < 0.99 ? ` (${percent(pr)}% likely)` : "") + " · Chinese BaZi" });
      const tot = Object.values(bz.elements).reduce((a, b) => a + b, 0) || 1;
      for (const [el, c] of Object.entries(bz.elements)) if (c)
        sig.push({ system: "bazi", body: "element", key: el, prob: c / tot * 5 / 5, vec: S.ELEMENT_VEC[el], w: S.B_WEIGHTS.element, needs_time: false,
          source: `${el} element (${c} of ${tot}) · Chinese BaZi` });
    }
    return sig;
  }
  function synthesize(prof, calibrate = true) {
    const signals = collectSignals(prof), SYS = S.SYSTEMS, DOM = S.DOMAINS;
    const raw = {}, contrib = {};
    for (const s of SYS) { raw[s] = {}; for (const d of DOM) raw[s][d] = new Array(NT).fill(0); }
    for (const sg of signals) for (const [d, wt] of Object.entries(sg.w)) {
      if (!wt) continue;
      for (const [t, tv] of Object.entries(sg.vec)) {
        const cc = wt * sg.prob * tv; raw[sg.system][d][TIDX[t]] += cc;
        (contrib[d + "|" + t] ||= []).push([cc, sg]);
      }
    }
    const norm = {};
    for (const s of SYS) { norm[s] = {}; for (const d of DOM) { const tot = raw[s][d].reduce((a, b) => a + b, 0); norm[s][d] = raw[s][d].map((x) => (x + S.PRIOR / NT) / (tot + S.PRIOR) * NT); } }
    if (calibrate && S.BASELINE) for (const s of SYS) for (const d of DOM) norm[s][d] = norm[s][d].map((x, i) => x / S.BASELINE[s][d][i]);
    const out = {};
    for (const d of DOM) {
      const rows = TRAITS.map((t, i) => {
        const per = {}; for (const s of SYS) per[s] = A.pyround(norm[s][d][i], 2);
        const totalW = SYS.reduce((a, s) => a + S.SYSTEM_WEIGHT[s], 0);
        const score = SYS.reduce((a, s) => a + per[s] * S.SYSTEM_WEIGHT[s], 0) / totalW;
        const supporters = SYS.filter((s) => per[s] >= S.SUPPORT);
        const ev = (contrib[d + "|" + t] || []).slice().sort((a, b) => b[0] - a[0]).slice(0, 4);
        return { trait: t, score: A.pyround(score, 2), _raw: score, per_system: per, supporters,
          level: supporters.length >= 3 ? "strong" : supporters.length === 2 ? "supported" : supporters.length === 1 ? "single" : "none",
          evidence: ev.map(([, sg]) => ({ source: sg.source, system: sg.system, needs_time: sg.needs_time })) };
      });
      rows.sort((a, b) => (Math.round(b._raw * 1e6) - Math.round(a._raw * 1e6)) || (TIDX[a.trait] - TIDX[b.trait]));
      out[d] = rows;
    }
    return { domains: out, signal_count: signals.length, _norm: norm };
  }
  const top = (synth, domain, k = 3, minScore = 1.15) => { const rows = synth.domains[domain].slice(0, k).filter((r) => r._raw >= minScore); return rows.length ? rows : synth.domains[domain].slice(0, 1); };
  const lowest = (synth, domain, k = 2) => synth.domains[domain].slice().sort((a, b) => (Math.round(a._raw * 1e6) - Math.round(b._raw * 1e6)) || (TIDX[a.trait] - TIDX[b.trait])).slice(0, k);
  function systemDisagreements(synth, domain = "character") {
    const res = [];
    for (const r of synth.domains[domain]) {
      const ps = r.per_system, ks = Object.keys(ps);
      const hi = ks.reduce((a, b) => (ps[b] > ps[a] ? b : a)), lo = ks.reduce((a, b) => (ps[b] < ps[a] ? b : a));
      if (ps[hi] >= 1.8 && ps[lo] <= 0.5) res.push({ trait: r.trait, high: hi, low: lo, per_system: ps });
    }
    return res.sort((a, b) => (b.per_system[b.high] - b.per_system[b.low]) - (a.per_system[a.high] - a.per_system[a.low])).slice(0, 3);
  }
  root.AB.build = build; root.AB.synthesize = synthesize; root.AB.top = top; root.AB.lowest = lowest; root.AB.systemDisagreements = systemDisagreements;
  root.AB.percent = percent; root.AB.dist = dist;
})(typeof window !== "undefined" ? window : globalThis);
