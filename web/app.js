/* AstroBaba front end: dependency-free, mobile-first. */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const app = $("#app");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const SIGN_G = Object.fromEntries(Object.entries({ Aries: "♈", Taurus: "♉", Gemini: "♊", Cancer: "♋", Leo: "♌", Virgo: "♍", Libra: "♎", Scorpio: "♏", Sagittarius: "♐", Capricorn: "♑", Aquarius: "♒", Pisces: "♓" }).map(([k, v]) => [k, v + "\uFE0E"])); // FE0E: force text (not emoji) glyphs
const SIGNS = Object.keys(SIGN_G);
const PLANET_G = { Sun: "☉", Moon: "☽", Mercury: "☿", Venus: "♀", Mars: "♂", Jupiter: "♃", Saturn: "♄", Uranus: "♅", Neptune: "♆", Pluto: "♇", "North Node": "☊", "South Node": "☋", Rahu: "☊", Ketu: "☋" };
const ABBR = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke" };
const EL_COLOR = { fire: "#fadde4", earth: "#dcf0e6", air: "#dcebf7", water: "#e7dff5" };
const EL = ["fire", "earth", "air", "water"];
const DASHA_COLOR = { Sun: "#fde6d5", Moon: "#dcebf7", Mars: "#fadde4", Rahu: "#e7dff5", Jupiter: "#fbf1cc", Saturn: "#dcebf7", Mercury: "#dcf0e6", Ketu: "#e7dff5", Venus: "#fadde4" };
const TINTS = ["lav", "blush", "mint", "peach", "sky", "butter"];
const TAB_ICON = { overview: "☉", strengths: "✦", watchouts: "◈", inner: "☽", mind: "☿", career: "✧", hobbies: "❀", relationships: "♡", wellbeing: "❁", purpose: "➶", timing: "◷", numbers: "№", charts: "◎", agreement: "⚖" };

/* ---------- storage ---------- */
const KEY = "astrobaba.profiles.v1";
function loadProfiles() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } }
function saveProfiles(p) { try { localStorage.setItem(KEY, JSON.stringify(p)); } catch { /* storage unavailable: fine */ } }
let profiles = loadProfiles();
const cache = new Map();
const uid = () => Math.random().toString(36).slice(2, 10);

async function api(path, body) {
  const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : undefined);
  if (!r.ok) {
    let m = "Something went wrong.";
    try { const j = await r.json(); m = typeof j.detail === "string" ? j.detail : (j.detail || []).map((d) => d.msg).join("; ") || m; } catch { /* ignore */ }
    throw new Error(m);
  }
  return r.json();
}
async function getProfile(p) {
  const k = JSON.stringify(p.input);
  if (!cache.has(k)) cache.set(k, await api("/api/profile", p.input));
  return cache.get(k);
}

/* ---------- router ---------- */
function route() {
  const h = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  document.querySelectorAll("[data-nav]").forEach((a) => a.classList.toggle("active", a.dataset.nav === (h[0] === "p" || !h[0] ? "home" : h[0])));
  window.scrollTo(0, 0);
  if (!h[0]) return viewHome();
  if (h[0] === "new") return viewNew();
  if (h[0] === "p") return viewProfile(h[1], h[2]);
  if (h[0] === "compare") return viewCompare();
  location.hash = "#/";
}
window.addEventListener("hashchange", route);

/* ---------- home ---------- */
function viewHome() {
  const list = profiles.length ? `
    <h2>Your profiles</h2>
    <div class="plist">${profiles.map((p, i) => `
      <div class="card pcard fade tint-${TINTS[i % TINTS.length]}">
        <h3>${esc(p.input.name || "Unnamed")}</h3>
        <div class="meta">${esc(p.input.date)} · ${esc(p.input.place || p.input.tz)}</div>
        <div class="meta">${p.summary ? esc(p.summary) : ""}</div>
        <div class="row"><a class="btn small" href="#/p/${p.id}">Open</a><button class="btn small danger" data-del="${p.id}">Remove</button></div>
      </div>`).join("")}</div>
    <p><a class="btn" href="#/new">Add another person</a></p>` : "";
  app.innerHTML = `
    <section class="hero fade">
      <h1>Know yourself, from every angle.</h1>
      <p>Western astrology, Vedic astrology and numerology, read side by side. See where they agree, where they differ, and what it means for your character, work, hobbies and relationships.</p>
      ${profiles.length ? "" : '<a class="btn" href="#/new">Create your profile</a>'}
    </section>
    ${list}
    <section class="pillars">
      <div class="card tint-sky"><span class="glyph">☉</span><h3>Western</h3><p class="small">Tropical zodiac: Sun, Moon, Rising and the planets, with aspects and house emphasis.</p></div>
      <div class="card tint-peach"><span class="glyph">☽</span><h3>Vedic</h3><p class="small">Sidereal zodiac: Moon sign, 27 nakshatras, Lagna, yogas and your current Vimshottari period.</p></div>
      <div class="card tint-mint"><span class="glyph">№</span><h3>Numerology</h3><p class="small">Life Path, Expression, Soul Urge, cycles and pinnacles (Pythagorean and Chaldean).</p></div>
    </section>
    <div class="card tint-butter"><b>How it works.</b> Each system votes on a shared set of traits. Where all three agree, the theme is strong. Where they differ, we show you the difference instead of hiding it. Every statement has a "Why this?" so you can see where it came from.</div>`;
  app.querySelectorAll("[data-del]").forEach((b) => b.onclick = () => {
    if (confirm("Remove this profile from this device?")) { profiles = profiles.filter((p) => p.id !== b.dataset.del); saveProfiles(profiles); viewHome(); }
  });
}

