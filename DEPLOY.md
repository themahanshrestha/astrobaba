# Hosting AstroBaba

**Netlify alone cannot run this app.** The calculations need Python and a compiled astronomy
library (Swiss Ephemeris); Netlify Functions run JavaScript/TypeScript/Go. So the backend goes on a
Python host, and Netlify can optionally serve the front end in front of it.

## Option A (simplest): everything on Render

1. Push this repo to GitHub (already done for this branch).
2. Render dashboard > New > Blueprint > choose the repo. `render.yaml` and `Dockerfile` do the rest.
3. When the build finishes you get `https://astrobaba-xxxx.onrender.com`. That is the full app.

The free plan sleeps after inactivity, so the first request after a pause is slow.

## Option B: Netlify front end + Render backend

1. Do Option A first and copy your Render URL.
2. In `netlify.toml`, replace `https://YOUR-BACKEND.onrender.com` with that URL and commit.
3. Netlify dashboard > Add new site > Import from Git > pick the repo. `netlify.toml` sets the
   publish folder (`web`) and proxies `/api/*` to Render, so the browser only talks to Netlify.

## Option C: Hugging Face Spaces (Docker SDK is paid on some accounts; skip if so)

1. Sign up at huggingface.co (email only).
2. New > Space > SDK **Docker** > Blank > pick Public (free) > Create.
3. Run `python tools/package.py`, unzip `dist/astrobaba-huggingface.zip`, then in the Space open
   Files > Add file > Upload files and drag in everything from the unzipped folder.
4. The Space builds from the `Dockerfile` (a few minutes). Free Spaces sleep when idle.

## Option D: a temporary public link to the copy on your own computer (no account)

Start the app locally (`./start.sh`), then in another terminal run
`cloudflared tunnel --url http://localhost:8000` and share the `trycloudflare.com` address it prints.
It works only while your computer and the app are running.

## Option E: PythonAnywhere free plan (no card)

Gives `https://YOURUSERNAME.pythonanywhere.com`. The free plan has a small daily CPU allowance, which is
plenty for personal use, and the app does not sleep.

1. Sign up at pythonanywhere.com (Beginner plan is free, no card).
2. Open a **Bash console** and run (replace nothing if the repo is public; otherwise upload
   `astrobaba-local.zip` on the Files tab and `unzip` it instead):
   ```
   git clone -b claude/stoic-goodall-al5pgm https://github.com/themahanshrestha/astrobaba.git
   mkvirtualenv --python=python3.12 astro
   pip install "setuptools<70" wheel
   pip install --no-build-isolation pyswisseph
   pip install fastapi a2wsgi tzdata
   ```
3. **Web** tab > Add a new web app > Manual configuration > Python 3.12.
4. Set **Virtualenv** to `/home/YOURUSERNAME/.virtualenvs/astro`.
5. Click the **WSGI configuration file** link, delete its contents, paste the contents of
   `pythonanywhere_wsgi.py`, and change `YOURUSERNAME`.
6. Click **Reload**, then open `https://YOURUSERNAME.pythonanywhere.com`.

Free accounts can only reach an allowlist of sites. Place search inside the app uses the browser, not the
server, so it still works, and the app falls back to its built-in city list.

## Before sharing the link with other people

- **Swiss Ephemeris licence:** AGPL. A public, closed-source or paid service needs the commercial licence.
- **Privacy:** birth data passes through your servers when computed (it is not stored). Add a short
  privacy notice. The app stores profiles only in the visitor's browser.
- **Access:** anyone with the link can use it. Add a password at the host if you want it private.
