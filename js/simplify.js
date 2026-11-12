/* Makes the report short and plain (mirror of engine/simplify.py: keep both identical). */
(function (root) {
  "use strict";
  const A = root.AB, D = A.D, TRAITS = D.TRAITS, SIGN_TEXT = D.SIGN_TEXT, NUMBERS = D.NUMBERS;
  const TITLES = new Set(Object.values(TRAITS).map((t) => t.title));
  const ADV_STARTS = ["Your Moon nakshatra", "Sun – Moon", "Moon – Saturn", "Mercury – Mars", "Romance and desire", "Where your luck",
    "Karmic debt", "A light element", "Your slow-burn", "Current life chapter", "Your current Vimshottari", "Saturn and your Moon",
    "Your emotional chapter", "A longer chapter", "Your solar-return", "Your dominant element", "Your dominant mode", "Vedic view:",
    "Missing or weak element", "Your Month animal", "How you pursue goals", "Where you spend your energy", "Where growth arrives",
    "Where you build slowly", "Where you feel at home"];
  const ADV_CONTAINS = [" yoga", " is at home", " is exalted", "works against the grain"];

  function firstSentences(text, n = 1) { const parts = text.match(/[^.!?]+[.!?]+(?:\s|$)/g); return parts ? parts.slice(0, n).join("").trim() : text; }
  function keepFirst(blocks, pred, n) { let seen = 0; return blocks.filter((b) => { if (pred(b)) { seen++; if (seen > n) return false; } return true; }); }
  const kw = (sign) => SIGN_TEXT[sign].kw.join(", ");

  function simplify(report) {
    const secs = Object.fromEntries(report.sections.map((s) => [s.id, s])), snap = report.snapshot;
    const tag = (p) => (p && p < 0.9 ? " (likely)" : "");
    const items = [{ label: `Sun in ${snap.sun_western.sign}`, text: kw(snap.sun_western.sign) },
      { label: `Moon in ${snap.moon_western.sign}${tag(snap.moon_western.prob)}`, text: kw(snap.moon_western.sign) }];
    if (snap.rising_western) items.push({ label: `Rising ${snap.rising_western.sign}${tag(snap.rising_western.prob)}`, text: kw(snap.rising_western.sign) });
    const lp = snap.life_path;
    items.push({ label: `Life Path ${lp}`, text: NUMBERS[lp].title.toLowerCase() });
    secs.overview.blocks.unshift({ h: "In short", src: ["Sun, Moon and Rising (Western) and Life Path (numerology)"], time: false, kind: "list", items });

    for (const s of report.sections) {
      let blocks = s.blocks; const sid = s.id;
      if (sid === "strengths") blocks = keepFirst(blocks, (b) => TITLES.has(b.h), 3);
      else if (sid === "watchouts") { blocks = keepFirst(blocks, (b) => b.h.endsWith(": the shadow side"), 3); blocks = keepFirst(blocks, (b) => b.h === "An inner tension", 2); }
      else if (sid === "inner") blocks = blocks.filter((b) => !b.h.startsWith("How stress shows up"));
      else if (sid === "mind") blocks = keepFirst(blocks, (b) => b.h.startsWith("Mental style:"), 1);
      else if (sid === "career") blocks = keepFirst(blocks, (b) => b.h.endsWith(" at work"), 2);
      else if (sid === "relationships") {
        blocks = keepFirst(blocks, (b) => b.h.startsWith("Your love style:"), 1);
        for (const b of blocks) if (b.h === "What to look for in a partner") b.items = b.items.slice(0, 2);
      } else if (sid === "wellbeing") blocks = keepFirst(blocks, (b) => b.h.startsWith("Under pressure:"), 2);
      else if (sid === "purpose") blocks = blocks.filter((b) => !b.h.endsWith("your central lesson"));
      else if (sid === "hobbies") {
        const pick = blocks.filter((b) => ["Moon (what restores", "Venus (what you enjoy", "Because of your"].some((p) => b.h.startsWith(p)));
        const because = pick.filter((b) => b.h.startsWith("Because of your")).slice(0, 2), base = pick.filter((b) => !b.h.startsWith("Because of your"));
        const labels = { "Moon (what restores you)": "To recharge", "Venus (what you enjoy)": "What you enjoy" };
        const its = base.map((b) => ({ label: labels[b.h], text: b.text })).concat(because.map((b) => ({ label: b.h.replace("Because of your", "Your").trim(), text: b.text })));
        const srcs = []; for (const b of pick.slice(0, 4)) srcs.push(...b.src);
        blocks = [{ h: "Things you may enjoy", src: srcs, time: false, kind: "list", items: its }];
      } else if (sid === "timing") {
        const jup = blocks.find((b) => b.h === "Jupiter now"), sat = blocks.find((b) => b.h === "Saturn now");
        if (jup && sat) {
          const merged = { h: "Jupiter and Saturn right now", src: jup.src.concat(sat.src), time: jup.time || sat.time, kind: "text", text: firstSentences(jup.text) + " " + firstSentences(sat.text) };
          blocks = blocks.filter((b) => b.h !== "Jupiter now" && b.h !== "Saturn now").concat([merged]);
        }
      }
      for (const b of blocks) if (b.kind === "views") {
        const signOf = (lab) => lab.split("·")[1].split("(")[0].trim();
        const wi = b.items.filter((i) => i.label.startsWith("Western")), vi = b.items.filter((i) => i.label.startsWith("Vedic"));
        if (wi.length === 1 && vi.length) {
          const vs = vi.map((i) => signOf(i.label)).join(" or "), adds = vi.map((i) => kw(signOf(i.label))).join("; ");
          b.text = `Western astrology places this in ${signOf(wi[0].label)} and Vedic in ${vs}. ` + firstSentences(wi[0].text, 2) + ` Vedic astrology adds: ${adds}.`;
          b.kind = "text"; delete b.items;
        } else b.items = b.items.map((i) => (i.label.startsWith("Vedic") ? { label: i.label, text: "Key qualities: " + kw(signOf(i.label)) + "." } : i));
      }
      for (const b of blocks) if (ADV_STARTS.some((p) => b.h.startsWith(p)) || ADV_CONTAINS.some((c) => b.h.includes(c))) b.adv = true;
      s.blocks = blocks;
    }
    return report;
  }
  root.AB.simplify = simplify; root.AB.firstSentences = firstSentences;
})(typeof window !== "undefined" ? window : globalThis);
