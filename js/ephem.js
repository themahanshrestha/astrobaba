/* Astronomy layer: planet positions, sidereal zodiac (Lahiri), nodes, ascendant and houses.
   Uses astronomy-engine (MIT) for bodies; Placidus houses and ayanamsa are implemented here. */
(function (root) {
  const A = root.Astronomy || (typeof require !== "undefined" ? require("./astronomy_node.js") : null);
  const D2R = Math.PI / 180, R2D = 180 / Math.PI;
  const norm = (x) => ((x % 360) + 360) % 360;
  const BODY = { Sun: "Sun", Moon: "Moon", Mercury: "Mercury", Venus: "Venus", Mars: "Mars", Jupiter: "Jupiter", Saturn: "Saturn", Uranus: "Uranus", Neptune: "Neptune", Pluto: "Pluto" };

  const jdUT = (d) => d.getTime() / 86400000 + 2440587.5;

  function tropLon(name, date) {
    const t = A.MakeTime(date);
    const v = name === "Moon" ? A.GeoMoon(t) : A.GeoVector(A.Body[name], t, true);
    const e = A.RotateVector(A.Rotation_EQJ_ECT(t), v);
    return norm(A.SphereFromVector(e).lon);
  }
  function tropLonSpeed(name, date) {
    const l = tropLon(name, date);
    const l2 = tropLon(name, new Date(date.getTime() + 3600000));
    let d = l2 - l; if (d > 180) d -= 360; if (d < -180) d += 360;
    return { lon: l, speed: d * 24 };
  }

  // Lahiri ayanamsa: value at J2000 plus general precession in longitude (IAU 2006 polynomial).
  const LAHIRI_J2000 = 23.857104;   // calibrated against Swiss Ephemeris (tools/check_ephem.js)
  function ayanamsa(jd) {
    const T = (jd - 2451545.0) / 36525;
    return LAHIRI_J2000 + (5028.796195 * T + 1.1054348 * T * T) / 3600;
  }

  function meanNode(jd) {
    const T = (jd - 2451545.0) / 36525;
    return norm(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + (T * T * T) / 467441 - (T * T * T * T) / 60616000);
  }
  // "True" node = osculating node of the Moon's instantaneous orbit (as Swiss Ephemeris does).
  function trueNode(jd) {
    const date = new Date((jd - 2440587.5) * 86400000);
    const vec = (dt) => {
      const t = A.MakeTime(new Date(date.getTime() + dt * 86400000));
      return A.RotateVector(A.Rotation_EQJ_ECT(t), A.GeoMoon(t));
    };
    const h = 0.02, p1 = vec(-h), p2 = vec(h), r = vec(0);
    const v = { x: (p2.x - p1.x) / (2 * h), y: (p2.y - p1.y) / (2 * h), z: (p2.z - p1.z) / (2 * h) };
    const hx = r.y * v.z - r.z * v.y, hy = r.z * v.x - r.x * v.z;
    return norm(Math.atan2(hx, -hy) * R2D);
  }

  function obliquity(jd) {   // true obliquity of the ecliptic (degrees)
    const T = (jd - 2451545.0) / 36525;
    const eps0 = 23.4392911 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T * T * T;
    const om = (125.04452 - 1934.136261 * T) * D2R;
    const L = (280.4665 + 36000.7698 * T) * D2R, Lm = (218.3165 + 481267.8813 * T) * D2R;
    const dEps = (9.20 * Math.cos(om) + 0.57 * Math.cos(2 * L) + 0.10 * Math.cos(2 * Lm) - 0.09 * Math.cos(2 * om)) / 3600;
    return eps0 + dEps;
  }
  function ramc(date, lon) {   // right ascension of the Midheaven (degrees)
    const gast = A.SiderealTime(A.MakeTime(date));   // apparent sidereal time, hours
    return norm(gast * 15 + lon);
  }
  function ascMc(date, lat, lon) {
    const jd = jdUT(date), eps = obliquity(jd) * D2R, th = ramc(date, lon) * D2R, ph = lat * D2R;
    const mc = norm(Math.atan2(Math.sin(th), Math.cos(th) * Math.cos(eps)) * R2D);
    let asc = norm(Math.atan2(Math.cos(th), -(Math.sin(th) * Math.cos(eps) + Math.tan(ph) * Math.sin(eps))) * R2D);
    // The Ascendant is the eastern horizon point, 0-180 degrees ahead of the Midheaven. Inside the polar
    // circles the formula can return the western point, so flip it (as Swiss Ephemeris does).
    if (norm(asc - mc) > 180) asc = norm(asc + 180);
    return { asc, mc, ramc: th * R2D, eps: eps * R2D };
  }

  function placidusCusps(date, lat, lon) {
    const { asc, mc, ramc: R, eps } = ascMc(date, lat, lon);
    const e = eps * D2R, ph = lat * D2R;
    if (Math.abs(lat) >= 90 - eps - 0.0001) return null;          // circumpolar: Placidus undefined
    function cusp(offset, mode, frac) {
      let lam = Math.atan2(Math.sin((R + offset) * D2R), Math.cos((R + offset) * D2R) * Math.cos(e));
      for (let i = 0; i < 40; i++) {
        const dec = Math.asin(Math.sin(e) * Math.sin(lam));
        const x = -Math.tan(ph) * Math.tan(dec);
        if (Math.abs(x) >= 1) return null;
        const dsa = Math.acos(x) * R2D, nsa = 180 - dsa;
        const ra = mode === "d" ? R + frac * dsa : R + 180 - frac * nsa;
        const nl = Math.atan2(Math.sin(ra * D2R), Math.cos(ra * D2R) * Math.cos(e));
        if (Math.abs(nl - lam) < 1e-10) { lam = nl; break; }
        lam = nl;
      }
      return norm(lam * R2D);
    }
    const c11 = cusp(30, "d", 1 / 3), c12 = cusp(60, "d", 2 / 3), c2 = cusp(120, "n", 2 / 3), c3 = cusp(150, "n", 1 / 3);
    if ([c11, c12, c2, c3].some((x) => x === null)) return null;
    const c = [asc, c2, c3, norm(mc + 180), norm(c11 + 180), norm(c12 + 180), norm(asc + 180), norm(c2 + 180), norm(c3 + 180), mc, c11, c12];
    return c;
  }
  function porphyryCusps(date, lat, lon) {   // fallback inside the polar circles
    const { asc, mc } = ascMc(date, lat, lon), ic = norm(mc + 180), dsc = norm(asc + 180);
    const q1 = norm(asc - mc) / 3, q2 = norm(ic - asc) / 3, q3 = norm(dsc - ic) / 3, q4 = norm(mc - dsc) / 3;
    return [asc, norm(asc + q2), norm(asc + 2 * q2), ic, norm(ic + q3), norm(ic + 2 * q3), dsc, norm(dsc + q4), norm(dsc + 2 * q4), mc, norm(mc + q1), norm(mc + 2 * q1)];
  }
  function houses(date, lat, lon) {
    const am = ascMc(date, lat, lon);
    let cusps = placidusCusps(date, lat, lon);
    if (!cusps) cusps = porphyryCusps(date, lat, lon);
    return { cusps, asc: am.asc, mc: am.mc };
  }

  function sidAscendant(date, lat, lon) {
    return norm(ascMc(date, lat, lon).asc - ayanamsa(jdUT(date)));
  }

  root.Ephem = { jdUT, tropLon, tropLonSpeed, ayanamsa, meanNode, trueNode, houses, ascMc, sidAscendant, norm, BODY };
  if (typeof module !== "undefined") module.exports = root.Ephem;
})(typeof window !== "undefined" ? window : globalThis);
