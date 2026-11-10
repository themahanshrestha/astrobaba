"""Builds self-contained AstroBaba pages from the web/ and js/ sources.

    python tools/build_offline.py            -> dist/astrobaba-offline.html  (double-click to open, no internet or server)
                                                site/index.html              (drop the site/ folder on any static host, e.g. Netlify)
    python tools/build_offline.py --artifact PATH   -> variant for the Claude artifact viewer (no print, no service worker,
                                                       plain-hash routing)
Run `python tools/build_js_data.py` first if the Python content or tables changed."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS = ["astronomy.min.js", "data.js", "ephem.js", "engine.js", "profile.js", "report.js", "compat.js", "api.js"]


def read(p):
    return (ROOT / p).read_text()


def body_scripts():
    return "\n".join(f"<script>/* {n} */\n{read('js/' + n)}\n</script>" for n in JS)


def page(variant):
    css, app = read("web/style.css"), read("web/app.js")
    head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>AstroBaba</title>
<meta name="description" content="Western astrology, Vedic astrology, Chinese BaZi and numerology read side by side.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">"""
    if variant == "artifact":
        shim = """const DEMO = { _h: "#/", get hash() { return this._h; }, set hash(v) { this._h = v || "#/"; setTimeout(route, 0); } };
document.addEventListener("click", (e) => { const a = e.target.closest('a[href^="#"]'); if (a) { e.preventDefault(); DEMO.hash = a.getAttribute("href"); } });
window.__NO_SW = true;"""
        app = app.replace("location.hash", "DEMO.hash").replace('window.addEventListener("hashchange", route);', "")
        app = app.replace('history.replaceState(null, "", `#/p/${id}/${t}`);', "DEMO._h = `#/p/${id}/${t}`;")
        app = app.replace('<button class="btn ghost" id="print-all" type="button">Save as PDF</button>', "")
        app = app.replace('$("#print-all").onclick =', '($("#print-all") || {}).onclick =')
        css += """
:root{color-scheme:light}
.shell{max-width:860px;margin:0 auto;padding-left:max(var(--gut),env(safe-area-inset-left,0px));padding-right:max(var(--gut),env(safe-area-inset-right,0px))}
.top{max-width:none;margin:0;padding:16px 0 8px} main{max-width:none;padding:8px 0 40px} .foot{max-width:none;padding:10px 0 100px}
.bottom-nav{padding-left:max(8px,env(safe-area-inset-left,0px));padding-right:max(8px,env(safe-area-inset-right,0px))} .skip{display:none}"""
        head = head.replace('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n', "")
        head = '<meta name="claude:viewport-fit-sides" content="cover">\n' + head
        markup = """<div class="shell">
<header class="top"><a class="brand" href="#/" aria-label="AstroBaba home"><span class="brand-star" aria-hidden="true">✦</span> AstroBaba</a>
<nav class="top-nav" aria-label="Main"><a href="#/" data-nav="home">Profiles</a><a href="#/compare" data-nav="compare">Compare</a><a href="#/new" class="btn small" data-nav="new">New profile</a></nav></header>
<main id="app" tabindex="-1"></main>
<footer class="foot"><p id="disclaimer"></p><p>Your birth details are saved only in this browser. Everything is calculated on your device.</p></footer></div>
<nav class="bottom-nav" aria-label="Main (mobile)"><a href="#/" data-nav="home"><span aria-hidden="true">☉</span>Profiles</a><a href="#/new" data-nav="new"><span aria-hidden="true">＋</span>New</a><a href="#/compare" data-nav="compare"><span aria-hidden="true">♡</span>Compare</a></nav>"""
        return f"{head}\n<style>\n{css}\n</style>\n{markup}\n{body_scripts()}\n<script>\n{shim}\n{app}\n</script>\n"
    markup = (ROOT / "web" / "index.html").read_text()
    m = re.search(r"<body>(.*?)<script src", markup, re.S)
    markup = m.group(1).replace("Place suggestions come from the free Open-Meteo geocoding service.", "Everything is calculated on your device; place suggestions use the free Open-Meteo service when online, with a built-in city list offline.")
    return f"""<!doctype html>
<html lang="en">
<head>
{head}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ccircle cx='32' cy='32' r='30' fill='%23e7dff5'/%3E%3Cpath d='M32 12l5 15 15 5-15 5-5 15-5-15-15-5 15-5z' fill='%238e7cc3'/%3E%3C/svg%3E">
<style>
{css}
</style>
</head>
<body>
{markup}
{body_scripts()}
<script>
{app}
</script>
</body>
</html>
"""


def main(argv):
    if argv and argv[0] == "--artifact":
        Path(argv[1]).write_text(page("artifact")); print("wrote", argv[1]); return
    out = ROOT / "dist"; out.mkdir(exist_ok=True)
    html = page("full")
    (out / "astrobaba-offline.html").write_text(html)
    (ROOT / "site").mkdir(exist_ok=True)
    (ROOT / "site" / "index.html").write_text(html)
    print("wrote dist/astrobaba-offline.html and site/index.html", len(html) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1:])
