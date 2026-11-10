"""Regenerates engine/baseline.json: the average per-trait vote of each system over a large
random sample of charts. Run after changing sign/number/nakshatra trait mappings or weights.

    python tools/calibrate.py
"""
import datetime as dt
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from content.traits import TRAIT_KEYS  # noqa: E402
from engine.profile import Birth, build  # noqa: E402
from engine import synthesis as S  # noqa: E402

random.seed(12345)
SYL = ["an", "ra", "mi", "ka", "so", "li", "ve", "tu", "ni", "sha", "dev", "pri", "ja", "ro", "el", "da", "ma", "bi", "ch", "ar", "yu", "ho"]


def rname():
    return " ".join("".join(random.choice(SYL) for _ in range(random.randint(2, 4))).title() for _ in range(random.randint(2, 3)))


N = 500
acc = {s: {d: [0.0] * len(TRAIT_KEYS) for d in S.DOMAINS} for s in S.SYSTEMS}
for _ in range(N):
    d = dt.date(1940, 1, 1) + dt.timedelta(days=random.randint(0, 30000))
    b = Birth(rname(), d, "exact", random.randint(0, 23), random.randint(0, 59), tz="UTC",
              lat=random.uniform(-55, 62), lon=random.uniform(-150, 150))
    syn = S.synthesize(build(b, dt.date(2026, 11, 10)), calibrate=False)
    for sy in S.SYSTEMS:
        for dom in S.DOMAINS:
            for i, v in enumerate(syn["_norm"][sy][dom]):
                acc[sy][dom][i] += v / N
json.dump({sy: {d: [round(x, 4) for x in v] for d, v in dm.items()} for sy, dm in acc.items()},
          open(Path(__file__).resolve().parent.parent / "engine" / "baseline.json", "w"), indent=0)
print("baseline written from", N, "charts")
