/* Short self-check (8 questions) and "Fits me / Doesn't fit" feedback. The chart gives the shared base;
   these answers are the part that can differ between people born at the same moment (e.g. twins). */
(function (root) {
  "use strict";
  const A = root.AB, S = A.D.SYN, TRAITS = S.TRAIT_KEYS, NT = TRAITS.length;
  const QUIZ = [
    { q: "When something new comes up, I usually…", a: ["jump in and work it out as I go", { initiative: 1 }], b: ["stop and think it through first", { precision: 0.5, introspection: 0.5 }] },
    { q: "In a group, I tend to…", a: ["take the lead and be noticed", { radiance: 1 }], b: ["listen and watch first", { introspection: 0.6, harmony: 0.4 }] },
    { q: "When I'm stressed, I…", a: ["talk it out with someone", { curiosity: 0.5, empathy: 0.5 }], b: ["go quiet and work it out alone", { introspection: 0.5, intensity: 0.5 }] },
    { q: "I'm happiest when life is…", a: ["calm, steady and predictable", { steadiness: 0.6, discipline: 0.4 }], b: ["full of change and new places", { exploration: 0.6, curiosity: 0.4 }] },
    { q: "In a disagreement, I…", a: ["look for peace and a middle ground", { harmony: 1 }], b: ["say plainly what I think", { initiative: 0.5, intensity: 0.5 }] },
    { q: "I'm more drawn to…", a: ["new ideas that break the rules", { originality: 1 }], b: ["proven ways that work", { discipline: 0.5, steadiness: 0.5 }] },
    { q: "People would call me…", a: ["warm and caring", { empathy: 1 }], b: ["sharp and well organised", { precision: 0.5, discipline: 0.5 }] },
    { q: "I make sense of things through…", a: ["feelings, hunches and imagination", { imagination: 0.7, empathy: 0.3 }], b: ["facts, details and logic", { precision: 0.7, curiosity: 0.3 }] },
  ];
  const SELF_WEIGHT = 0.4, FIT_STEP = 0.3;

  // answers: array of 8 values: 0 = first option, 1 = a bit of both, 2 = second option, null = skipped
  function selfVector(answers) {
    if (!Array.isArray(answers)) return null;
    const x = Object.fromEntries(TRAITS.map((t) => [t, 0])); let n = 0;
    QUIZ.forEach((q, i) => {
      const v = answers[i]; if (v !== 0 && v !== 1 && v !== 2) return; n++;
      const add = (w, f) => { for (const [t, val] of Object.entries(w)) x[t] += val * f; };
      if (v === 0) add(q.a[1], 1); else if (v === 2) add(q.b[1], 1); else { add(q.a[1], 0.5); add(q.b[1], 0.5); }
    });
    if (n < 4) return null;
    const mean = n / NT, out = {};
    for (const t of TRAITS) out[t] = Math.max(0.35, Math.min(2.6, 0.35 + 0.65 * (x[t] / mean)));
    return out;
  }

  // Blend into a synthesis: 60% chart systems, 40% your answers, plus a nudge from "fits me" / "doesn't fit".
  function applySelf(synth, input) {
    const self = selfVector(input.answers), fit = input.fit || {};
    const hasFit = Object.values(fit).some((v) => v);
    if (!self && !hasFit) return synth;
    const TIDX = Object.fromEntries(TRAITS.map((t, i) => [t, i]));
    for (const d of Object.keys(synth.domains)) {
      for (const r of synth.domains[d]) {
        let raw = r._raw;
        if (self) {
          raw = (1 - SELF_WEIGHT) * raw + SELF_WEIGHT * self[r.trait];
          r.per_system = Object.assign({}, r.per_system, { you: A.pyround(self[r.trait], 2) });
          r.you = self[r.trait] >= S.SUPPORT;
          if (r.you) r.evidence = [{ source: "Your self-check answers", system: "you", needs_time: false }].concat(r.evidence).slice(0, 4);
        }
        raw += FIT_STEP * (fit[r.trait] || 0);
        r._raw = raw; r.score = A.pyround(raw, 2);
      }
      synth.domains[d].sort((a, b) => (Math.round(b._raw * 1e6) - Math.round(a._raw * 1e6)) || (TIDX[a.trait] - TIDX[b.trait]));
    }
    synth._self = true;
    return synth;
  }
  root.AB.QUIZ = QUIZ; root.AB.selfVector = selfVector; root.AB.applySelf = applySelf;
})(typeof window !== "undefined" ? window : globalThis);
