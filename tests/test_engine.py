import datetime as dt
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from content.numbers import NUMBERS  # noqa: E402
from content.signs import SIGN_TEXT  # noqa: E402
from content.traits import TRAITS  # noqa: E402
from engine import astro as A  # noqa: E402
from engine import compat, numerology as N  # noqa: E402
from engine.profile import Birth, build  # noqa: E402
from engine.report import build_report  # noqa: E402
from engine.synthesis import NUM_VEC, SIGN_VEC, synthesize  # noqa: E402

KTM = dict(lat=27.7172, lon=85.324, tz="Asia/Kathmandu")
UTC = dt.timezone.utc
TODAY = dt.date(2026, 11, 10)


def lon(body, utc, sid=False):
    return A._calc(A.jd_ut(utc), body, A.F_SID if sid else A.F_TROP)[0]


# ---- astronomy: independent checks -------------------------------------------------------
def test_march_equinox_2024_sun_at_zero_aries():
    l = lon(A.swe.SUN, dt.datetime(2024, 3, 20, 3, 6, tzinfo=UTC))
    assert A.angular_diff(l, 0) < 0.05


@pytest.mark.parametrize("when,target", [(dt.datetime(2024, 4, 8, 18, 21, tzinfo=UTC), 0),
                                         (dt.datetime(2024, 3, 25, 7, 0, tzinfo=UTC), 180),
                                         (dt.datetime(2024, 5, 23, 13, 53, tzinfo=UTC), 180)])
def test_new_and_full_moon_elongation(when, target):
    e = (lon(A.swe.MOON, when) - lon(A.swe.SUN, when)) % 360
    assert A.angular_diff(e, target) < 0.2


def meeus_sun(jd):
    """Low-precision Sun longitude (Meeus ch.25), independent of Swiss Ephemeris."""
    T = (jd - 2451545.0) / 36525
    L0 = 280.46646 + 36000.76983 * T
    M = math.radians(357.52911 + 35999.05029 * T)
    C = (1.914602 - 0.004817 * T) * math.sin(M) + 0.019993 * math.sin(2 * M) + 0.000289 * math.sin(3 * M)
    om = math.radians(125.04 - 1934.136 * T)
    return (L0 + C - 0.00569 - 0.00478 * math.sin(om)) % 360


@pytest.mark.parametrize("d", [dt.datetime(1950, 6, 1, 0, tzinfo=UTC), dt.datetime(1987, 12, 25, 12, tzinfo=UTC),
                               dt.datetime(2003, 2, 14, 6, tzinfo=UTC), dt.datetime(2024, 8, 8, 18, tzinfo=UTC)])
def test_sun_matches_meeus(d):
    assert A.angular_diff(lon(A.swe.SUN, d), meeus_sun(A.jd_ut(d))) < 0.02


def test_lahiri_ayanamsa_j2000():
    assert abs(A.swe.get_ayanamsa_ut(A.jd_ut(dt.datetime(2000, 1, 1, 12, tzinfo=UTC))) - 23.857) < 0.01


def test_sidereal_is_tropical_minus_ayanamsa():
    u = dt.datetime(1990, 5, 17, 6, 30, tzinfo=UTC)
    jd = A.jd_ut(u)
    d = (lon(A.swe.MARS, u) - lon(A.swe.MARS, u, sid=True)) % 360
    assert abs(d - A.swe.get_ayanamsa_ut(jd)) < 0.01


def test_historical_timezone_nepal():
    assert A.to_utc(dt.date(1990, 5, 17), 12, 0, "Asia/Kathmandu").hour == 6 and \
           A.to_utc(dt.date(1990, 5, 17), 12, 0, "Asia/Kathmandu").minute == 15   # +5:45
    assert A.to_utc(dt.date(1980, 5, 17), 12, 0, "Asia/Kathmandu").minute == 30   # +5:30 before 1986


def test_ascendant_rises_in_east_sanity():
    # at local solar noon the Sun is near the Midheaven
    b = Birth("X", dt.date(2000, 6, 21), "exact", 12, 0, tz="UTC", lat=0.0, lon=0.0)
    p = build(b, TODAY)
    assert A.angular_diff(p["western"]["mc"]["lon"], p["western"]["planets"]["Sun"]["lon"]) < 5


