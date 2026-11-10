"""The browser (JavaScript) engine must reproduce the Python engine. Skipped if Node.js is unavailable."""
import datetime as dt
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")

PLACES = [("Asia/Kathmandu", 27.7172, 85.324), ("Asia/Kolkata", 19.076, 72.8777), ("Europe/London", 51.5072, -0.1276),
          ("America/New_York", 40.7128, -74.006), ("Australia/Sydney", -33.8688, 151.2093), ("Asia/Tokyo", 35.6762, 139.6503),
          ("America/Sao_Paulo", -23.5505, -46.6333), ("Europe/Oslo", 69.65, 18.96), ("Africa/Lagos", 6.5244, 3.3792)]
NAMES = ["Asha Rai", "Rohan Karki", "Li Wei Chen", "Maria José Álvarez", "John Smith", "Zoë Ñandú-Lee", "Omar Hassan"]
# differences that are expected between two ephemerides: ordering of near-tied aspects, dasha sample boundaries
ALLOWED = ("profile.western.aspects", "profile.dist.dasha", "profile.dasha.alternatives")


def run_node(*args):
    return subprocess.run(["node", *args], cwd=ROOT, capture_output=True, text=True, timeout=300)


def test_ephemeris_matches_swiss_ephemeris():
    r = run_node("js/check_ephem.js", "js/ref_ephem.json")
    assert r.returncode == 0, r.stderr
    worst = {}
    for line in r.stdout.splitlines():
        if ":" in line and "{" not in line:
            k, v = line.strip().rstrip(",").split(":"); worst[k.strip()] = float(v)
    assert all(v < 0.02 for k, v in worst.items() if k.startswith("trop_") or k in ("asc", "mc", "cusp", "sidAsc", "ayanamsa", "meanNode", "trueNode")), worst


def test_profiles_and_reports_match_python(tmp_path):
    from dump_profile import main as dump
    random.seed(5150); ins = []
    for _ in range(25):
        tz, la, lo = random.choice(PLACES); d = dt.date(1940, 1, 1) + dt.timedelta(days=random.randint(0, 30000))
        mode = random.choice(["exact", "exact", "approx", "unknown"]); h, m = random.randint(0, 23), random.randint(0, 59)
        ins.append(dict(name=random.choice(NAMES), current_name=None, date=d.isoformat(), time_mode=mode,
                        time=None if mode == "unknown" else f"{h:02d}:{m:02d}", window_min=random.choice([60, 120, 240]), lat=la, lon=lo, tz=tz, place="x"))
    (tmp_path / "in.json").write_text(json.dumps(ins))
    dump(str(tmp_path / "in.json"), str(tmp_path / "py.json"), "2026-11-10")
    r = run_node("js/compare.js", str(tmp_path / "py.json"), str(tmp_path / "in.json"), "2026-11-10")
    assert r.returncode == 0, r.stderr
    bad = [l for l in r.stdout.splitlines()[1:] if l.strip() and not any(a in l for a in ALLOWED)]
    assert not bad, "\n".join(bad)


def test_compatibility_matches_python(tmp_path):
    from dump_profile import to_birth
    from engine.profile import build
    from engine.synthesis import synthesize
    from engine import compat
    random.seed(77); today = dt.date(2026, 11, 10); cases, out = [], []
    for _ in range(8):
        pair = []
        for _ in range(2):
            tz, la, lo = random.choice(PLACES)
            pair.append(dict(name=random.choice(NAMES), current_name=None, date=(dt.date(1950, 1, 1) + dt.timedelta(days=random.randint(0, 25000))).isoformat(),
                             time_mode="exact", time=f"{random.randint(0,23):02d}:{random.randint(0,59):02d}", window_min=120, lat=la, lon=lo, tz=tz, place="x"))
        cases.append(pair)
        pa, pb = build(to_birth(pair[0]), today), build(to_birth(pair[1]), today); sa, sb = synthesize(pa), synthesize(pb)
        f = lambda n: n.split()[0] if n.strip() else "Person A"  # noqa: E731
        out.append({rel: compat.compare(pa, pb, sa, sb, rel, f(pair[0]["name"]), f(pair[1]["name"])) for rel in ("romantic", "business", "family", "friends")})
    (tmp_path / "c.json").write_text(json.dumps({"cases": cases, "out": out}, default=str))
    r = run_node("js/compare_compat.js", str(tmp_path / "c.json"))
    assert r.returncode == 0, r.stderr
    assert "with differences: 0" in r.stdout, r.stdout
