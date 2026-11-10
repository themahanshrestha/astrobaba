"""Creates dist/astrobaba-local.zip: the app folder plus an offline preview page, ready to unzip and run.

    python tools/package.py
"""
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "dist"}
OUT.mkdir(exist_ok=True)
preview = OUT / "AstroBaba-preview.html"
subprocess.run([sys.executable, str(ROOT / "tools" / "build_demo.py"), str(preview)], check=True, cwd=ROOT)
zpath = OUT / "astrobaba-local.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_dir() or SKIP_DIRS & set(rel.parts) or p.suffix == ".pyc":
            continue
        info = zipfile.ZipInfo(f"astrobaba/{rel.as_posix()}")
        info.external_attr = (0o755 if p.name == "start.sh" else 0o644) << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, p.read_bytes())
    z.write(preview, "astrobaba/AstroBaba-preview.html")
    z.writestr("astrobaba/START-HERE.txt", """AstroBaba

1. Needs Python 3.10 or newer (python.org).
2. Mac / Linux:  open a terminal in this folder and run   ./start.sh
   Windows:      double-click start.bat
3. Your browser opens at http://localhost:8000. The first run takes about a minute to set up.

AstroBaba-preview.html opens in any browser with no setup and shows three sample people.
Your birth details stay in your browser; nothing is stored on a server.
""")
print("wrote", zpath, zpath.stat().st_size // 1024, "KB")


# ---- Hugging Face Spaces bundle: files at the zip root, README with Space metadata --------------
HF_README = """---
title: AstroBaba
emoji: ✨
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 8000
pinned: false
license: agpl-3.0
---

# AstroBaba

Western astrology, Vedic astrology, Chinese BaZi and numerology read side by side. For
self-reflection and entertainment. Birth details are kept only in your browser.
"""
hf = OUT / "astrobaba-huggingface.zip"
with zipfile.ZipFile(hf, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_dir() or SKIP_DIRS & set(rel.parts) or p.suffix == ".pyc" or rel.parts[0] in ("tests",) \
                or rel.name in ("start.sh", "start.bat", "netlify.toml", "render.yaml", "README.md"):
            continue
        z.write(p, rel.as_posix())
    z.writestr("README.md", HF_README)
print("wrote", hf, hf.stat().st_size // 1024, "KB")