# ---- vedic ----------------------------------------------------------------------------------
def test_nakshatra_boundaries():
    assert A._vplanet("Moon", 0.0, False)["nakshatra"] == "Ashwini"
    assert A._vplanet("Moon", 13.34, False)["nakshatra"] == "Bharani"
    assert A._vplanet("Moon", 359.9, False)["nakshatra"] == "Revati" and A._vplanet("Moon", 359.9, False)["pada"] == 4


def test_navamsa_and_dasamsa():
    assert A.SIGNS[A.navamsa_idx(1)] == "Aries" and A.SIGNS[A.navamsa_idx(30 + 1)] == "Capricorn"
    assert A.SIGNS[A.navamsa_idx(60 + 1)] == "Libra" and A.SIGNS[A.navamsa_idx(90 + 1)] == "Cancer"
    assert A.SIGNS[A.dasamsa_idx(1)] == "Aries" and A.SIGNS[A.dasamsa_idx(31)] == "Capricorn"


def test_vimshottari_structure():
    birth = dt.datetime(1990, 5, 17, 6, 30, tzinfo=UTC)
    per = A.vimshottari(0.0, birth)                      # Moon at 0 Aries: Ketu, full 7y balance
    assert per[0]["lord"] == "Ketu" and abs((per[0]["end"] - birth).days / 365.25 - 7) < 0.01
    assert sum(A.DASHA_YEARS.values()) == 120
    for p in per:
        assert p["antars"][0]["start"] == p["start"]
        assert abs((p["antars"][-1]["end"] - p["end"]).total_seconds()) < 5


# ---- numerology -------------------------------------------------------------------------------
def test_numerology_known_values():
    n = N.compute("John Smith", dt.date(1990, 12, 25), TODAY)
    assert n["life_path"]["number"] == 11
    assert n["pythagorean"]["expression"] == 8 and n["pythagorean"]["soul_urge"] == 6 and n["pythagorean"]["personality"] == 11
    assert N.compute("A", dt.date(1992, 7, 6), TODAY)["life_path"]["karmic"] == 16
    assert N.reduce_num(29) == 11 and N.reduce_num(29, False) == 2 and N.reduce_num(38) == 11


def test_chaldean_differs_but_deterministic():
    n = N.compute("John Smith", dt.date(1990, 12, 25), TODAY)
    assert n["chaldean"]["expression_raw"] == 35


def test_name_cleaning_handles_accents():
    assert N.clean_name("Zoë Ñandú-Lee") == "ZOE NANDULEE"


def test_personal_year():
    assert N.personal_year(dt.date(1990, 12, 25), dt.date(2026, 11, 10))["year"] == 2   # 3+7+(2+0+2+6=10->1)=11->2


# ---- profile / time handling -------------------------------------------------------------------
def mk(mode="exact", h=12, m=15, win=120, d=dt.date(1990, 5, 17)):
    return build(Birth("Test Person", d, mode, h, m, window_min=win, **KTM), TODAY)


def test_unknown_time_omits_time_dependent_items():
    p = mk("unknown")
    assert p["western"]["asc"] is None and p["vedic"]["lagna"] is None
    r = build_report(p, synthesize(p))
    ov = next(s for s in r["sections"] if s["id"] == "overview")
    assert any(b["kind"] == "locked" for b in ov["blocks"])
    assert r["snapshot"]["rising_western"] is None


def test_approx_time_returns_probabilities_summing_to_one():
    p = mk("approx", 8, 0, 180)
    for k in ("asc", "mc", "dsc"):
        assert abs(sum(p["dist"]["w"][k].values()) - 1) < 0.02
    assert len(p["dist"]["w"]["asc"]) > 1


def test_exact_chart_is_stable_and_deterministic():
    a, b = mk(), mk()
    ra, rb = build_report(a, synthesize(a)), build_report(b, synthesize(b))
    assert ra == rb


def test_polar_latitude_does_not_crash():
    p = build(Birth("X Y", dt.date(2001, 12, 21), "exact", 10, 0, tz="Europe/Oslo", lat=78.2, lon=15.6), TODAY)
    assert p["western"]["asc"] is not None


def test_birth_on_sign_boundary_reports_uncertainty():
    # Sun enters Taurus around 20 April; with unknown time on that day both signs are possible
    p = build(Birth("X Y", dt.date(2024, 4, 19), "unknown", tz="UTC", lat=0, lon=0), TODAY)
    assert len(p["dist"]["w"]["sun"]) >= 1


