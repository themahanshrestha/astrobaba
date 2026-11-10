// Differential test: JS engine vs the Python engine on the same inputs.
//   node js/compare.js python_dump.json inputs.json 2026-11-10
const fs = require("fs");
globalThis.Astronomy = require("./astronomy_node.js");
for (const f of ["data", "ephem", "engine", "profile", "report", "compat", "api"]) { try { require("./" + f + ".js"); } catch (e) { if (e.code !== "MODULE_NOT_FOUND") throw e; } }
const AB = globalThis.AB;
const [dumpFile, inputFile, todayStr] = process.argv.slice(2);
const dump = JSON.parse(fs.readFileSync(dumpFile, "utf8")), inputs = JSON.parse(fs.readFileSync(inputFile, "utf8"));
const today = AB.dateOf(todayStr);
const mism = {};
const note = (path, a, b) => { const k = path.replace(/\[\d+\]/g, "[]"); (mism[k] ||= []).push([a, b]); };
const normIso = (s) => (typeof s === "string" ? s.replace("+00:00", ".000Z") : s);
const isDate = (s) => typeof s === "string" && /^\d{4}-\d\d-\d\d$/.test(s);
function cmp(a, b, path, tol) {
  if (typeof a === "number" && typeof b === "number") { if (Math.abs(a - b) > tol * Math.max(1, Math.abs(b) > 100 ? 1 : Math.abs(b))) note(path, a, b); return; }
  if (path.endsWith("ref_utc")) { a = normIso(a); b = normIso(b); }
  if (typeof a === "string" && typeof b === "string" && /^\d\d?°\d\d'$/.test(a) && /^\d\d?°\d\d'$/.test(b)) { const f = (x) => { const [d, m] = x.split("°"); return +d * 60 + parseInt(m); }; if (Math.abs(f(a) - f(b)) > 2) note(path, a, b); return; }
  if (isDate(a) && isDate(b)) { if (Math.abs(Date.parse(a) - Date.parse(b)) > 3 * 86400000) note(path, a, b); return; }
  if (a === null || b === null || typeof a !== typeof b) { if (!(a == null && b == null)) note(path, a, b); return; }
  if (Array.isArray(a)) { if (a.length !== b.length) { note(path + ".length", a.length, b.length); return; } a.forEach((x, i) => cmp(x, b[i], `${path}[${i}]`, tol)); return; }
  if (typeof a === "object") { const ks = new Set([...Object.keys(a), ...Object.keys(b)]); for (const k of ks) { if (!(k in a) || !(k in b)) { note(`${path}.${k}`, k in a, k in b); continue; } cmp(a[k], b[k], `${path}.${k}`, tol); } return; }
  if (a !== b) { const m = (x) => (typeof x === "string" ? x.replace(/\d{4}-\d\d-\d\d/g, "D") : x); if (m(a) !== m(b)) note(path, a, b); }
}
let n = 0;
inputs.forEach((inp, i) => {
  const b = { name: inp.name.trim(), current_name: inp.current_name || null, date: inp.date, time_mode: inp.time_mode, hour: 12, minute: 0, window_min: inp.window_min || 120, lat: inp.lat, lon: inp.lon, tz: inp.tz, place: inp.place || "" };
  if (inp.time) [b.hour, b.minute] = inp.time.split(":").map(Number);
  const prof = AB.build(b, today), syn = AB.synthesize(prof);
  const py = dump[i];
  cmp(JSON.parse(JSON.stringify(prof)), py.profile, "profile", 0.03);
  const byTrait = (rows) => Object.fromEntries(rows.map((r) => [r.trait, { score: r.score, per_system: r.per_system, level: r.level }]));
  const jsSyn = Object.fromEntries(Object.entries(syn.domains).map(([d, rows]) => [d, byTrait(rows)]));
  const pySyn = Object.fromEntries(Object.entries(py.synth).map(([d, rows]) => [d, byTrait(rows)]));
  cmp(jsSyn, pySyn, "synth", 0.08);
  if (AB.buildReport) { const rep = AB.buildReport(prof, syn); cmp(JSON.parse(JSON.stringify(rep)), py.report, "report", 0.03); }
  n++;
});
const keys = Object.keys(mism).sort((a, b) => mism[b].length - mism[a].length);
console.log(`compared ${n} inputs; ${keys.length} distinct mismatching paths`);
for (const k of keys.slice(0, 25)) console.log(String(mism[k].length).padStart(3), k, JSON.stringify(mism[k][0]).slice(0, 160));
