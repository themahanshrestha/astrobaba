# AstroBaba — Product & Technical Plan (v0.1, pre-build)

Status: v0.3. Owner decisions are recorded in section 15; the Phase 1-4 MVP is built (see section 15). Section 14 questions are now answered.

---

## 0. Honest framing (read first)

1. **"Accurate" has two meanings.** The *calculations* (planet positions, dashas, numerology reductions) can be made provably correct and tested against reference software. The *interpretations* (what a Moon in Rohini means for your career) are tradition-based and have no validated predictive power. The product must be exact about the first and transparent about the second ("traditional reading", not "scientific prediction").
2. **Systems disagree, and naive blending produces mush.** Tropical (Western) and sidereal (Vedic) Sun signs differ for roughly 4 in 5 people (ayanamsa ≈ 24°). Numerology (Pythagorean vs Chaldean) can give different numbers for the same name. The core IP of this app is a **synthesis layer that detects agreement and conflict between systems and says so**, instead of averaging them into generic horoscope prose.
3. **LLM-only readings will hallucinate chart facts.** The engine computes the chart deterministically; the LLM only *narrates* from a structured list of signals it cannot change.
4. **Guardrails are a product feature**: no death/illness/lawsuit/investment-timing predictions, no fear-based remedies upsell, crisis-language handling, clear "entertainment & self-reflection" positioning, and a rule-set that avoids deterministic claims about third parties (e.g. "your partner will cheat").

---

## 1. Product vision

A personal "chart + number + cycle" profile that produces **comprehensive, explainable** analysis of:

- **Character** (core self, emotional nature, mind, drives, strengths/shadow)
- **Career & vocation** (aptitudes, work style, leadership vs. support, money patterns, timing windows)
- **Relationships** (attachment/love style, what you need, compatibility with another person)
- **Life areas** (family, learning, wellbeing-as-lifestyle (non-medical), spirituality, finances at the temperament level)
- **Timing** (current and upcoming cycles: dashas, transits, personal year)

Differentiators: every statement is **traceable** ("Why am I seeing this?" → shows the placement/number and the tradition it comes from), and every report has a **Consensus / Divergence** section across traditions.

---

## 2. Methodology inventory

### Tier 1 — Core (MVP)
| System | Components |
|---|---|
| **Western (tropical)** | Sun/Moon/Rising; all planets Mercury→Pluto; houses (Placidus default, Whole Sign option); aspects with orbs; dignities (domicile, exaltation, detriment, fall); elements/modalities balance; chart patterns (stellium, T-square, grand trine, yod…); North/South Node; Chiron; Lilith; Part of Fortune; retrogrades |
| **Vedic (sidereal / Jyotish)** | Lagna (ascendant), Rashi chart (D1) with whole-sign houses; Moon sign (Rashi) as primary; **27 Nakshatras + padas**; Navamsa (D9); Dasamsa (D10, career); **Vimshottari Dasha** (Maha/Antar/Pratyantar); Yogas (Raja, Dhana, Gaja-Kesari, Pancha Mahapurusha, etc.); Doshas (Manglik, Kaal Sarp, Sade Sati — presented gently, not as fear); Graha strength basics; Gochar (transits); **Ashtakoota/Guna Milan (36 pts)** for compatibility; Panchang (tithi, vara, yoga, karana) |
| **Numerology** | Pythagorean *and* Chaldean (user-selectable, shown side by side where they differ); Life Path, Expression/Destiny, Soul Urge/Heart's Desire, Personality, Birthday, Maturity; Karmic Debt (13/14/16/19); Master numbers (11/22/33 kept unreduced); Personal Year/Month/Day; Pinnacles & Challenges; Lo Shu grid / missing numbers; Name vs. birth-name vs. current-name analysis |

### Tier 2 — Strong additions (v1.x)
- **Western timing**: transits to natal, secondary progressions, solar returns, lunar returns
- **Relationship astrology**: synastry (inter-aspects), composite chart, Davison chart
- **Hellenistic techniques**: annual profections, time-lords, Lots, sect (day/night chart) — excellent for *timing* and currently under-served in apps
- **Chinese BaZi (Four Pillars)** + Chinese zodiac animal/element, Luck Pillars (strong on career/element balance)
- **Vedic extensions**: more divisional charts (D7 children, D12 parents, D60 etc.), Shadbala, Ashtakavarga (transit scoring), Varshaphal (Tajika annual), Muhurta (auspicious timing), Jaimini karakas (Atmakaraka), KP system option, Lal Kitab (optional/cultural)
- **Astrocartography / relocation** (where on Earth specific themes are emphasized)

