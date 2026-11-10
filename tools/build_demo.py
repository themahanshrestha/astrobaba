"""Builds a single-file, read-only preview of the web app with precomputed sample profiles.

    python tools/build_demo.py OUTPUT.html

The preview runs the real front end; only the API is replaced by embedded JSON, so new profiles
cannot be created in it. Use it for sharing a look at the app without hosting the Python backend.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient  # noqa: E402
from api.main import app  # noqa: E402

KTM = dict(lat=27.7172, lon=85.324, tz="Asia/Kathmandu", place="Kathmandu, Nepal", current_name=None, window_min=150)
SAMPLES = [
    dict(id="demo1", name="Asha Rai", date="1990-05-17", time_mode="exact", time="12:15", **KTM),
    dict(id="demo2", name="Rohan Karki", date="1992-11-03", time_mode="approx", time="07:00", **KTM),
    dict(id="demo3", name="Mira Thapa", date="1995-03-08", time_mode="unknown", time=None, **KTM),
]
RELS = ["romantic", "business", "family", "friends"]


def inp(s):
    return {k: v for k, v in s.items() if k != "id"}


def main(out):
    c = TestClient(app)
    profiles, compares = {}, {}
    for s in SAMPLES:
        r = c.post("/api/profile", json=inp(s)); r.raise_for_status()
        profiles[f"{s['name']}|{s['date']}|{s['time_mode']}"] = r.json()
    a, b = SAMPLES[0], SAMPLES[1]
    for rel in RELS:
        r = c.post("/api/compare", json={"a": inp(a), "b": inp(b), "relation": rel}); r.raise_for_status()
        compares[f"{a['name']}|{b['name']}|{rel}"] = r.json()
    data = json.dumps({"profiles": profiles, "compares": compares, "samples": [{"id": s["id"], "input": inp(s)} for s in SAMPLES]},
                      separators=(",", ":")).replace("<", "\\u003c")

    css = (ROOT / "web" / "style.css").read_text()
    js = (ROOT / "web" / "app.js").read_text()
    # route without touching location.hash (artifacts only allow plain #name hashes)
    js = js.replace("location.hash", "DEMO.hash")
    js = js.replace('window.addEventListener("hashchange", route);', "")
    js = js.replace('history.replaceState(null, "", `#/p/${id}/${t}`);', "DEMO._h = `#/p/${id}/${t}`;")
    js = js.replace('let profiles = loadProfiles();', "let profiles = DEMO_DATA.samples.map((s) => ({ ...s, summary: '' }));")
    js = js.replace("function saveProfiles(p) {", "function saveProfiles(p) { return; ")
    js = js.replace('<button class="btn ghost" id="print-all" type="button">Save as PDF</button>', "")
    js = js.replace('$("#print-all").onclick =', '($("#print-all") || {}).onclick =')
    js = js.replace('app.innerHTML = `<div class="card fade">${steps}${body}', 'app.innerHTML = `<div class="card fade"><div class="note" style="margin-bottom:14px"><b>Preview only.</b> You can fill this in, but this hosted preview cannot calculate new charts. Run AstroBaba on your computer to read your own.</div>${steps}${body}')
    js = js.replace('if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});', "")
    js = js.replace('fetch("/api/health").catch(() => {});', "")
    shim = """
const DEMO_DATA = JSON.parse(document.getElementById('demo-data').textContent);
const DEMO = { _h: "#/", get hash() { return this._h; }, set hash(v) { this._h = v || "#/"; setTimeout(route, 0); } };
const _json = (o, status = 200) => Promise.resolve(new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json" } }));
window.fetch = (url, opts) => {
  const u = String(url);
  if (!u.startsWith("/api/")) return Promise.reject(new Error("offline preview"));
  const body = opts && opts.body ? JSON.parse(opts.body) : null;
  if (u === "/api/profile" && body) {
    const d = DEMO_DATA.profiles[`${body.name}|${body.date}|${body.time_mode}`];
    return d ? _json(d) : _json({ detail: "This hosted preview only contains three sample people. Run AstroBaba on your own computer to read your own chart." }, 503);
  }
  if (u === "/api/compare" && body) {
    const d = DEMO_DATA.compares[`${body.a.name}|${body.b.name}|${body.relation}`];
    return d ? _json(d) : _json({ detail: "In this preview, compare Asha Rai with Rohan Karki." }, 503);
  }
  if (u.startsWith("/api/places")) return _json({ results: [] });
  if (u.startsWith("/api/timezones")) return _json({ timezones: ["Asia/Kathmandu"] });
  return _json({ ok: true });
};
document.addEventListener("click", (e) => { const a = e.target.closest('a[href^="#"]'); if (a) { e.preventDefault(); DEMO.hash = a.getAttribute("href"); } });
"""
    html = f"""<title>AstroBaba</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<style>
{css}
:root{{color-scheme:light}}
.shell{{max-width:860px;margin:0 auto;padding-left:max(var(--gut),env(safe-area-inset-left,0px));padding-right:max(var(--gut),env(safe-area-inset-right,0px))}}
.top{{max-width:none;margin:0;padding:16px 0 8px}} main{{max-width:none;padding:8px 0 40px}} .foot{{max-width:none;padding:10px 0 100px}}
.bottom-nav{{padding-left:max(8px,env(safe-area-inset-left,0px));padding-right:max(8px,env(safe-area-inset-right,0px))}}
.demo-note{{background:var(--lav);border-radius:16px;padding:10px 14px;margin:6px 0 4px;font-size:.88rem}}
.skip{{display:none}}
</style>
<div class="shell">
<header class="top">
  <a class="brand" href="#/" aria-label="AstroBaba home"><span class="brand-star" aria-hidden="true">✦</span> AstroBaba</a>
  <nav class="top-nav" aria-label="Main">
    <a href="#/" data-nav="home">Profiles</a>
    <a href="#/compare" data-nav="compare">Compare</a>
    <a href="#/new" class="btn small" data-nav="new">New profile</a>
  </nav>
</header>
<div class="demo-note"><b>Preview.</b> Three fictional sample people, calculated by the real engine. Creating new profiles needs the app running on your own computer.</div>
<main id="app" tabindex="-1"></main>
<footer class="foot"><p id="disclaimer"></p></footer>
</div>
<nav class="bottom-nav" aria-label="Main (mobile)">
  <a href="#/" data-nav="home"><span aria-hidden="true">☉</span>Profiles</a>
  <a href="#/compare" data-nav="compare"><span aria-hidden="true">♡</span>Compare</a>
</nav>
<script type="application/json" id="demo-data">{data}</script>
<script>
{shim}
{js}
</script>
"""
    Path(out).write_text(html)
    print("wrote", out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