/* ---------- new profile form ---------- */
const DAYPARTS = [["Early morning", "05:30", 90, "about 4–7am"], ["Morning", "09:30", 150, "about 7am–12pm"], ["Afternoon", "14:30", 150, "about 12–5pm"], ["Evening", "19:00", 120, "about 5–9pm"], ["Night", "00:30", 210, "about 9pm–4am"]];
let form;
function freshForm(over = {}) { return { step: 0, name: "", current_name: "", date: "", mode: "exact", time: "", dp: 1, window: 120, place: null, manual: false, ...over }; }

function viewNew() {
  form = form || freshForm();
  renderForm();
}
function renderForm() {
  const f = form, s = f.step, N = 4;
  const steps = `<div class="steps" aria-hidden="true">${Array.from({ length: N }, (_, i) => `<i class="${i <= s ? "on" : ""}"></i>`).join("")}</div>`;
  let body = "";
  if (s === 0) body = `
    <h2>Who is this for?</h2>
    <div class="field"><label for="f-name">Full name at birth</label><input id="f-name" type="text" autocomplete="off" value="${esc(f.name)}" placeholder="e.g. Maya Devi Sharma">
      <p class="hint">Used for numerology. Use the name as written on your birth certificate, including middle names.</p></div>
    <div class="field"><label for="f-cur">Name you use now <span class="muted">(optional)</span></label><input id="f-cur" type="text" value="${esc(f.current_name)}" placeholder="If different from your birth name"></div>`;
  if (s === 1) body = `
    <h2>When were you born?</h2>
    <div class="field"><label for="f-date">Date of birth</label><input id="f-date" type="date" value="${esc(f.date)}" max="${new Date().toISOString().slice(0, 10)}"></div>`;
  if (s === 2) body = `
    <h2>Do you know your birth time?</h2>
    <p class="muted">Time unlocks your Rising sign, Lagna and houses. It's fine if you don't know it: we'll tell you exactly what's affected.</p>
    <div class="choice" role="radiogroup">
      <label><input type="radio" name="mode" value="exact" ${f.mode === "exact" ? "checked" : ""}><span><b>I know it</b>From a birth certificate or family record.</span></label>
      <label><input type="radio" name="mode" value="approx" ${f.mode === "approx" ? "checked" : ""}><span><b>Roughly</b>"Around sunrise" or "in the evening" is plenty.</span></label>
      <label><input type="radio" name="mode" value="unknown" ${f.mode === "unknown" ? "checked" : ""}><span><b>I don't know</b>We'll use everything that doesn't depend on time.</span></label>
    </div>
    <div id="time-extra" style="margin-top:16px"></div>`;
  if (s === 3) body = `
    <h2>Where were you born?</h2>
    <div class="field"><label for="f-place">City or town</label><input id="f-place" type="text" autocomplete="off" placeholder="Start typing…" value="${esc(f.place ? f.place.label : "")}">
      <ul class="results" id="place-results" hidden></ul>
      ${f.place ? `<div class="picked">📍 ${esc(f.place.label)} <span class="muted small">(${f.place.lat.toFixed(2)}, ${f.place.lon.toFixed(2)} · ${esc(f.place.tz)})</span></div>` : ""}
      <p class="hint">Can't find it? <a href="#" id="manual-toggle">Enter coordinates manually</a>.</p></div>
    <div id="manual" ${f.manual ? "" : "hidden"}>
      <div class="field"><label for="m-lat">Latitude</label><input id="m-lat" type="number" step="0.0001" placeholder="27.7172"></div>
      <div class="field"><label for="m-lon">Longitude</label><input id="m-lon" type="number" step="0.0001" placeholder="85.3240"></div>
      <div class="field"><label for="m-tz">Time zone</label><select id="m-tz"><option value="">Loading…</option></select></div>
      <button class="btn small ghost" id="m-use" type="button">Use these</button>
    </div>`;
  app.innerHTML = `<div class="card fade">${steps}${body}<div id="form-err"></div>
    <div class="row" style="margin-top:8px;justify-content:space-between">
      <button class="btn ghost" id="back" ${s === 0 ? "disabled" : ""}>Back</button>
      <button class="btn" id="next">${s === N - 1 ? "Create profile" : "Continue"}</button></div></div>`;
  wireForm();
}
function wireForm() {
  const f = form, s = f.step;
  const err = (m) => { $("#form-err").innerHTML = m ? `<div class="err" role="alert">${esc(m)}</div>` : ""; };
  $("#back").onclick = () => { collect(); f.step = Math.max(0, f.step - 1); renderForm(); };
  function collect() {
    if (s === 0) { f.name = $("#f-name").value; f.current_name = $("#f-cur").value; }
    if (s === 1) f.date = $("#f-date").value;
    if (s === 2) { const r = document.querySelector("input[name=mode]:checked"); if (r) f.mode = r.value; const t = $("#f-time"); if (t) f.time = t.value; const w = $("#f-win"); if (w) f.window = +w.value; }
  }
  if (s === 2) {
    const draw = () => {
      const m = document.querySelector("input[name=mode]:checked")?.value || f.mode; f.mode = m;
      const el = $("#time-extra");
      if (m === "exact") el.innerHTML = `<div class="field"><label for="f-time">Time of birth</label><input id="f-time" type="time" value="${esc(f.time)}"><p class="hint">Local time at the place of birth. Use 24-hour or the picker, whichever you prefer.</p></div>`;
      else if (m === "approx") el.innerHTML = `<label>Roughly when?</label><div class="chips" role="radiogroup">${DAYPARTS.map((d, i) => `<button type="button" class="chip ${f.dp === i ? "on" : ""}" data-dp="${i}" title="${d[3]}">${d[0]}<span class="muted small"> · ${d[3]}</span></button>`).join("")}</div>
        <p class="hint">Or enter a best-guess time and how far off it could be:</p>
        <div class="row"><input id="f-time" type="time" value="${esc(f.time)}" style="max-width:150px"><span>±</span><select id="f-win" style="max-width:140px">${[30, 60, 120, 180, 240, 360].map((v) => `<option value="${v}" ${f.window === v ? "selected" : ""}>${v >= 60 ? v / 60 + " h" : v + " min"}</option>`).join("")}</select></div>`;
      else el.innerHTML = `<div class="note">No problem. Rising sign, Lagna and houses will be left out, and we'll show how likely each Moon sign and nakshatra is across the day.</div>`;
      el.querySelectorAll("[data-dp]").forEach((b) => b.onclick = () => { f.dp = +b.dataset.dp; f.time = ""; el.querySelectorAll("[data-dp]").forEach((x) => x.classList.toggle("on", x === b)); const t = $("#f-time"); if (t) t.value = ""; });
    };
    document.querySelectorAll("input[name=mode]").forEach((r) => r.onchange = draw); draw();
  }
  if (s === 3) wirePlace(err);
  $("#next").onclick = async () => {
    collect(); err("");
    if (s === 0 && !f.name.trim()) return err("Please enter your name. Numerology needs it.");
    if (s === 1 && !f.date) return err("Please choose a date of birth.");
    if (s === 2 && f.mode === "exact" && !f.time) return err("Enter your birth time, or choose 'Roughly' or 'I don't know'.");
    if (s === 3) {
      if (!f.place) return err("Choose a place from the list, or enter coordinates.");
      return submitForm(err);
    }
    f.step++; renderForm();
  };
}
function wirePlace(err) {
  const inp = $("#f-place"), res = $("#place-results");
  let t;
  inp.oninput = () => { clearTimeout(t); t = setTimeout(() => searchPlace(inp.value), 250); };
  async function searchPlace(q) {
    if (q.trim().length < 2) { res.hidden = true; return; }
    let out = [];
    try {
      const ctl = new AbortController(); const to = setTimeout(() => ctl.abort(), 3500);
      const r = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&count=6&language=en&format=json`, { signal: ctl.signal });
      clearTimeout(to);
      const j = await r.json();
      out = (j.results || []).map((x) => ({ label: [x.name, x.admin1, x.country].filter(Boolean).join(", "), lat: x.latitude, lon: x.longitude, tz: x.timezone }));
    } catch { /* offline or blocked: use built-in list */ }
    if (!out.length) {
      try { const j = await api("/api/places?q=" + encodeURIComponent(q)); out = j.results.map((x) => ({ label: `${x.name}, ${x.country}`, lat: x.lat, lon: x.lon, tz: x.tz })); } catch { /* ignore */ }
    }
    res.hidden = !out.length;
    res.innerHTML = out.map((o, i) => `<li><button type="button" data-i="${i}">${esc(o.label)}</button></li>`).join("");
    res.querySelectorAll("button").forEach((b) => b.onclick = () => { form.place = out[+b.dataset.i]; renderForm(); });
  }
  const loadTz = async () => {
    try { const j = await api("/api/timezones"); $("#m-tz").innerHTML = '<option value="">Choose…</option>' + j.timezones.map((z) => `<option>${esc(z)}</option>`).join(""); } catch { /* ignore */ }
  };
  $("#manual-toggle").onclick = (e) => {
    e.preventDefault(); form.manual = !form.manual; $("#manual").hidden = !form.manual;
    if (form.manual) loadTz();
  };
  if (form.manual) loadTz();
  $("#m-use").onclick = () => {
    const lat = parseFloat($("#m-lat").value), lon = parseFloat($("#m-lon").value), tz = $("#m-tz").value;
    if (isNaN(lat) || isNaN(lon) || !tz) return err("Enter latitude, longitude and a time zone.");
    form.place = { label: `${lat.toFixed(2)}, ${lon.toFixed(2)}`, lat, lon, tz }; renderForm();
  };
}
function inputFromForm(f) {
  let time = null, mode = f.mode, win = 120;
  if (mode === "exact") time = f.time;
  if (mode === "approx") {
    if (f.time) { time = f.time; win = f.window; } else { const d = DAYPARTS[f.dp]; time = d[1]; win = d[2]; }
  }
  return { name: f.name.trim(), current_name: f.current_name.trim() || null, date: f.date, time_mode: mode, time, window_min: win,
    lat: f.place.lat, lon: f.place.lon, tz: f.place.tz, place: f.place.label };
}
async function submitForm(err) {
  const input = inputFromForm(form);
  $("#next").disabled = true; $("#next").innerHTML = '<span class="spin"></span> Reading the sky…';
  try {
    const data = await api("/api/profile", input);
    const p = { id: uid(), input, summary: summaryOf(data) };
    cache.set(JSON.stringify(input), data);
    profiles.push(p); saveProfiles(profiles); form = null;
    location.hash = "#/p/" + p.id;
  } catch (e) { err(e.message); $("#next").disabled = false; $("#next").textContent = "Create profile"; }
}
function summaryOf(d) {
  const s = d.report.snapshot; return `☉ ${s.sun_western.sign} · ☽ ${s.moon_vedic.sign} (Vedic) · Life Path ${s.life_path}`;
}

/* ---------- profile ---------- */
const TAB_ORDER = ["overview", "strengths", "watchouts", "inner", "mind", "career", "hobbies", "relationships", "wellbeing", "purpose", "timing", "numbers", "charts", "agreement"];
async function viewProfile(id, tab = "overview") {
  const p = profiles.find((x) => x.id === id);
  if (!p) { location.hash = "#/"; return; }
  app.innerHTML = `<div class="card"><span class="spin"></span> Reading the sky…</div>`;
  let d;
  try { d = await getProfile(p); } catch (e) { app.innerHTML = `<div class="err" role="alert">${esc(e.message)}</div><a class="btn" href="#/">Back</a>`; return; }
  if (!p.summary) { p.summary = summaryOf(d); saveProfiles(profiles); }
  $("#disclaimer").textContent = d.report.disclaimer;
  const secs = Object.fromEntries(d.report.sections.map((s) => [s.id, s]));
  const titles = { ...Object.fromEntries(d.report.sections.map((s) => [s.id, s.title])), numbers: "Your numbers", charts: "Charts", agreement: "Where systems agree" };
  const snap = d.report.snapshot, meta = d.profile.meta;
  const sn = (lab, main, sub, tint) => `<div style="background:var(--${tint})"><small>${lab}</small><b>${main}</b><span>${sub || ""}</span></div>`;
  const g = (s) => s ? `${SIGN_G[s]} ${s}` : "–";
  const maybe = (o) => o && o.prob < 0.9 ? " (likely)" : "";
  const notes = d.profile.notes || [];
  app.innerHTML = `<div class="fade">
    <h1 style="margin-bottom:.1em">${esc(meta.name || "Your profile")}</h1>
    <p class="muted">${esc(meta.date)} · ${esc(meta.place || meta.tz)} · ${meta.time_mode === "exact" ? "time " + esc(meta.time) : meta.time_mode === "approx" ? "approximate time" : "time unknown"}</p>
    <div class="snap">
      ${sn("Sun · Western", g(snap.sun_western.sign), "tropical", "sky")}
      ${sn("Moon · Western", g(snap.moon_western.sign) + maybe(snap.moon_western), "tropical", "lav")}
      ${sn("Rising · Western", snap.rising_western ? g(snap.rising_western.sign) + maybe(snap.rising_western) : "needs time", "", "blush")}
      ${sn("Moon · Vedic", g(snap.moon_vedic.sign), snap.moon_vedic.nakshatra + " · pada " + snap.moon_vedic.pada, "peach")}
      ${sn("Lagna · Vedic", snap.lagna_vedic ? g(snap.lagna_vedic.sign) + maybe(snap.lagna_vedic) : "needs time", "", "butter")}
      ${sn("Life Path", snap.life_path, "", "mint")}
    </div>
    ${notes.length ? `<div class="banner"><b>About your birth data</b><ul>${notes.map((n) => `<li>${esc(n)}</li>`).join("")}</ul></div>` : ""}
    <div class="tabs" role="tablist" aria-label="Report sections">${TAB_ORDER.map((t) => `<button role="tab" id="tab-${t}" aria-selected="${t === tab}" data-tab="${t}">${TAB_ICON[t]} ${esc(titles[t])}</button>`).join("")}</div>
    <section id="panel" role="tabpanel" aria-live="polite"></section>
    <div class="row" style="margin-top:20px"><a class="btn" href="#/compare">Compare with someone</a></div>
  </div>`;
  const panel = $("#panel");
  const show = (t) => {
    tab = t;
    document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === t));
    panel.innerHTML = `<div class="fade"><h2>${esc(titles[t])}</h2>${t === "numbers" ? numbersPanel(d) : t === "charts" ? chartsPanel(d) : t === "agreement" ? agreementPanel(d) : secs[t].blocks.map((b, i) => blockHtml(b, meta, i)).join("")}</div>`;
    history.replaceState(null, "", `#/p/${id}/${t}`);
    const btn = $(`#tab-${t}`); btn && btn.scrollIntoView({ inline: "center", block: "nearest" });
  };
  document.querySelectorAll(".tabs button").forEach((b) => b.onclick = () => { show(b.dataset.tab); window.scrollTo({ top: $(".tabs").offsetTop - 4, behavior: "smooth" }); });
  show(TAB_ORDER.includes(tab) ? tab : "overview");
}

function why(src) {
  if (!src || !src.length) return "";
  return `<details class="why"><summary>Why this?</summary><ul>${src.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></details>`;
}
function blockHtml(b, meta, i) {
  const badge = b.time && meta.time_mode !== "exact" ? `<span class="badge">depends on birth time</span>` : "";
  if (b.kind === "locked") return `<div class="locked"><h3>${esc(b.h)}</h3><p>🔒 ${esc(b.text)}</p></div>`;
  if (b.kind === "note") return `<div class="note">${esc(b.text)}</div>`;
  let inner = "";
  if (b.kind === "traits") inner = b.items.map((t) => `<div class="trait"><h4>${esc(t.name)}</h4><div>${esc(t.tag)}</div><div class="lvl">${esc(t.level_label)}</div>${sysBars(t.per_system)}</div>`).join("");
  else if (b.kind === "views") inner = `<div class="views">${b.items.map((v) => `<div class="v"><b>${esc(v.label)}</b>${esc(v.text)}</div>`).join("")}</div>`;
  else if (b.kind === "list") inner = `<div class="list">${b.items.map((v) => `<p class="item">${v.label ? `<b>${esc(v.label)}.</b> ` : ""}${esc(v.text)}</p>`).join("")}</div>`;
  else inner = `<p>${esc(b.text)}</p>`;
  return `<div class="card block${b.kind === "traits" ? " tint-lav" : ""}"><h3>${esc(b.h)}${badge}</h3>${inner}${why(b.src)}</div>`;
}
function sysBars(ps) {
  const row = (lab, v, cls) => `<span>${lab}</span><div class="bar" title="${lab}: ${v}"><i class="${cls}" style="width:${Math.min(100, v / 3 * 100)}%"></i></div>`;
  return `<div class="bars" aria-label="Strength of this theme in each system">${row("Western", ps.western, "b-w")}${row("Vedic", ps.vedic, "b-v")}${row("Numerology", ps.numerology, "b-n")}</div>`;
}

/* numbers */
function numbersPanel(d) {
  const n = d.profile.numerology, ni = d.numbers_info;
  const sys = n.pythagorean ? ["pythagorean", "chaldean"] : [];
  const cell = (lab, v, tint) => v == null ? "" : `<div class="num" style="background:var(--${tint})"><b>${v}</b><small>${lab}</small><small>${esc(ni[v]?.title || "")}</small></div>`;
  const P = n.pythagorean, C = n.chaldean;
  let html = `<div class="card"><h3>Core numbers (Pythagorean)</h3><div class="numgrid">
    ${cell("Life Path", n.life_path.number, "mint")}${cell("Expression", P?.expression, "lav")}${cell("Soul Urge", P?.soul_urge, "blush")}
    ${cell("Personality", P?.personality, "sky")}${cell("Birthday", n.birthday, "peach")}${cell("Maturity", n.maturity, "butter")}</div>
    <p class="hint">Master numbers 11, 22 and 33 are kept unreduced. Y counts as a vowel only when a name has no other vowel.</p></div>`;
  if (C) html += `<div class="card"><h3>Chaldean comparison</h3><p class="small muted">The older Chaldean system numbers letters differently, so your name numbers can differ. Both are shown so you can see which feels truer.</p>
    <table><tr><th></th><th>Pythagorean</th><th>Chaldean</th></tr>
    <tr><td>Expression</td><td>${P.expression}</td><td>${C.expression}</td></tr><tr><td>Soul Urge</td><td>${P.soul_urge}</td><td>${C.soul_urge}</td></tr>
    <tr><td>Personality</td><td>${P.personality}</td><td>${C.personality}</td></tr></table></div>`;
  if (n.current_name) html += `<div class="card"><h3>Your current name</h3><p class="small muted">The name you use now carries its own vibration, alongside your birth name.</p><div class="numgrid">${cell("Expression", n.current_name.expression, "lav")}${cell("Soul Urge", n.current_name.soul_urge, "blush")}${cell("Personality", n.current_name.personality, "sky")}</div></div>`;
  html += `<div class="card"><h3>Right now</h3><div class="numgrid">${cell("Personal Year", n.personal.year, "mint")}${cell("Personal Month", n.personal.month, "peach")}${cell("Personal Day", n.personal.day, "sky")}</div></div>`;
  const cy = n.cycles;
  html += `<div class="card"><h3>Life chapters (pinnacles) and challenges</h3><div class="scroll-x"><table><tr><th>Chapter</th><th>Ages</th><th>Number</th><th>Challenge</th></tr>
    ${cy.pinnacles.map((p, i) => `<tr><td>${i + 1}</td><td>${p.from}–${p.to ?? "onward"}</td><td>${p.n} · ${esc(ni[p.n]?.title || "")}</td><td>${cy.challenges[i]}</td></tr>`).join("")}</table></div></div>`;
  if (n.missing && n.missing.length) html += `<div class="card"><h3>Missing numbers in your name</h3><p>${n.missing.join(", ")}. These point to qualities you may need to build deliberately: ${n.missing.map((m) => esc(ni[m].title.toLowerCase())).join(", ")}.</p></div>`;
  if (n.karmic_debts.length) html += `<div class="card tint-butter"><h3>Karmic debt numbers</h3>${n.karmic_debts.map((k) => `<p>${esc(d.karmic[k])}</p>`).join("")}</div>`;
  return html;
}

/* charts */
function chartsPanel(d) {
  const w = d.profile.western, v = d.profile.vedic, meta = d.profile.meta, dist = d.profile.dist;
  const exact = meta.time_mode === "exact";
  let html = `<div class="charts"><div class="card"><h3>Western wheel</h3>${wheel(w, exact)}<p class="hint">${exact ? "Placidus houses, Rising sign on the left." : "No houses without an exact time."}</p></div>
    <div class="card"><h3>Vedic chart (South Indian)</h3>${southIndian(v, exact)}<p class="hint">${esc(v.ayanamsa_name)} sidereal zodiac${exact ? ". Asc marks the Lagna." : "; Lagna needs an exact time."}</p></div></div>`;
  const rows = (pl, ved) => Object.entries(pl).map(([k, p]) => `<tr><td>${PLANET_G[k] || ""} ${k}</td><td>${SIGN_G[p.sign]} ${p.sign} ${p.deg}${p.retro && !k.includes("Node") && k !== "Rahu" && k !== "Ketu" ? " ℞" : ""}</td>${ved ? `<td>${esc(p.nakshatra)} ${p.pada}</td><td>${SIGN_G[p.navamsa]} ${p.navamsa}</td>` : ""}<td>${p.house ?? "–"}</td></tr>`).join("");
  html += `<div class="card"><h3>Western positions</h3><div class="scroll-x"><table><tr><th>Body</th><th>Sign</th><th>House</th></tr>${rows(w.planets, false)}</table></div></div>`;
  html += `<div class="card"><h3>Vedic positions</h3><div class="scroll-x"><table><tr><th>Graha</th><th>Sign</th><th>Nakshatra</th><th>Navamsa</th><th>House</th></tr>${rows(v.planets, true)}</table></div>
    ${v.yogas.length ? `<p class="small" style="margin-top:10px"><b>Yogas:</b> ${v.yogas.join(", ")}</p>` : ""}</div>`;
  if (w.aspects.length) html += `<div class="card"><h3>Main aspects</h3><div class="scroll-x"><table><tr><th>Between</th><th>Aspect</th><th>Orb</th></tr>${w.aspects.slice(0, 12).map((a) => `<tr><td>${esc(a.a)} – ${esc(a.b)}</td><td>${a.type}</td><td>${a.orb}°</td></tr>`).join("")}</table></div></div>`;
  html += dashaPanel(d.profile.dasha);
  return html;
}
function polar(cx, cy, r, ang) { const a = ang * Math.PI / 180; return [cx + r * Math.cos(a), cy - r * Math.sin(a)]; }
function wheel(w, exact) {
  const C = 170, asc = exact ? w.asc.lon : 0;
  const ang = (L) => 180 + (L - asc);
  let s = `<svg viewBox="0 0 340 340" role="img" aria-label="Western birth chart wheel">`;
  for (let i = 0; i < 12; i++) {
    const a0 = ang(i * 30), a1 = ang(i * 30 + 30), el = EL[i % 4];
    const p = [polar(C, C, 160, a0), polar(C, C, 160, a1), polar(C, C, 124, a1), polar(C, C, 124, a0)];
    s += `<path d="M${p[0]} A160 160 0 0 0 ${p[1]} L${p[2]} A124 124 0 0 1 ${p[3]}Z" fill="${EL_COLOR[el]}" stroke="#fff" stroke-width="1.5"/>`;
    const m = polar(C, C, 142, ang(i * 30 + 15)); s += `<text x="${m[0]}" y="${m[1]}" text-anchor="middle" dominant-baseline="central" font-size="16" fill="#6b6382">${SIGN_G[SIGNS[i]]}</text>`;
  }
  s += `<circle cx="${C}" cy="${C}" r="124" fill="#fff" stroke="#ebe4f1"/><circle cx="${C}" cy="${C}" r="60" fill="#fbf8f5" stroke="#ebe4f1"/>`;
  if (exact && w.cusps) w.cusps.forEach((c, i) => { const a = polar(C, C, 124, ang(c)), b = polar(C, C, 60, ang(c)); s += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${i % 3 === 0 ? "#8e7cc3" : "#ebe4f1"}" stroke-width="${i % 3 === 0 ? 1.6 : 1}"/>`; const t = polar(C, C, 72, ang(c) + 14); s += `<text x="${t[0]}" y="${t[1]}" font-size="9" fill="#a99fc0" text-anchor="middle" dominant-baseline="central">${i + 1}</text>`; });
  const items = Object.entries(w.planets).filter(([k]) => k !== "South Node").map(([k, p]) => [k, p.lon]).sort((a, b) => a[1] - b[1]);
  let prev = -99, lvl = 0;
  items.forEach(([k, L]) => { lvl = L - prev < 9 ? (lvl + 1) % 3 : 0; prev = L; const r = 106 - lvl * 15; const pt = polar(C, C, r, ang(L)); s += `<g><circle cx="${pt[0]}" cy="${pt[1]}" r="9" fill="#fff" stroke="#8e7cc3" stroke-width="1"/><text x="${pt[0]}" y="${pt[1]}" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#3b3350">${PLANET_G[k]}</text><title>${k} ${p_deg(w.planets[k])}</title></g>`; });
  if (exact) { const a = polar(C, C, 168, 180); s += `<text x="${a[0] - 2}" y="${a[1] - 8}" font-size="10" fill="#8e7cc3" font-weight="600">ASC</text>`; }
  return s + "</svg>";
}
const p_deg = (p) => `${p.sign} ${p.deg}`;
function southIndian(v, exact) {
  const pos = { Pisces: [0, 0], Aries: [0, 1], Taurus: [0, 2], Gemini: [0, 3], Cancer: [1, 3], Leo: [2, 3], Virgo: [3, 3], Libra: [3, 2], Scorpio: [3, 1], Sagittarius: [3, 0], Capricorn: [2, 0], Aquarius: [1, 0] };
  const cell = 80, by = {};
  Object.entries(v.planets).forEach(([k, p]) => (by[p.sign] ||= []).push(ABBR[k] + (p.retro && k !== "Rahu" && k !== "Ketu" ? "ʳ" : "")));
  let s = `<svg viewBox="0 0 320 320" role="img" aria-label="Vedic South Indian chart">`;
  Object.entries(pos).forEach(([sign, [r, c]], i) => {
    const x = c * cell, y = r * cell, isL = exact && v.lagna && v.lagna.sign === sign;
    s += `<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="${isL ? "#fbf1cc" : EL_COLOR[EL[SIGNS.indexOf(sign) % 4]]}" stroke="#fff" stroke-width="2"/>`;
    s += `<text x="${x + 6}" y="${y + 15}" font-size="11" fill="#8a82a0">${SIGN_G[sign]}</text>`;
    if (isL) s += `<text x="${x + cell - 6}" y="${y + 15}" font-size="10" text-anchor="end" fill="#8e7cc3" font-weight="600">Asc</text>`;
    const pl = by[sign] || [];
    pl.forEach((t, j) => s += `<text x="${x + 8 + (j % 2) * 34}" y="${y + 38 + Math.floor(j / 2) * 16}" font-size="13" fill="#3b3350">${t}</text>`);
  });
  s += `<text x="160" y="152" text-anchor="middle" font-family="Cormorant Garamond, serif" font-size="20" fill="#8e7cc3">Rāśi</text><text x="160" y="176" text-anchor="middle" font-size="11" fill="#a99fc0">Lahiri</text></svg>`;
  return s;
}
function dashaPanel(ds) {
  const tl = ds.timeline, cur = ds.current;
  if (!tl.length) return "";
  const t0 = new Date(tl[0].start).getTime(), t1 = new Date(tl[tl.length - 1].end).getTime();
  const now = Date.now();
  const segs = tl.map((p) => { const a = Math.max(new Date(p.start).getTime(), t0), b = new Date(p.end).getTime(); const isNow = cur && p.lord === cur.maha && p.start.slice(0, 4) === cur.maha_start.slice(0, 4); return `<div class="${isNow ? "now" : ""}" style="flex:${(b - a) / (t1 - t0)};background:${DASHA_COLOR[p.lord]}" title="${p.lord}: ${p.start.slice(0, 4)}–${p.end.slice(0, 4)}">${p.lord.slice(0, 2)}</div>`; }).join("");
  return `<div class="card"><h3>Vimshottari timeline</h3><div class="dasha">${segs}</div>
    <p class="hint">Each block is a planetary period (Maha Dasha), in order of your life. ${cur ? `You are in <b>${esc(cur.maha)}</b> until ${esc(cur.maha_end)}, within <b>${esc(cur.antar || "")}</b> until ${esc(cur.antar_end || "")}.` : ""} ${ds.uncertain ? "Dates are approximate because your birth time is not exact." : ""}</p></div>`;
}

/* agreement */
const DOM_TITLE = { character: "Character", career: "Career", relationships: "Relationships" };
function agreementPanel(d) {
  const snap = d.report.snapshot;
  let html = `<div class="card"><h3>Western and Vedic, side by side</h3>
    <p class="small muted">The Western (tropical) and Vedic (sidereal) zodiacs are offset by about 24°, so the same planet often falls in a different sign. Both are valid frames; where they agree, the signal is stronger.</p>
    <table><tr><th></th><th>Western</th><th>Vedic</th><th></th></tr>
    <tr><td>Sun</td><td>${SIGN_G[snap.sun_western.sign]} ${snap.sun_western.sign}</td><td>${SIGN_G[snap.sun_vedic.sign]} ${snap.sun_vedic.sign}</td><td>${snap.sun_western.sign === snap.sun_vedic.sign ? "✓ agree" : ""}</td></tr>
    <tr><td>Moon</td><td>${SIGN_G[snap.moon_western.sign]} ${snap.moon_western.sign}</td><td>${SIGN_G[snap.moon_vedic.sign]} ${snap.moon_vedic.sign}</td><td>${snap.moon_western.sign === snap.moon_vedic.sign ? "✓ agree" : ""}</td></tr>
    <tr><td>Rising / Lagna</td><td>${snap.rising_western ? SIGN_G[snap.rising_western.sign] + " " + snap.rising_western.sign : "–"}</td><td>${snap.lagna_vedic ? SIGN_G[snap.lagna_vedic.sign] + " " + snap.lagna_vedic.sign : "–"}</td><td>${snap.rising_western && snap.lagna_vedic && snap.rising_western.sign === snap.lagna_vedic.sign ? "✓ agree" : ""}</td></tr></table></div>`;
  html += d.consensus.map((c) => `<div class="card"><h3>${DOM_TITLE[c.domain]}: your strongest themes</h3>
    ${c.rows.slice(0, 5).map((r) => `<div class="trait"><h4>${esc(r.title)}</h4><div class="lvl">${r.level === "strong" ? "All three systems agree" : r.level === "supported" ? "Two systems agree" : "One system emphasises this"}</div>${sysBars(r.per_system)}</div>`).join("")}</div>`).join("");
  if (d.disagreements.length) html += `<div class="card tint-butter"><h3>Where your systems pull apart</h3><p class="small">These are not errors. They show different sides of you: one tradition emphasises a trait the other barely touches.</p>
    ${d.disagreements.map((x) => `<p><b>${esc(x.title)}</b>: strongest in ${x.high}, quiet in ${x.low}.</p>`).join("")}</div>`;
  html += `<div class="note">Bars show how strongly each system points to a theme compared with the average person (the full bar is about three times average). Scores come from ${d.signal_count} placements and numbers.</div>`;
  return html;
}

/* ---------- compare ---------- */
let cmp = { a: "", b: "", rel: "romantic" };
const RELS = [["romantic", "Romantic"], ["business", "Business"], ["family", "Family"], ["friends", "Friends"]];
function viewCompare() {
  if (profiles.length < 2) {
    app.innerHTML = `<div class="card fade"><h2>Compare two people</h2><p>You need at least two saved profiles to compare. ${profiles.length ? "You have one so far." : ""} Add the other person with their birth details. Only add someone if they're comfortable with it.</p><a class="btn" href="#/new">Add a profile</a></div>`;
    return;
  }
  cmp.a ||= profiles[0].id; cmp.b ||= profiles.find((p) => p.id !== cmp.a).id;
  const opt = (sel) => profiles.map((p) => `<option value="${p.id}" ${p.id === sel ? "selected" : ""}>${esc(p.input.name)}</option>`).join("");
  app.innerHTML = `<div class="fade"><h1>Compare</h1>
    <div class="card"><div class="field"><label for="c-a">Person one</label><select id="c-a">${opt(cmp.a)}</select></div>
    <div class="field"><label for="c-b">Person two</label><select id="c-b">${opt(cmp.b)}</select></div>
    <label>What kind of relationship?</label><div class="chips" id="c-rel">${RELS.map(([k, v]) => `<button class="chip ${cmp.rel === k ? "on" : ""}" data-r="${k}">${v}</button>`).join("")}</div>
    <p style="margin-top:16px"><button class="btn" id="c-go">See compatibility</button> <a class="btn ghost" href="#/new">Add someone</a></p></div>
    <div id="c-out"></div></div>`;
  $("#c-a").onchange = (e) => cmp.a = e.target.value; $("#c-b").onchange = (e) => cmp.b = e.target.value;
  document.querySelectorAll("#c-rel .chip").forEach((b) => b.onclick = () => { cmp.rel = b.dataset.r; document.querySelectorAll("#c-rel .chip").forEach((x) => x.classList.toggle("on", x === b)); });
  $("#c-go").onclick = runCompare;
}
async function runCompare() {
  const out = $("#c-out");
  if (cmp.a === cmp.b) { out.innerHTML = `<div class="err" role="alert">Choose two different people.</div>`; return; }
  out.innerHTML = `<div class="card"><span class="spin"></span> Comparing charts…</div>`;
  const A = profiles.find((p) => p.id === cmp.a), B = profiles.find((p) => p.id === cmp.b);
  try {
    const r = await api("/api/compare", { a: A.input, b: B.input, relation: cmp.rel });
    out.innerHTML = compareHtml(r); out.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) { out.innerHTML = `<div class="err" role="alert">${esc(e.message)}</div>`; }
}
function compareHtml(r) {
  const [a, b] = r.names;
  return `<div class="fade"><div class="card tint-lav"><h2>${esc(a)} & ${esc(b)} · ${esc(r.relation_label)}</h2>
    <div class="score"><div class="ring" style="--p:${r.overall}"><span>${r.overall}</span></div><div><b>${esc(r.summary)}</b><p class="small muted" style="margin:.3em 0 0">A blend of four independent views. It is a conversation starter, not a verdict.</p></div></div></div>
    <div class="card"><h3>How each method sees it</h3>${r.methods.map((m) => `<div><b>${esc(m.name)}</b> <span class="muted">${m.score}/100</span><div class="meter"><i style="width:${m.score}%"></i></div><p class="hint" style="margin-top:-4px">${esc(m.how)}</p></div>`).join("")}
      ${r.friction_systems.map((x) => `<div class="note">${esc(x)}</div>`).join("")}</div>
    <div class="card"><h3>Dimension by dimension</h3>${r.dimensions.map((x) => `<div><b>${esc(x.title)}</b> <span class="muted">${x.score}</span><div class="meter"><i style="width:${x.score}%"></i></div><p class="small">${esc(x.text)}</p></div>`).join("")}</div>
    ${r.shared.length ? `<div class="card tint-mint"><h3>What you share</h3>${r.shared.map((s) => `<p><b>${esc(s.title)}.</b> ${esc(s.text)}</p>`).join("")}</div>` : ""}
    ${r.complement.length ? `<div class="card tint-sky"><h3>What each brings</h3>${r.complement.map((s) => `<p><b>${esc(s.who)}</b>: ${esc(s.title)}. Brings ${esc(s.text)}.</p>`).join("")}</div>` : ""}
    ${r.friction.length ? `<div class="card tint-blush"><h3>Where friction can show up</h3>${r.friction.map((f) => `<p>${esc(f.text)}</p>`).join("")}</div>` : ""}
    <div class="card"><h3>Vedic Guna Milan: ${r.ashtakoota.total}/36</h3><p class="small muted">${esc(a)}: ${esc(r.ashtakoota.moon_a)} · ${esc(b)}: ${esc(r.ashtakoota.moon_b)}</p>
      <div class="scroll-x"><table><tr><th>Koota</th><th>Score</th><th>Meaning</th></tr>${r.ashtakoota.kootas.map((k) => `<tr><td>${k.name}</td><td>${k.score}/${k.max}</td><td>${esc(k.meaning)}</td></tr>`).join("")}</table></div></div>
    <div class="card"><h3>Numerology</h3>${r.numerology_notes.map((n) => `<p>${esc(n)}</p>`).join("")}</div>
    <div class="card tint-butter"><h3>Making it work</h3><ul>${r.tips.map((t) => `<li>${esc(t)}</li>`).join("")}</ul></div></div>`;
}

if (!location.hash) location.hash = "#/";
fetch("/api/health").catch(() => {});
route();
