// Twins test: same chart, different names and answers must give different readings; no answers must change nothing.
globalThis.Astronomy = require("./astronomy_node.js");
for (const f of ["data", "ephem", "engine", "profile", "simplify", "quiz", "report", "compat", "api"]) require("./" + f + ".js");
const assert = require("assert");
const base = { date: "2015-06-09", time_mode: "exact", lat: 27.7172, lon: 85.324, tz: "Asia/Kathmandu", place: "KTM" };
const today = { y: 2026, m: 11, d: 12 };
const plain = AstroEngine.profile({ ...base, name: "Aarav Shrestha", time: "10:14" }, today);
const same = AstroEngine.profile({ ...base, name: "Aarav Shrestha", time: "10:14", answers: [null, null, null, null, null, null, null, null], fit: {} }, today);
assert.deepStrictEqual(JSON.stringify(plain.report), JSON.stringify(same.report), "no answers must change nothing");
const A = AstroEngine.profile({ ...base, name: "Aarav Shrestha", time: "10:14", answers: [0, 0, 0, 2, 2, 0, 0, 0] }, today);
const B = AstroEngine.profile({ ...base, name: "Aarav Shrestha", time: "10:15", answers: [2, 2, 2, 0, 0, 2, 2, 2] }, today);   // same name on purpose
const top = (r) => r.consensus[0].rows.slice(0, 3).map((x) => x.trait).join(",");
assert.notStrictEqual(top(A), top(B), "opposite answers must give different top traits even with the same name");
assert.strictEqual(A.profile.western.planets.Sun.sign, B.profile.western.planets.Sun.sign, "same sky");
assert(A.consensus[0].rows[0].per_system.you !== undefined, "answers shown as a 'you' bar");
// "Fits me" raises a trait, "Doesn't fit" lowers it
const t = plain.consensus[0].rows[5].trait, idx = (r) => r.consensus[0].rows.findIndex((x) => x.trait === t);
const up = AstroEngine.profile({ ...base, name: "Aarav Shrestha", time: "10:14", fit: { [t]: 1 } }, today), down = AstroEngine.profile({ ...base, name: "Aarav Shrestha", time: "10:14", fit: { [t]: -1 } }, today);
assert(idx(up) < idx(plain) && idx(down) > idx(plain), "fit feedback must move the trait");
assert(AB.selfVector([0, 0, null, null, null, null, null, null]) === null, "fewer than 4 answers are ignored");
console.log("twin / quiz / fit tests ok:", top(A), "vs", top(B));
