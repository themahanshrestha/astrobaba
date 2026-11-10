@echo off
rem AstroBaba launcher for Windows. Needs Python 3.10+ (python.org) and, for the first run,
rem the "Desktop development with C++" build tools if no prebuilt astronomy wheel is available.
cd /d "%~dp0"
if not exist .venv (
  echo First run: setting up, this takes a minute...
  python -m venv .venv || (echo Python 3.10+ is required. Install it from python.org & pause & exit /b 1)
  call .venv\Scripts\activate.bat
  pip install --quiet --upgrade pip
  pip install --quiet "setuptools<70" wheel
  pip install --quiet --no-build-isolation pyswisseph || (echo Could not build the astronomy library. Install Microsoft C++ Build Tools, then run again. & rmdir /s /q .venv & pause & exit /b 1)
  pip install --quiet fastapi "uvicorn[standard]" tzdata
) else (
  call .venv\Scripts\activate.bat
)
start "" http://localhost:8000
echo AstroBaba is running at http://localhost:8000 (close this window to stop)
uvicorn api.main:app --port 8000