### Tier 3 — Optional / experimental (flagged as such)
- Human Design, Gene Keys, Mayan Tzolkin, Celtic tree signs, Tarot birth cards, Kabbalistic numerology, Draconic chart, Harmonics, Uranian points, fixed stars, 9 Star Ki.

### Cross-validation layer (things you didn't list but I'd add)
- **Big Five / Enneagram / MBTI self-assessment (short)**: let users take a 5-minute personality questionnaire and compare to the astro/numerology profile. Big Five has actual psychometric validity; it gives users a reality-check and gives *you* data to see which signals people feel are accurate (feedback loop in 9.4).
- **Birth-time rectification** assistant (life-event questionnaire → narrows ascendant), since unknown/inaccurate birth time is the single biggest accuracy killer for Rising sign, houses, Lagna, divisional charts and dashas.

### Explicitly out of scope **[DEFAULT]**
Palmistry/face reading (needs image ML, no formal calc), Nadi leaves, medical astrology, stock/financial-timing astrology, fixed-date death/health predictions.

---

## 3. Synthesis engine (the core IP)

### 3.1 Signal model
Every system emits **typed signals**, not prose:

```
Signal {
  id, system: western|vedic|numerology|bazi|...,
  source: "Moon in Taurus (house 4)" | "Life Path 7" | "Rohini pada 2",
  domain: character|career|relationship|money|growth|timing,
  trait: "emotional_stability" | "analytical_mind" | ...,   // controlled vocabulary
  polarity: +1/-1/0 (strength vs. challenge),
  weight: 0..1 (importance in that tradition: e.g. Sun/Moon/Asc high, minor aspect low),
  confidence: depends on input quality (unknown birth time lowers house-based signals),
  evidence_text_id → curated interpretation snippet
}
```

### 3.2 Trait ontology
~60–100 controlled traits (e.g. `independence`, `emotional_depth`, `structure_seeking`, `communication`, `risk_tolerance`, `leadership`, `service_orientation`, `attachment_security`…) mapped to a common space so Sun-in-Leo, Nakshatra Magha, Life Path 1 and BaZi Fire-Yang can all "vote" on `leadership`.

### 3.3 Scoring & conflict handling
- Weighted vote per trait per domain; **agreement across ≥3 systems = "Strong theme"**, 2 = "Supported", 1 = "Single-tradition note", opposing polarity = **"Tension"** (shown as nuance: "Western reads you as X, Vedic emphasises Y").
- Per-system weights are configurable (user can choose "I trust Vedic more" profiles, and the default weights are a documented, versioned config — not hidden magic).
- Rule engine (not ML) decides *what is true about the chart*; this keeps outputs deterministic and testable.

### 3.4 Narration (UPDATED: no LLM, per owner decision)
- **Superseded:** readings are composed from the curated library by rules only; no model writes text. The paragraph below describes the original LLM idea and is kept for reference.
- Curated **interpretation library** (written/licensed, versioned, ~5–8k snippets at v1: planet×sign, planet×house, nakshatra×planet, numbers 1–33, yogas, dashas, aspects).
- LLM composes the report **only from selected signals + snippets**, in a chosen tone (warm / direct / practical). Guard-checker pass: every claim in the generated text must map back to a signal id; unmapped claims are removed. Banned-topic filter runs last.
- Output is cached by (chart hash, report type, tone, KB version).

---

## 4. Report catalogue

1. **Core Profile** — Big Three (Sun/Moon/Rising) + Vedic Moon sign/nakshatra/Lagna + Life Path/Expression, "Who you are in one page".
2. **Character Deep-Dive** — mind, emotions, drives, strengths, shadows, growth edge.
3. **Career & Purpose** — aptitudes, environments you thrive in, work style, leadership/entrepreneur/employee tendencies, Midheaven/10th house/D10/Life Path, money temperament, timing windows (current dasha/profection/personal year).
4. **Relationships & Love** — love language/attachment tendencies, Venus/Moon/7th house/Darakaraka, Guna Milan basics, patterns to watch.
5. **Compatibility (two people)** — synastry + composite + Ashtakoota + numerology compatibility + BaZi; overall + per-dimension (emotional, communication, values, intimacy, long-term).
6. **Cycles & Timing** — the next 12 months by month: transits, dasha/antardasha, Personal Year/Month, profections; calendar view.
7. **Year Ahead / Solar Return** (v1.x).
8. **Name Analysis** — numerology of name variants; (no "change your name" sales pressure **[DEFAULT]**).
9. **Consensus & Divergence Map** — one-page view of where traditions agree/disagree.
10. **Daily/Weekly insight** (retention feature) — personalised, built from real transits + personal day number.

