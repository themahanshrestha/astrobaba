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


# ---- Hugging Face Spaces bundle (Gradio SDK, which is free; runs our FastAPI app via app.py) ----
HF_README = """---
title: AstroBaba
emoji: ✨
colorFrom: purple
colorTo: pink
sdk: gradio
app_file: app.py
pinned: false
license: agpl-3.0
---

# AstroBaba

Western astrology, Vedic astrology, Chinese BaZi and numerology read side by side. For
self-reflection and entertainment. Birth details are kept only in your browser.
"""
HF_APP = """# Hugging Face Spaces entry point: serves the AstroBaba web app and API on the Space's port.
import os

import uvicorn

from api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
"""
HF_REQ = "pyswisseph\ntzdata\npydantic>=2\n"   # gradio (installed by the Space) provides fastapi and uvicorn
SKIP_NAMES = {"start.sh", "start.bat", "netlify.toml", "render.yaml", "README.md", "Dockerfile", ".dockerignore",
              "requirements.txt", "pythonanywhere_wsgi.py", "DEPLOY.md", "PLAN.md"}
hf = OUT / "astrobaba-huggingface.zip"
with zipfile.ZipFile(hf, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if p.is_dir() or SKIP_DIRS & set(rel.parts) or p.suffix == ".pyc" or rel.parts[0] in ("tests", "tools") \
                or rel.name in SKIP_NAMES:
            continue
        z.write(p, rel.as_posix())
    z.writestr("README.md", HF_README)
    z.writestr("app.py", HF_APP)
    z.writestr("requirements.txt", HF_REQ)
print("wrote", hf, hf.stat().st_size // 1024, "KB")