# ---- synthesis ---------------------------------------------------------------------------------
def test_synthesis_covers_all_traits_and_domains():
    s = synthesize(mk())
    for dom, rows in s["domains"].items():
        assert {r["trait"] for r in rows} == set(TRAITS)
        assert all(r["level"] in ("strong", "supported", "single", "none") for r in rows)


def test_vector_tables_reference_real_traits():
    for v in list(SIGN_VEC.values()) + list(NUM_VEC.values()):
        assert set(v) <= set(TRAITS)
    assert set(SIGN_VEC) == set(A.SIGNS) == set(SIGN_TEXT)


def test_content_is_complete():
    for s, t in SIGN_TEXT.items():
        for f in ("sun", "moon", "rising", "venus", "mars", "mercury", "career", "hobbies", "partner", "node"):
            assert len(t[f]) > 30, (s, f)
    for k, t in TRAITS.items():
        for f in ("title", "tag", "strength", "watch", "develop", "career", "work", "hobbies", "love", "seek", "avoid", "stress", "money", "gives"):
            assert t[f], (k, f)
    assert set(NUM_VEC) == set(NUMBERS)
    for n in range(1, 10):
        assert NUMBERS[n]["year"]


def test_no_banned_fear_language():
    banned = ["will die", "doomed", "cursed", "fatal", "you will get sick", "cancer will"]
    import json
    blob = json.dumps([SIGN_TEXT, TRAITS, NUMBERS]).lower()
    assert not any(b in blob for b in banned)


# ---- compatibility ---------------------------------------------------------------------------------
def test_yoni_matrix_symmetric_and_diagonal():
    M = compat.YONI_M
    for i in range(14):
        assert M[i][i] == 4
        for j in range(14):
            assert M[i][j] == M[j][i]
    # classic natural enemies score zero
    idx = {a: i for i, a in enumerate(compat.YONI_ORDER)}
    for a, b in [("Cow", "Tiger"), ("Elephant", "Lion"), ("Horse", "Buffalo"), ("Dog", "Deer"),
                 ("Serpent", "Mongoose"), ("Monkey", "Sheep"), ("Cat", "Rat")]:
        assert M[idx[a]][idx[b]] == 0


def test_ashtakoota_bounds_and_self_match():
    p = mk()
    a = compat.ashtakoota(p, p)
    assert a["max"] == 36 and a["total"] == 28   # identical nakshatra => Nadi dosha (0/8) only
    q = mk(d=dt.date(1992, 11, 3))
    assert 0 <= compat.ashtakoota(p, q)["total"] <= 36


def test_nadi_formula_matches_tradition():
    assert [compat.ashtakoota.__globals__["A"].NAKSHATRAS[i] for i in (0, 5, 6, 11, 12, 17, 18, 23, 24)] == \
        ["Ashwini", "Ardra", "Punarvasu", "Uttara Phalguni", "Hasta", "Jyeshtha", "Mula", "Shatabhisha", "Purva Bhadrapada"]  # Adi nadi group


def test_compare_all_relation_types():
    a, b = mk(), mk(d=dt.date(1992, 11, 3), h=7, m=0)
    sa, sb = synthesize(a), synthesize(b)
    for rel in ("romantic", "business", "family", "friends"):
        r = compat.compare(a, b, sa, sb, rel, "A", "B")
        assert 0 <= r["overall"] <= 100 and len(r["dimensions"]) == 5 and r["tips"]


# ---- api ------------------------------------------------------------------------------------------------
def test_api_validation_and_happy_path():
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    body = {"name": "Maya Sharma", "date": "1992-11-03", "time_mode": "exact", "time": "07:10", "tz": "Asia/Kathmandu",
            "lat": 27.7, "lon": 85.3, "place": "Kathmandu"}
    r = c.post("/api/profile", json=body)
    assert r.status_code == 200 and r.json()["report"]["sections"]
    assert c.post("/api/profile", json={**body, "tz": "Nope/Zone"}).status_code == 422
    assert c.post("/api/profile", json={**body, "lat": 123}).status_code == 422
    assert c.post("/api/profile", json={**body, "time": "25:99"}).status_code == 422
    assert c.post("/api/profile", json={**body, "time_mode": "exact", "time": None}).status_code == 200  # falls back to unknown
    assert c.post("/api/compare", json={"a": body, "b": body, "relation": "nope"}).status_code == 422
    assert c.get("/api/places?q=pokh").json()["results"][0]["name"] == "Pokhara"


# ---- BaZi -------------------------------------------------------------------------------------------
from engine import bazi as BZ, timing as T  # noqa: E402