---

## 5. System architecture

```
Client (Web PWA → later iOS/Android)
   │
API Gateway / BFF
   ├── Auth & Profiles (people, charts, privacy settings)
   ├── Ephemeris Service        (Swiss Ephemeris; pure functions, heavily cached)
   ├── Chart Services           (western, vedic, numerology, bazi … each outputs Signals)
   ├── Synthesis Service        (signal merge, scoring, conflict detection)
   ├── Narration Service        (RAG over interpretation library + LLM + guard-checker)
   ├── Report/PDF Service
   ├── Geo/Time Service         (geocoding + historical timezone resolution)
   └── Billing, Notifications, Analytics
Data: Postgres (profiles, charts, reports), Redis (cache), object storage (PDFs), vector index (interpretation snippets, optional)
```

### 5.1 Recommended stack **[DEFAULT]**
- **Calc backend: Python 3.12 + FastAPI** — `pyswisseph` (Swiss Ephemeris) is the de-facto engine; best ecosystem for astro libs.
- **Frontend: Next.js (React, TypeScript) PWA**, SVG chart wheel (own renderer, Western wheel + North/South Indian Vedic chart styles).
- **DB: Postgres**; **Cache: Redis**; **LLM: Anthropic Claude API** (narration + guard-check).
- Mobile later via React Native/Expo reusing the API.
- Monorepo: `/engine` (Python calc + synthesis), `/api`, `/web`, `/kb` (interpretation library as versioned YAML/JSON), `/tests/golden`.

