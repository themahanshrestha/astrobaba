"""AstroBaba API + static web app. Run:  uvicorn api.main:app --reload"""
from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, available_timezones

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import astro, compat, places  # noqa: E402
from engine.profile import Birth, build  # noqa: E402
from engine.report import build_report  # noqa: E402
from engine.synthesis import synthesize, system_disagreements  # noqa: E402
from content.misc import RELATION_TYPES  # noqa: E402
from content.traits import TRAITS  # noqa: E402
from content.numbers import NUMBERS, KARMIC_DEBT  # noqa: E402

app = FastAPI(title="AstroBaba", version="0.1.0")
_TZ = available_timezones()


class BirthIn(BaseModel):
    name: str = Field("", max_length=120)
    current_name: str | None = Field(None, max_length=120)
    date: dt.date
    time_mode: str = "unknown"            # exact | approx | unknown
    time: str | None = None               # "HH:MM"
    window_min: int = 120
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    tz: str
    place: str = ""

    @field_validator("time_mode")
    @classmethod
    def _mode(cls, v):
        if v not in ("exact", "approx", "unknown"):
            raise ValueError("time_mode must be exact, approx or unknown")
        return v

    @field_validator("tz")
    @classmethod
    def _tz(cls, v):
        if v not in _TZ:
            raise ValueError("unknown timezone")
        return v

    @field_validator("date")
    @classmethod
    def _date(cls, v):
        if v.year < 1800 or v > dt.date.today():
            raise ValueError("date out of range")
        return v

    def to_birth(self) -> Birth:
        h, m = 12, 0
        mode = self.time_mode
        if mode in ("exact", "approx"):
            if not self.time:
                mode = "unknown"
            else:
                try:
                    h, m = [int(x) for x in self.time.split(":")[:2]]
                    assert 0 <= h < 24 and 0 <= m < 60
                except Exception:
                    raise HTTPException(422, "time must be HH:MM")
        return Birth(name=self.name.strip(), date=self.date, time_mode=mode, hour=h, minute=m,
                     window_min=self.window_min, lat=self.lat, lon=self.lon, tz=self.tz,
                     place=self.place, current_name=(self.current_name or None))


class CompareIn(BaseModel):
    a: BirthIn
    b: BirthIn
    relation: str = "romantic"


def _full(b: BirthIn):
    birth = b.to_birth()
    prof = build(birth)
    synth = synthesize(prof)
    return prof, synth


@app.get("/api/health")
def health():
    return {"ok": True, "engine": "swisseph", "ephemeris": "swieph" if os.environ.get("ASTROBABA_EPHE_PATH") else "moshier"}


@app.get("/api/places")
def api_places(q: str = ""):
    return {"results": places.search(q)}


@app.get("/api/timezones")
def api_tz():
    return {"timezones": sorted(_TZ)}


@app.post("/api/profile")
def api_profile(b: BirthIn):
    try:
        prof, synth = _full(b)
    except HTTPException:
        raise
    except Exception as e:  # e.g. nonexistent local time
        raise HTTPException(422, f"Could not compute chart: {e}")
    report = build_report(prof, synth)
    consensus = []
    for dom in ("character", "career", "relationships"):
        consensus.append({"domain": dom, "rows": [
            {"trait": r["trait"], "title": TRAITS[r["trait"]]["title"], "score": r["score"],
             "per_system": r["per_system"], "level": r["level"]} for r in synth["domains"][dom]]})
    dis = [{"trait": d["trait"], "title": TRAITS[d["trait"]]["title"], "high": d["high"], "low": d["low"],
            "per_system": d["per_system"]} for d in system_disagreements(synth)]
    numbers_info = {str(k): {"title": v["title"], "core": v["core"], "strength": v["strength"], "watch": v["watch"]}
                    for k, v in NUMBERS.items()}
    return {"profile": _public(prof), "report": report, "consensus": consensus, "disagreements": dis,
            "numbers_info": numbers_info, "karmic": {str(k): v for k, v in KARMIC_DEBT.items()},
            "signal_count": synth["signal_count"]}


def _public(prof: dict) -> dict:
    from content.signs import SIGN_TEXT
    p = dict(prof)
    p["rising_timeline"] = [{**r, "western_kw": SIGN_TEXT[r["western"]]["kw"], "vedic_kw": SIGN_TEXT[r["vedic"]]["kw"]}
                            for r in prof["rising_timeline"]]
    w = p["western"]
    w = {**w, "cusps": w.get("cusps")}
    p["western"] = w
    return p


@app.post("/api/compare")
def api_compare(c: CompareIn):
    if c.relation not in RELATION_TYPES:
        raise HTTPException(422, "relation must be one of " + ", ".join(RELATION_TYPES))
    try:
        pa, sa = _full(c.a)
        pb, sb = _full(c.b)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(422, f"Could not compute chart: {e}")
    na = c.a.name.split()[0] if c.a.name.strip() else "Person A"
    nb = c.b.name.split()[0] if c.b.name.strip() else "Person B"
    return compat.compare(pa, pb, sa, sb, c.relation, na, nb)


WEB = ROOT / "web"
app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(WEB / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse(WEB / "sw.js", media_type="application/javascript", headers={"Service-Worker-Allowed": "/"})


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
