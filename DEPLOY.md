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

## Option C: free, no card: Hugging Face Spaces

1. Sign up at huggingface.co (email only).
2. New > Space > SDK **Docker** > Blank > pick Public (free) > Create.
3. Run `python tools/package.py`, unzip `dist/astrobaba-huggingface.zip`, then in the Space open
   Files > Add file > Upload files and drag in everything from the unzipped folder.
4. The Space builds from the `Dockerfile` (a few minutes). Free Spaces sleep when idle.

## Option D: a temporary public link to the copy on your own computer (no account)

Start the app locally (`./start.sh`), then in another terminal run
`cloudflared tunnel --url http://localhost:8000` and share the `trycloudflare.com` address it prints.
It works only while your computer and the app are running.

## Before sharing the link with other people

- **Swiss Ephemeris licence:** AGPL. A public, closed-source or paid service needs the commercial licence.
- **Privacy:** birth data passes through your servers when computed (it is not stored). Add a short
  privacy notice. The app stores profiles only in the visitor's browser.
- **Access:** anyone with the link can use it. Add a password at the host if you want it private.
