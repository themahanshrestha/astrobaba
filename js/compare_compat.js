// Compares JS compatibility output with the Python engine. node js/compare_compat.js dump.json
const fs = require("fs");
globalThis.Astronomy = require("./astronomy_node.js");
for (const f of ["data", "ephem", "engine", "profile", "simplify", "enrich", "quiz", "report", "compat", "api"]) require("./" + f + ".js");
const { cases, out } = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const today = { y: 2026, m: 11, d: 10 }; let bad = 0, n = 0;
cases.forEach((c, i) => {
  for (const rel of ["romantic", "business", "family", "friends"]) {
    const js = AstroEngine.compare(c[0], c[1], rel, today), py = out[i][rel]; n++;
    const diffs = [];
    if (Math.abs(js.overall - py.overall) > 2) diffs.push(["overall", js.overall, py.overall]);
    js.methods.forEach((m, k) => { if (Math.abs(m.score - py.methods[k].score) > 3) diffs.push([m.name, m.score, py.methods[k].score]); });
    if (js.ashtakoota.total !== py.ashtakoota.total) diffs.push(["guna", js.ashtakoota.total, py.ashtakoota.total]);
    if (JSON.stringify(js.shared) !== JSON.stringify(py.shared)) diffs.push(["shared", js.shared.map((s) => s.key), py.shared.map((s) => s.key)]);
    if (JSON.stringify(js.tips) !== JSON.stringify(py.tips)) diffs.push(["tips"]);
    if (diffs.length) { bad++; if (bad <= 6) console.log(i, rel, JSON.stringify(diffs)); }
  }
});
console.log(`compat compared ${n}; with differences: ${bad}`);
