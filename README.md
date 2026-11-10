# AstroBaba

A self-discovery platform that reads Western astrology, Vedic astrology, Chinese BaZi and numerology side by side and
shows where they agree and where they differ. It covers character, strengths, watch-outs, career,
hobbies, relationships (including what to look for in a partner), stress and recovery, life lessons,
current timing, and compatibility for romantic, business, family and friendship pairs.

Reports are assembled by rules from an original text library. There is no AI-generated text and
no remedies. See `PLAN.md` for the full plan and decisions.

## Run it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install "setuptools<70" wheel
pip install --no-build-isolation pyswisseph     # needs a C compiler
pip install -r requirements.txt
uvicorn api.main:app --reload                   # http://localhost:8000
```

Tests:

```bash
python -m pytest -q tests
```

## Layout

| Path | What it is |
|---|---|
| `engine/astro.py` | Swiss Ephemeris wrapper: tropical + sidereal (Lahiri), houses, nakshatras, divisional charts, Vimshottari, aspects |
| `engine/numerology.py` | Pythagorean and Chaldean numerology |
| `engine/bazi.py` | Chinese Four Pillars |
| `engine/timing.py` | Profections, progressions, solar return, transits |
| `engine/profile.py` | Builds a profile; handles exact / approximate / unknown birth time by sampling the plausible window |
| `engine/synthesis.py` | Maps placements and numbers to 13 shared traits, scores agreement across systems |
| `engine/baseline.json` | Population calibration (regenerate with `python tools/calibrate.py`) |
| `engine/report.py` | Turns a profile into readable sections, each with "Why this?" sources |
| `engine/compat.py` | Synastry, Ashtakoota, numerology and trait compatibility |
| `content/` | All interpretive text (original). Edit here to change what people read |
| `api/main.py` | FastAPI app (`/api/profile`, `/api/compare`, `/api/places`) and static hosting |
| `web/` | Mobile-first responsive front end (no build step), installable PWA, print-to-PDF |

## How accuracy is handled

- **Calculations are tested** against independent sources: equinox, new and full moon times, a separate
  Sun-longitude formula, the Lahiri ayanamsa, historical timezone offsets, and hand-checked numerology.
- **Interpretations are traditional**, not scientifically validated. The app says so, shows the source
  placement for every statement, and never makes predictions about death, illness, money or legal outcomes.
- **Unknown birth time is not faked.** Time-dependent items (Rising, Lagna, houses, exact Moon sign near
  a boundary, dasha dates) are computed across the plausible window and shown with probabilities.
- Defaults: Lahiri ayanamsa, mean Rahu/Ketu, whole-sign houses for Vedic, Placidus for Western,
  365.25-day dasha years.

## Licensing note

Swiss Ephemeris is AGPL (or a paid commercial licence). Fine for a personal project; buy the
commercial licence before distributing a closed-source or paid version.

## Privacy

Profiles are stored only in the browser (`localStorage`). The server computes and returns results and
stores nothing. Place suggestions use the free Open-Meteo geocoding API from the user's browser, with a
small built-in city list as fallback.

## Feature map

Core self, strengths, watch-outs, inner world, mind, career, hobbies, relationships (what to look for
in a partner), life areas (houses), stress and recovery, growth, current season, Chinese Four Pillars,
numbers, charts and cross-system agreement. Compatibility covers romantic, business, family and
friends. Approximate or unknown birth times are handled with probabilities and a Rising-sign helper.

## Install as an app

Open the site in a mobile browser and choose "Add to Home Screen". When you are ready for native
apps, the same API can back a Capacitor or React Native shell.