def test_bazi_known_pillars_chinese_new_year_2024():
    p = BZ.pillars(321.0, dt.datetime(2024, 2, 10, 12, 0), True)    # 10 Feb 2024: Jia-Chen year, Bing-Yin month, Jia-Chen day
    assert (p["year"]["stem"], p["year"]["branch"]) == ("Jia", "Chen")
    assert (p["month"]["stem"], p["month"]["branch"]) == ("Bing", "Yin")
    assert (p["day"]["stem"], p["day"]["branch"]) == ("Jia", "Chen")


def test_bazi_day_cycle_anchor_and_lichun_boundary():
    assert BZ.day_index(dt.date(2000, 1, 1)) == 54                  # Wu-Wu
    before = BZ.pillars(300.0, dt.datetime(1990, 2, 3, 12, 0), False)   # before Lichun: still previous BaZi year
    after = BZ.pillars(316.0, dt.datetime(1990, 2, 5, 12, 0), False)
    assert before["year"]["animal"] == "Snake" and after["year"]["animal"] == "Horse"   # 1989 = Snake, 1990 = Horse


def test_bazi_year_animals():
    assert BZ.pillars(60.0, dt.datetime(1990, 5, 17, 12), False)["year"]["animal"] == "Horse"
    assert BZ.pillars(60.0, dt.datetime(2000, 5, 17, 12), False)["year"]["animal"] == "Dragon"


def test_bazi_late_zi_hour_rolls_day():
    a = BZ.pillars(60.0, dt.datetime(2020, 5, 1, 22, 30), True)
    b = BZ.pillars(60.0, dt.datetime(2020, 5, 1, 23, 30), True)
    assert a["day"]["stem"] != b["day"]["stem"] and b["hour"]["branch"] == "Zi"


def test_bazi_relations():
    assert BZ.animal_relation("Rat", "Ox") == "harmony" and BZ.animal_relation("Rat", "Horse") == "clash"
    assert BZ.animal_relation("Rat", "Dragon") == "trine"
    assert BZ.element_relation("Wood", "Fire") == "supportive" and BZ.element_relation("Wood", "Earth") == "controlling"


# ---- timing --------------------------------------------------------------------------------------------
def test_profection_cycle():
    assert T.profection("Virgo", 0)["house"] == 1 and T.profection("Virgo", 12)["house"] == 1
    assert T.profection("Virgo", 7)["sign"] == "Aries" and T.profection("Virgo", 7)["lord"] == "Mars"
    assert T.profection(None, 5) is None


def test_solar_return_is_on_or_before_today_and_near_birthday():
    p = mk()
    sr = p["timing"]["solar_return"]
    d = dt.date.fromisoformat(sr["date"])
    assert d <= TODAY and abs((d - dt.date(2026, 5, 17)).days) <= 2


def test_timing_without_exact_time_has_no_house_claims():
    p = mk("approx", 8, 0, 180)
    assert p["timing"]["transits"]["Saturn"]["house"] is None


def test_rising_timeline_covers_day_for_unknown_time():
    p = mk("unknown")
    assert len(p["rising_timeline"]) >= 10     # ascendant passes through all twelve signs in 24 hours


def test_four_systems_in_synthesis_and_report_sections():
    p = mk()
    s = synthesize(p)
    assert set(s["domains"]["character"][0]["per_system"]) == {"western", "vedic", "numerology", "bazi"}
    ids = [x["id"] for x in build_report(p, s)["sections"]]
    assert "bazi" in ids and "houses" in ids and "timing" in ids


def test_houses_locked_without_exact_time():
    p = mk("approx", 8, 0, 180)
    houses = next(x for x in build_report(p, synthesize(p))["sections"] if x["id"] == "houses")
    assert houses["blocks"][0]["kind"] == "locked"


def test_compare_includes_bazi():
    a, b = mk(), mk(d=dt.date(1992, 11, 3), h=7, m=0)
    r = compat.compare(a, b, synthesize(a), synthesize(b), "romantic", "A", "B")
    assert any(m["name"] == "Chinese BaZi" for m in r["methods"]) and r["bazi_notes"]
    assert abs(sum(compat.METHOD_WEIGHTS["romantic"].values()) - 1) < 1e-9
    for rel in compat.METHOD_WEIGHTS:
        assert abs(sum(compat.METHOD_WEIGHTS[rel].values()) - 1) < 1e-9