### 5.2 Accuracy-critical details (these are where astro apps silently go wrong)
- **Swiss Ephemeris licensing**: AGPL or commercial licence (≈ CHF 700 one-time for the professional licence). A closed-source commercial app needs the commercial licence. Budget and decide before building a paid product.
- **Ephemeris files**: use the full `.se1` files (JPL-grade precision) in production, not the Moshier fallback.
- **Birth time → UT conversion** requires *historical* timezone & DST rules (IANA tzdata, plus pre-1970 and country-specific oddities, e.g. India 1942–45 war time, Nepal's +5:45). Wrong here = wrong ascendant.
- **Geocoding** with lat/long/elevation (GeoNames/Mapbox/OSM Nominatim), with disambiguation UI.
- **Ayanamsa**: default **Lahiri (Chitrapaksha)**; allow Raman, KP, Fagan-Bradley. State it on every Vedic output.
- **Nodes**: Vedic default = Mean Rahu/Ketu; Western default = True Node (configurable, labelled).
- **House systems**: Western default Placidus (fallback to Whole Sign/Porphyry above ~66° latitude); Vedic = Whole Sign (and Bhava Chalit view).
- **Dasha year length**: 365.25 days (default) vs 360, configurable; document it.
- **Name transliteration** for numerology (Devanagari/Nepali/Hindi names → Latin spellings) — significant for the likely audience; allow multiple spellings and show impact.
- **Unknown birth time**: do not fake it. Provide a "no-time" mode (Sun, Moon sign(±), planets, nakshatra if Moon far from boundary, numerology) and flag every signal that depends on time.
- **Moon sign boundary warning**: the Moon moves ~13°/day; if birth time is uncertain, warn when sign/nakshatra could change.

---

## 6. Data model (sketch)

- `User` (auth, plan, preferences: tradition weights, tone, language, ayanamsa, house system)
- `Person` (name variants, birth date/time, time-certainty level, place → lat/lon/tz, relation to user) — supports family/partner profiles
- `Chart` (person, system, computed JSON, engine_version, settings hash)
- `SignalSet` (chart_id → signals[])
- `Report` (person(s), type, tone, kb_version, content blocks, citations)
- `Feedback` (report_id, signal_id, "resonates / doesn't") ← drives continuous improvement
- `KBSnippet` (id, system, key, text, tags, version, source/licence)

---

## 7. UX plan

- **Onboarding**: name (all variants) → birth date → time (with "I'm not sure" path + rectification offer) → place (autocomplete) → goals (career? love? both?).
- **Instant "wow" screen** in <10s: Big Three + Moon nakshatra + Life Path + 3 headline traits, free.
- **Chart views**: Western wheel, North Indian diamond, South Indian grid; tap any planet → plain-language meaning + "Why this?".
- **Reports as scrollable story + expandable evidence drawers**; PDF export.
- **Consensus map** visual (radar of traits by system).
- **Compare mode** for two people.
- **Timeline** for cycles/dashas.
- **Language**: English first; Hindi/Nepali next (Vedic audience) **[DEFAULT: EN first, i18n-ready from day 1]**.
- Tone controls: gentle / balanced / blunt (matches "advisor" voice).

---

## 8. Phased roadmap

| Phase | Scope | Exit criteria |
|---|---|---|
| **0. Decisions** (this doc) | Answer section 14; licence decisions; audience; platforms | Signed-off scope |
| **1. Calculation core** | Ephemeris wrapper, geo/timezone, Western natal, Vedic D1/D9/nakshatra/dasha, numerology | **Golden tests pass**: ≥30 reference charts match Astro.com / Jagannatha Hora / Drik Panchang / hand-calculated numerology within tolerance (planets ≤ 1 arc-min, asc ≤ 1°, dasha dates exact) |
| **2. Knowledge base v1** | Trait ontology, signal rules, interpretation snippets for Tier-1 | Editorial review; coverage report (no empty placements) |
| **3. Synthesis + narration** | Scoring, conflict detection, LLM narration with guard-checker | Hallucination audit: 0 unmapped claims across 200 generated reports |
| **4. Web app MVP** | Onboarding, profile, charts, Core Profile, Character, Career, Relationships reports | Usable by 10 pilot users; feedback loop live |
| **5. Compatibility + timing** | Synastry/composite/Ashtakoota, transits/dasha/personal-year timeline | Matches reference outputs |
| **6. Tier-2 systems** | BaZi, Hellenistic profections, solar return, astrocartography | Per-system golden tests |
| **7. Monetization & launch** | Billing, PDF, mobile PWA polish, analytics, legal pages | Public beta |
| **8. Growth** | Daily insights, push notifications, mobile apps, languages, rectification tool | — |

Rough effort (1 strong full-stack dev + me as pair, calendar time): Phases 1–4 ≈ 10–14 weeks; 5–7 ≈ another 8–10 weeks. KB writing (Phase 2) is the long pole and the real quality driver — start it early.

---

## 9. Quality & accuracy strategy

1. **Golden test corpus**: 30+ charts (famous people with Rodden-rated data, edge cases: polar latitudes, DST transitions, 1940s India, Nepal +5:45, births at midnight, retro stations, sign cusps).
2. **Differential testing** against Astro.com, Jagannatha Hora, Drik Panchang; automated nightly.
3. **Property tests** (e.g. house cusps monotonic, sum of dasha = 120y, numerology reductions idempotent).
4. **Interpretation QA**: editorial style guide, contradiction linter (two snippets in one report claiming opposite traits), reading-level check.
5. **User feedback loop**: per-statement "resonates / doesn't" + blind test (does the user pick their own report out of a line-up?). This is the only honest "accuracy" metric available for interpretations; publish internally, use to tune weights.
6. **Versioning**: engine_version + kb_version stored on every report so older reports are reproducible.

---

## 10. Privacy, legal, ethics

- Birth data + names = personal data (GDPR/CCPA/Nepal-India data laws). Encrypt at rest, minimal retention, export/delete account, no selling data.
- Profiles of *other* people (partner, family): require user attestation; allow deletion; do not allow public lookup.
- Disclaimers: entertainment/self-reflection; not medical, legal, financial advice.
- Content policy: no mortality/illness/accident predictions; no coercive "remedy" upsells (gemstones/pujas) unless user opts in to cultural-remedy section; sensitive-topic detection → supportive language and resources.
- Age gating (13+/16+ per region), app-store astrology policy checks.
- Swiss Ephemeris licensing (section 5.2) and third-party text licensing: **write original KB content**; do not copy copyrighted books/sites.

---

## 11. Monetization **[DEFAULT: freemium]**

- **Free**: Big Three, nakshatra, Life Path, 3 traits, daily insight.
- **Pro (subscription)**: full reports, compatibility, timing calendar, PDF exports, multiple profiles.
- **One-off purchases**: deep compatibility report, year-ahead report.
- B2B later: API / white-label for astrologers, "astrologer mode" with raw technical data.

---

## 12. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Users expect "predictions", and are disappointed or harmed | Trust, app-store, ethical | Honest framing, guardrails, self-reflection language |
| Unknown/wrong birth time | Wrong asc/houses/dashas | No-time mode, rectification, confidence flags |
| Generic "Barnum" output | Low differentiation | Specific signal-linked statements, conflict map, personalization from feedback |
| LLM hallucination | Credibility | Deterministic engine + guard-checker + citations |
| KB writing volume | Schedule | Prioritise by weight; AI-draft + human-edit with style guide |
| Swiss Eph licence cost / AGPL | Business | Decide early; commercial licence |
| Vedic-vs-Western purist backlash | Brand | Show both, label clearly, let users set weights |

---

## 13. MVP definition (what I'd build first)

Web app, English, one user + partner profile, Tier-1 systems only, 4 reports (Core, Character, Career, Relationships) + 2-person compatibility, Consensus map, "Why this?" evidence drawers, feedback buttons, PDF export. Everything in Tier 2/3 deferred.

---

## 14. Questions for you (answers change the plan)

1. **Audience & market**: Who is this for (Nepal/India diaspora, Western spiritual-curious, practitioners)? This changes default tradition weights, language, and tone.
2. **Platform**: Web first, or native mobile first?
3. **Business goal**: Personal project, startup, or tool for your own astrology/consulting practice?
4. **Tradition priority**: If Western and Vedic conflict, which leads by default?
5. **AI use**: OK to use the Claude API for narration (per-report cost + needs API key), or must it be 100% template-based/offline?
6. **Content source**: Do you have your own interpretation texts / a style you want to follow, or should I draft original ones?
7. **Compatibility**: Romantic only, or also business partners/family/friends?
8. **Remedies**: Include traditional remedies (mantras, gemstones, pujas)? Opt-in section, or leave out?
9. **Languages**: English only for v1, or Hindi/Nepali too?
10. **Budget**: Okay with Swiss Ephemeris commercial licence if you monetize, and API/hosting costs?
11. **Birth data**: Will many users not know their birth time? (decides how early to build rectification)
12. **Tooling preference**: Happy with Python + Next.js, or do you have a stack/hosting you must use?

---

## 15. Decisions & build status (v0.2)

### Owner decisions
| # | Decision | Effect on the build |
|---|---|---|
| 1 | Audience: everyone, especially people who tried several approaches without learning about themselves | Plain language, self-discovery framing, every statement explainable ("Why this?") |
| 2 | Personal project now, maybe public/monetised later | Swiss Ephemeris used under AGPL for now; **a commercial licence is required before closed-source/commercial release** |
| 3 | Western + Vedic + numerology all included | Three systems vote with equal weight; differences are shown, not hidden |
| 4 | No narration: people read the answers | **No LLM.** Reports are rule-assembled from an original, curated text library; deterministic and testable |
| 5 | Focus: character, strengths, watch-outs, then career, hobbies, relationships (incl. what to look for in a partner) | Dedicated sections, plus additions: inner world, mind/communication, stress & recovery, growth/life lessons, current season (timing), numerology and charts pages |
| 6 | No remedies (gemstones, pujas, mantras) | Not built; Sade Sati phrased as a season, not a warning |
| 7 | Compatibility for romantic, business, family and friends | Relationship type changes factor weights and tips |
| 8 | English only | i18n not built yet; all text lives in `content/` so translation is possible later |
| 9 | Mobile-first responsive web now, native app later; pastel palette, elegant fonts | Dependency-free PWA-style front end (Cormorant Garamond + Jost); the same API can back a React Native/Capacitor app |
| 10 | Birth time may be exact, approximate or unknown | Time-sensitive facts are computed across the plausible window and weighted by probability; unknown time omits Rising/Lagna/houses and says so |

### Built (Phases 1-4 of the roadmap, plus part of 5)
- Calculation core (Swiss Ephemeris): tropical planets, true node, Placidus houses (Porphyry fallback at polar latitudes); sidereal Lahiri planets, mean Rahu/Ketu, Lagna, whole-sign houses, 27 nakshatras with padas, Navamsa, Dasamsa, Vimshottari Maha/Antar, a few yogas, Sade Sati.
- Numerology: Pythagorean and Chaldean, Life Path, Expression, Soul Urge, Personality, Birthday, Maturity, karmic debts, master numbers, Personal Year/Month/Day, pinnacles and challenges, missing numbers, current-name comparison.
- Synthesis: 13-trait vocabulary, per-system normalisation with evidence shrinkage and population calibration, agreement levels, tension pairs, system disagreements.
- Reports: 11 narrative sections plus Numbers, Charts and Agreement pages.
- Compatibility: Western synastry by dimension, Ashtakoota (36 points, modernised gender-neutral), numerology resonance, trait overlap/complement/friction, tips by relationship type.
- 33 automated tests (astronomy cross-checked against independent sources, numerology, time handling, content completeness, API).

### Not built yet / known limits
- Chiron, Lilith, asteroids; secondary progressions and solar returns; Hellenistic profections; BaZi; astrocartography; more divisional charts; Shadbala/Ashtakavarga.
- Birth-time rectification assistant (approximate/unknown handling exists; guided rectification does not).
- Accounts, server-side storage and PDF export (profiles are stored in the browser only).
- Ashtakoota Varna/Vashya use simplified gender-neutral rules and the Yoni matrix was entered from memory of the standard table: **verify against a trusted reference before treating Guna Milan as authoritative.**
- Ephemeris runs on the built-in Moshier model (sub-arcminute). Set `ASTROBABA_EPHE_PATH` to Swiss Ephemeris files for full precision.
- Interpretation text is original and concise (about 9,000 words); expanding depth per placement is the main way to improve the product.

### v0.3 additions (Tier 2 features now built)
- **Chinese BaZi** as a fourth voting system: Four Pillars (year at Lichun, month by solar term, day by the 60-day cycle, hour by two-hour branch), Day Master, year/month animals, element balance. Simplified: no hidden stems or luck pillars; hour uses clock time; day rolls at 11pm.
- **Timing techniques:** Hellenistic annual profections, secondary progressions (Moon and Sun), solar return (Moon and Rising), Jupiter and Saturn transits with houses.
- **Life areas:** which house the Sun, Moon, Venus, Mars, Jupiter and Saturn live in (exact birth time only), plus Vedic Moon/Venus houses.
- **Depth:** Jupiter-sign (where luck grows) and Saturn-sign (slow-burn lessons) readings.
- **Birth-time helper:** for approximate or unknown times, a timeline showing which Rising sign / Lagna applies at each time, with keywords, so people can recognise themselves.
- **Compatibility** now includes a BaZi view (year-animal harmony/trine/clash and Day Master elements); weights re-balanced per relationship type.
- **Delivery:** installable PWA (manifest, offline shell, icons) and a print-friendly "Save as PDF" of the whole report.
- Recalibrated the population baseline for four systems; 45 tests.

### Deliberately not built
| Item | Why |
|---|---|
| Ashtakavarga, Shadbala | Need large lookup tables; I will not enter them from memory in a product that claims accuracy. Add from a verified source. |
| Astrocartography | Needs a map UI and careful line geometry; low value before core depth is expanded |
| Chiron, asteroids | Need the Swiss Ephemeris asteroid files (`seas_*.se1`); add once `ASTROBABA_EPHE_PATH` ships in deployment |
| Human Design, Gene Keys, Mayan, Celtic, Tarot birth cards | Tier 3 / experimental; weakest traditional basis and they would dilute the cross-system agreement signal |
| Accounts, server-side storage | Profiles are browser-only by design (privacy); add with proper auth, encryption and a data-deletion flow before going public |
| Guided rectification from life events | The helper timeline exists; event-based rectification needs a validated method |

### v0.4: runs entirely in the browser
- The engine was ported to JavaScript (`js/`), so the app needs no server and works offline or online.
  Planets come from astronomy-engine (MIT); Placidus houses, ayanamsa and nodes are implemented in `js/ephem.js`.
  Accuracy against Swiss Ephemeris on 60 random times: planets within 0.005 degrees, Ascendant/MC/cusps within 0.0001, true node within 0.01.
- Python remains the reference implementation. `tests/test_js_engine.py` runs both on the same inputs and requires identical
  readings (ignoring near-tie aspect order and dasha dates that differ by a day).
- **Bug fixed:** the BaZi scoring added in v0.3 was never connected, so BaZi did not influence the trait scores until now.
  A test now guards it. Trait ranking also became deterministic (unrounded score, then fixed trait order).
- Hosting is now a drag-and-drop of `site/` (Netlify Drop, Cloudflare Pages, GitHub Pages). The Python hosting options
  are kept in `DEPLOY.md` but are no longer needed.
- Known limits: Safari not tested here (Chromium only); dasha dates can differ by a day from the Swiss-based engine.
