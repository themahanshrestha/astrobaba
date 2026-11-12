/* AstroBaba engine in JavaScript: a port of the Python engine (engine/*.py) that runs entirely in the
   browser. Text and scoring tables come from data.js, generated from the Python content library. */
(function (root) {
  "use strict";
  const D = root.ABDATA, E = root.Ephem;
  const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
  const ELEMENT = Object.fromEntries(SIGNS.map((s, i) => [s, ["fire", "earth", "air", "water"][i % 4]]));
  const MODALITY = Object.fromEntries(SIGNS.map((s, i) => [s, ["cardinal", "fixed", "mutable"][i % 3]]));
  const NAKS = D.ASTRO.NAKSHATRAS, NAK_SPAN = 360 / 27;
  const DASHA_ORDER = D.ASTRO.DASHA_ORDER, DASHA_YEARS = D.ASTRO.DASHA_YEARS, YEAR_DAYS = 365.25;
  const W_BODIES = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"];
  const V_BODIES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
  const SIGN_LORD = {};
  for (const [p, ss] of Object.entries(D.ASTRO.DOMICILE)) for (const s of ss) SIGN_LORD[s] = p;
  const OUTER = new Set(["Uranus", "Neptune", "Pluto"]);
  const ASPECTS = { conjunction: [0, 8], sextile: [60, 5], square: [90, 7], trine: [120, 7], opposition: [180, 8] };
  const DAY_MS = 86400000;

  // ---------- helpers ---------------------------------------------------------------------------------
  const norm = E.norm;
  function pyround(x, nd = 0) {
    const m = 10 ** nd, v = x * m, f = Math.floor(v);
    const r = Math.abs(v - f - 0.5) < 1e-9 ? (f % 2 === 0 ? f : f + 1) : Math.round(v);
    return r / m;
  }
  const signOf = (l) => SIGNS[Math.floor((((l % 360) + 360) % 360) / 30)];
  const signIdx = (l) => Math.floor((((l % 360) + 360) % 360) / 30);
  const pad2 = (n) => String(n).padStart(2, "0");
  function fmtDeg(l) {
    const d = ((l % 30) + 30) % 30;
    return `${Math.floor(d)}°${pad2(pyround((d % 1) * 60))}'`;
  }
  function angDiff(a, b) { const d = Math.abs(a - b) % 360; return Math.min(d, 360 - d); }
  function dignity(planet, sign) {
    const dom = D.ASTRO.DOMICILE[planet];
    if (dom && dom.includes(sign)) return "domicile";
    if (D.ASTRO.EXALT[planet] === sign) return "exalted";
    if (dom) {
      const o1 = SIGNS[(SIGNS.indexOf(dom[0]) + 6) % 12], o2 = SIGNS[(SIGNS.indexOf(dom[dom.length - 1]) + 6) % 12];
      if (sign === o1 || sign === o2) return "detriment";
    }
    if (D.ASTRO.EXALT[planet] && SIGNS[(SIGNS.indexOf(D.ASTRO.EXALT[planet]) + 6) % 12] === sign) return "fall";
    return null;
  }
  const dateOf = (s) => { const [y, m, d] = s.split("-").map(Number); return { y, m, d }; };
  const dayNum = (y, m, d) => Math.floor(Date.UTC(y, m - 1, d) / DAY_MS);
  function addDaysYMD(c, n) { const t = new Date(Date.UTC(c.y, c.m - 1, c.d) + n * DAY_MS); return { y: t.getUTCFullYear(), m: t.getUTCMonth() + 1, d: t.getUTCDate() }; }
  const isoDate = (ms) => { const t = new Date(ms); return `${t.getUTCFullYear()}-${pad2(t.getUTCMonth() + 1)}-${pad2(t.getUTCDate())}`; };

  // ---------- time zones (historical rules come from the browser's IANA database) --------------------
  const fmtCache = {};
  function partsAt(ms, tz) {
    const f = fmtCache[tz] || (fmtCache[tz] = new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric", second: "numeric", era: "short" }));
    const p = {}; for (const x of f.formatToParts(new Date(ms))) p[x.type] = x.value;
    let y = +p.year; if (p.era && /^B/i.test(p.era)) y = 1 - y;
    return { y, m: +p.month, d: +p.day, h: (+p.hour) % 24, mi: +p.minute, s: +p.second };   // some Safari versions report midnight as 24
  }
  function offsetMs(ms, tz) {
    const p = partsAt(ms, tz);
    const asUtc = Date.UTC(p.y, p.m - 1, p.d, p.h, p.mi, p.s);
    return asUtc - Math.floor(ms / 1000) * 1000;
  }
  function toUtc(c, h, mi, tz) {
    const naive = Date.UTC(c.y, c.m - 1, c.d, h, mi);
    let utc = naive - offsetMs(naive, tz);
    utc = naive - offsetMs(utc, tz);
    return new Date(utc);
  }
  function localParts(date, tz) { return partsAt(date.getTime(), tz); }

  // ---------- Western & Vedic charts ------------------------------------------------------------------
  function houseOf(lon, cusps) {
    for (let i = 0; i < 12; i++) {
      const a = cusps[i], b = cusps[(i + 1) % 12], span = norm(b - a);
      if (norm(lon - a) < span) return i + 1;
    }
    return 1;
  }
  function western(date, lat, lon, withHouses = true) {
    const planets = {};
    for (const n of W_BODIES) {
      const { lon: l, speed } = E.tropLonSpeed(n, date);
      planets[n] = { lon: l, sign: signOf(l), deg: fmtDeg(l), retro: speed < 0, dignity: dignity(n, signOf(l)) };
    }
    const jd = E.jdUT(date), nn = E.trueNode(jd), sn = norm(nn + 180);
    planets["North Node"] = { lon: nn, sign: signOf(nn), deg: fmtDeg(nn), retro: true, dignity: null };
    planets["South Node"] = { lon: sn, sign: signOf(sn), deg: fmtDeg(sn), retro: true, dignity: null };
    const out = { planets, asc: null, mc: null, cusps: null };
    if (withHouses) {
      const h = E.houses(date, lat, lon);
      out.cusps = h.cusps;
      out.asc = { lon: h.asc, sign: signOf(h.asc), deg: fmtDeg(h.asc) };
      out.mc = { lon: h.mc, sign: signOf(h.mc), deg: fmtDeg(h.mc) };
      const dsc = norm(h.asc + 180);
      out.dsc = { lon: dsc, sign: signOf(dsc) };
      for (const p of Object.values(planets)) p.house = houseOf(p.lon, h.cusps);
    }
    return out;
  }
  function navamsaIdx(lon) {
    const si = signIdx(lon), start = [0, 9, 6, 3][si % 4];
    return (start + Math.floor((((lon % 30) + 30) % 30) / (30 / 9))) % 12;
  }
  function dasamsaIdx(lon) {
    const si = signIdx(lon), start = si % 2 === 0 ? si : (si + 8) % 12;
    return (start + Math.floor((((lon % 30) + 30) % 30) / 3)) % 12;
  }
  function vplanet(name, l, retro) {
    const nk = Math.floor(l / NAK_SPAN), pada = Math.floor((l % NAK_SPAN) / (NAK_SPAN / 4)) + 1;
    return { lon: l, sign: signOf(l), deg: fmtDeg(l), retro, nakshatra: NAKS[nk], nak_idx: nk, pada,
      navamsa: SIGNS[navamsaIdx(l)], dignity: dignity(name, signOf(l)) };
  }
  function vedic(date, lat, lon, withHouses = true) {
    const jd = E.jdUT(date), ay = E.ayanamsa(jd), planets = {};
    for (const n of V_BODIES) {
      const { lon: l, speed } = E.tropLonSpeed(n, date);
      planets[n] = vplanet(n, norm(l - ay), speed < 0);
    }
    const rahu = norm(E.meanNode(jd) - ay);
    planets.Rahu = vplanet("Rahu", rahu, true);
    planets.Ketu = vplanet("Ketu", norm(rahu + 180), true);
    const out = { planets, lagna: null, ayanamsa: ay };
    if (withHouses) {
      const la = E.sidAscendant(date, lat, lon), li = signIdx(la);
      out.lagna = { lon: la, sign: SIGNS[li], deg: fmtDeg(la), navamsa: SIGNS[navamsaIdx(la)], dasamsa: SIGNS[dasamsaIdx(la)] };
      for (const p of Object.values(planets)) p.house = ((signIdx(p.lon) - li) % 12 + 12) % 12 + 1;
      out.house_signs = Array.from({ length: 12 }, (_, i) => SIGNS[(li + i) % 12]);
    }
    return out;
  }
  function findAspects(items, onlyWith) {
    const names = Object.keys(items), res = [];
    for (let i = 0; i < names.length; i++) for (let j = i + 1; j < names.length; j++) {
      const a = names[i], b = names[j];
      if ((OUTER.has(a) && OUTER.has(b)) || (a.includes("Node") && b.includes("Node"))) continue;
      if (onlyWith && !onlyWith.has(a) && !onlyWith.has(b)) continue;
      const diff = angDiff(items[a], items[b]);
      for (const [aname, [ang, orb]] of Object.entries(ASPECTS)) {
        const lum = a === "Sun" || a === "Moon" || b === "Sun" || b === "Moon";
        const o = orb + (lum ? 1 : 0) - (OUTER.has(a) || OUTER.has(b) || (a + b).includes("Node") ? 2 : 0);
        if (Math.abs(diff - ang) <= o) { res.push({ a, b, type: aname, orb: pyround(Math.abs(diff - ang), 2), max: o, _ratio: Math.abs(diff - ang) / o }); break; }
      }
    }
    const cmpStr = (p, q) => (p < q ? -1 : p > q ? 1 : 0);
    res.sort((x, y) => (Math.round(x._ratio * 1e6) - Math.round(y._ratio * 1e6)) || cmpStr(x.a, y.a) || cmpStr(x.b, y.b));
    for (const r of res) delete r._ratio;
    return res;
  }
  const addYears = (ms, y) => ms + y * YEAR_DAYS * DAY_MS;
  function vimshottari(moonLon, birthMs) {
    const nk = Math.floor(moonLon / NAK_SPAN), elapsed = (moonLon % NAK_SPAN) / NAK_SPAN, first = nk % 9;
    let start = addYears(birthMs, -DASHA_YEARS[DASHA_ORDER[first]] * elapsed);
    const periods = [];
    for (let i = 0; i < 12; i++) {
      const lord = DASHA_ORDER[(first + i) % 9], end = addYears(start, DASHA_YEARS[lord]);
      const antars = []; let s = start;
      for (let j = 0; j < 9; j++) {
        const sub = DASHA_ORDER[(DASHA_ORDER.indexOf(lord) + j) % 9], e = addYears(s, DASHA_YEARS[lord] * DASHA_YEARS[sub] / 120);
        antars.push({ lord: sub, start: s, end: e }); s = e;
      }
      periods.push({ lord, start, end, antars }); start = end;
    }
    return periods;
  }
  function currentDasha(periods, ms) {
    for (const p of periods) if (p.start <= ms && ms < p.end) return { maha: p, antar: p.antars.find((a) => a.start <= ms && ms < a.end) || null };
    return null;
  }
  function sadeSati(moonIdx, date) {
    const l = norm(E.tropLon("Saturn", date) - E.ayanamsa(E.jdUT(date)));
    return { 11: "rising", 0: "peak", 1: "setting" }[(((signIdx(l) - moonIdx) % 12) + 12) % 12] || null;
  }

  // ---------- numerology -------------------------------------------------------------------------------
  const MASTER = new Set([11, 22, 33]), KARMIC = new Set([13, 14, 16, 19]);
  const PYTH = {}, CHALDEAN = {};
  "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").forEach((c, i) => {
    PYTH[c] = (i % 9) + 1;
    CHALDEAN[c] = [1, 2, 3, 4, 5, 8, 3, 5, 1, 1, 2, 3, 4, 5, 7, 8, 1, 2, 3, 4, 6, 6, 6, 5, 1, 7][i];
  });
  const digitSum = (n) => String(n).split("").reduce((a, c) => a + +c, 0);
  function reduceNum(n, keepMaster = true) { while (n > 9 && !(keepMaster && MASTER.has(n))) n = digitSum(n); return n; }
  function reductionTrail(n) { const t = [n]; while (n > 9 && !MASTER.has(n)) { n = digitSum(n); t.push(n); } return t; }
  function cleanName(name) { return name.normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/[^A-Za-z ]/g, "").toUpperCase(); }
  function nameNumbers(name, table) {
    let tot = 0, vow = 0, con = 0; const counts = {}; for (let i = 1; i <= 9; i++) counts[i] = 0;
    for (const w of cleanName(name).split(" ").filter(Boolean)) {
      const hasVowel = [...w].some((c) => "AEIOU".includes(c));
      for (const c of w) {
        const v = table[c], isV = "AEIOU".includes(c) || (c === "Y" && !hasVowel);
        tot += v; counts[v]++; if (isV) vow += v; else con += v;
      }
    }
    return { total: tot, vowels: vow, consonants: con, counts };
  }
  const pack = (raw, keep = true) => ({ raw, number: reduceNum(raw, keep), karmic: reductionTrail(raw).find((t) => KARMIC.has(t)) ?? null });
  function lifePath(c) {
    const m = reduceNum(c.m), d = reduceNum(c.d), y = reduceNum(digitSum(c.y)), raw = m + d + y, r = pack(raw);
    return { number: r.number, raw, karmic: r.karmic ?? (KARMIC.has(c.d) ? c.d : null), parts: [m, d, y] };
  }
  function pinnacles(c, lp) {
    const m = reduceNum(c.m), d = reduceNum(c.d), y = reduceNum(digitSum(c.y));
    const base = { 11: 2, 22: 4, 33: 6 }[lp] || lp;
    const p1 = reduceNum(m + d), p2 = reduceNum(d + y), p3 = reduceNum(p1 + p2), p4 = reduceNum(m + y);
    const c1 = Math.abs(m - d), c2 = Math.abs(d - y), c3 = Math.abs(c1 - c2), c4 = Math.abs(m - y), a1 = 36 - base;
    return { pinnacles: [{ n: p1, from: 0, to: a1 }, { n: p2, from: a1, to: a1 + 9 }, { n: p3, from: a1 + 9, to: a1 + 18 }, { n: p4, from: a1 + 18, to: null }],
      challenges: [c1, c2, c3, c4].map((x) => reduceNum(x, false)) };
  }
  function personalYear(c, t) {
    const py = reduceNum(reduceNum(c.m) + reduceNum(c.d) + reduceNum(digitSum(t.y)), false);
    const pm = reduceNum(py + t.m, false), pd = reduceNum(pm + t.d, false);
    return { year: py, month: pm, day: pd };
  }
  function numerology(birthName, c, today, currentName) {
    const lp = lifePath(c);
    const out = { life_path: lp, birthday: reduceNum(c.d), birthday_raw: c.d, personal: personalYear(c, today), cycles: pinnacles(c, lp.number) };
    out.mulank = { number: reduceNum(c.d, false) };
    out.bhagyank = { number: reduceNum(digitSum(parseInt(`${c.d}${c.m}${c.y}`, 10)), false) };
    const hasName = cleanName(birthName).trim() !== "";
    if (hasName) for (const [key, table] of [["pythagorean", PYTH], ["chaldean", CHALDEAN]]) {
      const nn = nameNumbers(birthName, table), exp = pack(nn.total);
      out[key] = { expression: exp.number, expression_raw: nn.total, karmic: exp.karmic, soul_urge: reduceNum(nn.vowels), personality: reduceNum(nn.consonants), counts: nn.counts };
    }
    if (out.chaldean) out.namank = { number: reduceNum(out.chaldean.expression_raw, false) };
    if (out.pythagorean) {
      const p = out.pythagorean;
      out.maturity = reduceNum(lp.number + p.expression, true);
      const vals = Object.values(p.counts), mx = Math.max(...vals);
      out.missing = Object.entries(p.counts).filter(([, v]) => v === 0).map(([k]) => +k);
      out.dominant = Object.entries(p.counts).filter(([, v]) => v === mx && v > 1).map(([k]) => +k);
      const nn = nameNumbers(birthName, PYTH);
      const set = new Set([lp.karmic, p.karmic, pack(nn.vowels).karmic, pack(nn.consonants).karmic].filter((x) => x));
      out.karmic_debts = [...set].sort((a, b) => a - b);
    } else out.karmic_debts = lp.karmic ? [lp.karmic] : [];
    if (currentName && cleanName(currentName).trim() && cleanName(currentName) !== cleanName(birthName)) {
      const nn = nameNumbers(currentName, PYTH);
      out.current_name = { expression: reduceNum(nn.total), soul_urge: reduceNum(nn.vowels), personality: reduceNum(nn.consonants) };
    }
    return out;
  }

  // ---------- Chinese BaZi -----------------------------------------------------------------------------
  const X = D.EXTRA;
  const BZ_EL = ["Wood", "Fire", "Earth", "Metal", "Water"];
  const PRODUCES = { Wood: "Fire", Fire: "Earth", Earth: "Metal", Metal: "Water", Water: "Wood" };
  const CONTROLS = { Wood: "Earth", Earth: "Water", Water: "Fire", Fire: "Metal", Metal: "Wood" };
  function stemBranch(s, b) {
    return { stem: X.STEMS[s], branch: X.BRANCHES[b], animal: X.ANIMALS[b], stem_el: X.STEM_ELEMENT[s], branch_el: X.BRANCH_ELEMENT[b], polarity: s % 2 === 0 ? "Yang" : "Yin", _s: s, _b: b };
  }
  const mod = (a, n) => ((a % n) + n) % n;
  function dayIndex(c) { const jdn = dayNum(c.y, c.m, c.d) + 2440588; return mod(jdn - 2451545 + 54, 60); }
  function baziPillars(sunLon, lp, withHour) {   // lp: local {y,m,d,h,mi}
    let y = lp.y; if (lp.m <= 2 && sunLon >= 270 && sunLon < 315) y -= 1;
    const ys = mod(y - 4, 10), year = stemBranch(ys, mod(y - 4, 12));
    const m = Math.floor(norm(sunLon - 315) / 30);
    const month = stemBranch((((ys % 5) * 2 + 2 + m) % 10), (2 + m) % 12);
    const dc = lp.h >= 23 ? addDaysYMD(lp, 1) : lp, di = dayIndex(dc), day = stemBranch(di % 10, di % 12);
    const out = { year, month, day, hour: null };
    if (withHour) { const hb = Math.floor((lp.h + 1) / 2) % 12; out.hour = stemBranch(((day._s % 5) * 2 + hb) % 10, hb); }
    return out;
  }
  function baziPublic(p) {
    const out = {};
    for (const k of ["year", "month", "day", "hour"]) out[k] = p[k] ? Object.fromEntries(Object.entries(p[k]).filter(([x]) => !x.startsWith("_"))) : null;
    out.day_master = `${p.day.polarity} ${p.day.stem_el}`;
    const c = Object.fromEntries(BZ_EL.map((e) => [e, 0]));
    for (const [k, pl] of Object.entries(p)) { if (!pl) continue; c[pl.stem_el] += 1; c[pl.branch_el] += k === "month" ? 1.5 : 1; }
    out.elements = c;
    return out;
  }
  const bzSet = (list) => new Set(list.map((p) => p.join("|")));
  const SIX = bzSet(D.BAZI_REL.SIX_HARMONY), CLASH = bzSet(D.BAZI_REL.CLASHES);
  const pairKey = (a, b) => [a, b].sort().join("|");
  function animalRelation(a, b) {
    if (a === b) return "same";
    if (SIX.has(pairKey(a, b))) return "harmony";
    if (D.BAZI_REL.TRINES.some((t) => t.includes(a) && t.includes(b))) return "trine";
    if (CLASH.has(pairKey(a, b))) return "clash";
    return "neutral";
  }
  function elementRelation(a, b) {
    if (a === b) return "same";
    if (PRODUCES[a] === b || PRODUCES[b] === a) return "supportive";
    if (CONTROLS[a] === b || CONTROLS[b] === a) return "controlling";
    return "neutral";
  }

  // ---------- timing -----------------------------------------------------------------------------------
  const ordinal = (n) => `${n}${n % 100 >= 10 && n % 100 <= 20 ? "th" : { 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th"}`;
  function solcross(target, startJd) {   // first Sun crossing of `target` longitude after startJd
    const lonAt = (jd) => E.tropLon("Sun", new Date((jd - 2440587.5) * DAY_MS));
    const diff = (jd) => { let d = lonAt(jd) - target; while (d > 180) d -= 360; while (d < -180) d += 360; return d; };
    let a = startJd, fa = diff(a);
    while (fa > 0) { a += 1; fa = diff(a); }      // move to the "before" side
    let b = a + 1; while (diff(b) < 0) { a = b; b += 1; }
    for (let i = 0; i < 40; i++) { const m = (a + b) / 2; if (diff(m) < 0) a = m; else b = m; }
    return (a + b) / 2;
  }
  function timingCompute(c, birthJd, natalSun, ascSign, lat, lon, today, housesExact) {
    const age = today.y - c.y - ((today.m < c.m || (today.m === c.m && today.d < c.d)) ? 1 : 0);
    let profection = null;
    if (ascSign) {
      const h = age % 12, sign = SIGNS[(SIGNS.indexOf(ascSign) + h) % 12];
      profection = { age, house: h + 1, house_name: X.HOUSE_NAME[h], house_theme: X.HOUSE_THEME[h], sign, lord: SIGN_LORD[sign] };
    }
    const todayJd = Date.UTC(today.y, today.m - 1, today.d, 12) / DAY_MS + 2440587.5;
    const pjd = birthJd + (todayJd - birthJd) / 365.2422, pdate = new Date((pjd - 2440587.5) * DAY_MS);
    const progressed = { sun_sign: signOf(E.tropLon("Sun", pdate)), moon_sign: signOf(E.tropLon("Moon", pdate)) };
    const jdOf = (y) => Date.UTC(y, c.m - 1, Math.min(c.d, 28)) / DAY_MS + 2440587.5 - 6;
    let sr = solcross(natalSun, jdOf(today.y));
    if (sr > todayJd) sr = solcross(natalSun, jdOf(today.y - 1));
    const srDate = new Date((sr - 2440587.5) * DAY_MS), srChart = western(srDate, lat, lon, housesExact);
    const solar_return = { date: isoDate(srDate.getTime()), moon_sign: srChart.planets.Moon.sign, asc_sign: housesExact ? srChart.asc.sign : null };
    const tdate = new Date(Date.UTC(today.y, today.m - 1, today.d, 12)), transits = {};
    for (const n of ["Saturn", "Jupiter"]) {
      const { lon: l, speed } = E.tropLonSpeed(n, tdate), s = signOf(l);
      transits[n] = { sign: s, retro: speed < 0, house: ascSign ? mod(SIGNS.indexOf(s) - SIGNS.indexOf(ascSign), 12) + 1 : null };
    }
    return { age, profection, progressed, solar_return, transits };
  }

  root.AB = { D, E, SIGNS, ELEMENT, MODALITY, NAKS, NAK_SPAN, DASHA_ORDER, DASHA_YEARS, SIGN_LORD, W_BODIES, V_BODIES, ASPECTS, DAY_MS,
    pyround, signOf, signIdx, fmtDeg, angDiff, dignity, dateOf, dayNum, addDaysYMD, isoDate, toUtc, localParts, western, vedic, findAspects,
    vimshottari, currentDasha, sadeSati, numerology, reduceNum, cleanName, baziPillars, baziPublic, animalRelation, elementRelation, timingCompute,
    ordinal, houseOf, mod, addYears, navamsaIdx, dasamsaIdx, norm, X, PYTH, CHALDEAN, nameNumbers, pack };
})(typeof window !== "undefined" ? window : globalThis);
