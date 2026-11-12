/* In-browser replacement for the Python API: validates input, builds profiles and comparisons. */
(function (root) {
  "use strict";
  const A = root.AB, D = A.D;
  class InputError extends Error {}
  function todayLocal() { const t = new Date(); return { y: t.getFullYear(), m: t.getMonth() + 1, d: t.getDate() }; }
  function validate(i) {
    const err = (m) => { throw new InputError(m); };
    if (!/^\d{4}-\d\d-\d\d$/.test(i.date || "")) err("Please enter a valid date of birth.");
    const c = A.dateOf(i.date), t = todayLocal();
    if (c.y < 1800 || A.dayNum(c.y, c.m, c.d) > A.dayNum(t.y, t.m, t.d)) err("Date of birth is out of range.");
    if (!(i.lat >= -90 && i.lat <= 90 && i.lon >= -180 && i.lon <= 180)) err("Latitude or longitude is out of range.");
    try { new Intl.DateTimeFormat("en-US", { timeZone: i.tz }); } catch { err("Unknown time zone."); }
    let mode = ["exact", "approx", "unknown"].includes(i.time_mode) ? i.time_mode : "unknown", h = 12, m = 0;
    if (mode !== "unknown") {
      if (!i.time) mode = "unknown";
      else { const mm = /^(\d{1,2}):(\d{2})/.exec(i.time); if (!mm || +mm[1] > 23 || +mm[2] > 59) err("Time must be HH:MM."); h = +mm[1]; m = +mm[2]; }
    }
    return { name: (i.name || "").trim(), current_name: i.current_name || null, date: i.date, time_mode: mode, hour: h, minute: m,
      window_min: i.window_min || 120, lat: +i.lat, lon: +i.lon, tz: i.tz, place: i.place || "",
      answers: Array.isArray(i.answers) ? i.answers : null, fit: i.fit && typeof i.fit === "object" ? i.fit : null };
  }
  function full(input, today) {
    const b = validate(input), prof = A.build(b, today || todayLocal()), synth = A.applySelf(A.synthesize(prof), b);
    return { prof, synth };
  }
  function pub(prof) {
    const SIGN_TEXT = D.SIGN_TEXT, p = Object.assign({}, prof);
    p.rising_timeline = prof.rising_timeline.map((r) => Object.assign({}, r, { western_kw: SIGN_TEXT[r.western].kw, vedic_kw: SIGN_TEXT[r.vedic].kw }));
    return p;
  }
  function profile(input, today) {
    const { prof, synth } = full(input, today), report = A.buildReport(prof, synth);
    const consensus = ["character", "career", "relationships"].map((dom) => ({ domain: dom, rows: synth.domains[dom].map((r) => ({ trait: r.trait, title: D.TRAITS[r.trait].title, score: r.score, per_system: r.per_system, level: r.level })) }));
    const disagreements = A.systemDisagreements(synth).map((d) => ({ trait: d.trait, title: D.TRAITS[d.trait].title, high: d.high, low: d.low, per_system: d.per_system }));
    const numbers_info = Object.fromEntries(Object.entries(D.NUMBERS).map(([k, v]) => [k, { title: v.title, core: v.core, strength: v.strength, watch: v.watch }]));
    return { profile: pub(prof), report, consensus, disagreements, numbers_info, karmic: D.KARMIC_DEBT, signal_count: synth.signal_count };
  }
  function compare(a, b, relation, today) {
    if (!D.RELATION_TYPES[relation]) throw new InputError("Unknown relationship type.");
    const A1 = full(a, today), B1 = full(b, today), first = (n, d) => (n.trim() ? n.trim().split(/\s+/)[0] : d);
    return A.compare(A1.prof, B1.prof, A1.synth, B1.synth, relation, first(a.name || "", "Person A"), first(b.name || "", "Person B"));
  }
  function places(q) {
    q = (q || "").trim().toLowerCase(); if (q.length < 2) return [];
    const P = D.PLACES, hits = P.filter((p) => p.name.toLowerCase().startsWith(q))
      .concat(P.filter((p) => p.name.toLowerCase().includes(q) && !p.name.toLowerCase().startsWith(q)), P.filter((p) => p.country.toLowerCase().includes(q) && !p.name.toLowerCase().includes(q)));
    return hits.slice(0, 8);
  }
  root.AstroEngine = { profile, compare, places, InputError, validate, quiz: A.QUIZ };
})(typeof window !== "undefined" ? window : globalThis);
