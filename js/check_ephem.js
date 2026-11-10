// Compares js/ephem.js against Swiss Ephemeris reference numbers (made by tools/make_ephem_ref.py).
const fs = require("fs");
globalThis.Astronomy = require("./astronomy_node.js");
const E = require("./ephem.js");
const rows = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const dd = (a, b) => { let d = Math.abs(a - b) % 360; return Math.min(d, 360 - d); };
const worst = {};
const upd = (k, v) => { worst[k] = Math.max(worst[k] || 0, v); };
for (const r of rows) {
  const d = new Date(r.ms), jd = E.jdUT(d);
  for (const n of ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]) upd("trop_" + n, dd(E.tropLon(n, d), r["t_" + n]));
  upd("ayanamsa", Math.abs(E.ayanamsa(jd) - r.ay));
  upd("trueNode", dd(E.trueNode(jd), r.tn)); upd("meanNode", dd(E.meanNode(jd), r.mn));
  const h = E.houses(d, r.lat, r.lon);
  upd("asc", dd(h.asc, r.asc)); upd("mc", dd(h.mc, r.mc)); upd("sidAsc", dd(E.sidAscendant(d, r.lat, r.lon), r.sasc));
  for (let i = 0; i < 12; i++) upd("cusp", dd(h.cusps[i], r.cusps[i]));
}
console.log(Object.fromEntries(Object.entries(worst).map(([k, v]) => [k, +v.toFixed(4)])));
