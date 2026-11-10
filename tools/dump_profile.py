"""Dumps Python-engine API-shaped output for given inputs (oracle for js/compare.js).
   python tools/dump_profile.py inputs.json out.json"""
import datetime as dt, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine.profile import Birth, build
from engine.synthesis import synthesize
from engine.report import build_report
from engine import compat

def to_birth(i):
    h, m = 12, 0
    if i["time_mode"] in ("exact", "approx"):
        h, m = [int(x) for x in i["time"].split(":")[:2]]
    return Birth(name=i["name"].strip(), date=dt.date.fromisoformat(i["date"]), time_mode=i["time_mode"], hour=h, minute=m,
                 window_min=i.get("window_min", 120), lat=i["lat"], lon=i["lon"], tz=i["tz"], place=i.get("place", ""),
                 current_name=i.get("current_name"))

def main(inp, out, today):
    today = dt.date.fromisoformat(today)
    res = []
    for i in json.load(open(inp)):
        p = build(to_birth(i), today); s = synthesize(p)
        rep = build_report(p, s)
        res.append({"profile": p, "report": rep, "synth": {d: [{k: r[k] for k in ("trait", "score", "per_system", "level", "supporters")} for r in rows] for d, rows in s["domains"].items()}})
    json.dump(res, open(out, "w"), default=str)

if __name__ == "__main__":
    main(*sys.argv[1:4])
