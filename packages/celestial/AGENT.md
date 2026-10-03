# AGENT.md: sunholo/celestial

## When to use

Use this package when you need where a planet or moon is, how fast it moves,
or which way its pole points, on a real date, with numbers you can cite:
- Solving Kepler's equation and turning orbital elements into position and
  velocity (`kepler`).
- Heliocentric planet positions from the JPL approximate elements, 3000 BC to
  3000 AD, and a labelled mean orbit beyond (`ephemeris`).
- Planetocentric moon positions from JPL mean satellite elements (`ephemeris`).
- The Earth's centre and the Moon, split out of Standish's Earth-Moon
  barycentre (`earthAt`, `moonAt`, `earthMoonSplit` in `ephemeris`).
- Rotating ecliptic vectors into ICRS or galactic coordinates, and IAU poles
  and prime meridians (`frames`).
- Where a moving body is *seen*: the light-travel (retarded) time and
  position (`lighttime`).
- The Newtonian gravity at a point, e.g. what a drive must cancel to hold a
  line or a station near planets (`gravity`).
- How bright a planet, moon or ring is in reflected starlight: per-pixel
  radiance (Lambert, Minnaert, ring single scattering) and disc-integrated
  illuminance at the observer (`reflect`, `rings`).

It is pure: no effects, deterministic, and the same bits on the bytecode VM
(`--strict-bytecode`) and the interpreter. It depends on no other package.

Do NOT use it for:
- Precision ephemerides. Standish's approximate elements carry errors of
  arc-seconds to tens of arc-minutes depending on the planet and the epoch
  (the JPL page lists them); dates of oppositions and equinoxes come out
  within a few days. Use a JPL DE file through Horizons/SPICE when that is
  not enough.
- N-body integration, perturbations beyond the published mean rates,
  hyperbolic or parabolic orbits (e must be in [0, 1)).
- Relativity: that is `sunholo/relativity`; the two never import each other.
  Aberration, Doppler and the star's photometry (illuminanceFromV) live
  there; pass their results in as numbers.
- Precise gravity (no J2 oblateness, no 1PN), multiple scattering in rings
  or atmospheres, or measured phase curves (Mallama & Hilton 2018 polynomials):
  the photometry here is the Minnaert-sphere model.

## Units and conventions

- **AU, days (TDB), radians**, float64. Satellite inputs take `a` in km; every
  output is AU and AU/day. `auKm()` = 149,597,870.7 km.
- **Time is a Julian Date in TDB.** `julianDate(year, month, dayFraction)`
  is Meeus eq. 7.1 on the proleptic Gregorian calendar with astronomical
  years (1 BC = 0): `julianDate(2000, 1, 1.5)` = 2451545.0 = J2000. For the
  game's ±2-day checks TT, TDB and UT are interchangeable; they are not for
  anything finer.
- **Frames.** Planet and satellite states are ecliptic J2000 (mean ecliptic
  and equinox of J2000). `frames` rotates to ICRS (equatorial) and galactic.
  Poles from `poleAndSpin` are unit vectors in ecliptic J2000.
- **Angles in records are radians.** The JPL tables are in degrees (and
  degrees per century, or per day). Convert once in your data.
- **Gravity mixes units on purpose:** positions in AU (the ephemeris's),
  GM in km^3/s^2 and radii in km (as IAU and JPL tabulate them), the
  acceleration out in **m/s^2**.
- **Photometry:** pass the star's illuminance at 1 AU in lux and radiance
  comes back in cd/m^2, illuminance in lux. Phase angles are radians in
  [0, pi]; mu, mu0, cosI, cosE are cosines (for rings, |sin| of the
  elevation over the ring plane).
- `Orbit.gm` is the effective n^2 a^3 that makes the velocity follow the
  mean motion actually used, not a physical GM. `elementsAt` and
  `satelliteElementsAt` set it for you.

## Quick start

```ailang
import pkg/sunholo/celestial/kepler (Orbit, State, solveKepler, stateFromElements)
import pkg/sunholo/celestial/ephemeris (MeanElements, ElementRates, SatElements, elementsAt, planetAt, satelliteAt, julianDate, earthAt, moonAt)
import pkg/sunholo/celestial/frames (PoleModel, eclipticToGalactic, poleAndSpin, lonLat)
import pkg/sunholo/celestial/lighttime (retarded, secondsPerDay)
import pkg/sunholo/celestial/gravity (GravBody, accelerationAt, gmEarthNominal, radiusEarthNominal)
import pkg/sunholo/celestial/reflect (discIlluminance, minnaertRadiance, rhoFromGeometricAlbedo)
import pkg/sunholo/celestial/rings (ringLitRadiance, ringTransmission)

pure func rad(d: float) -> float = d * 3.141592653589793 / 180.0

-- Jupiter, Standish Table 2a (J2000 values) and its rates per century + Table 2b:
let jupEl = { a: 5.20248019, e: 0.04853590, incl: rad(1.29861416), meanLong: rad(34.33479152),
              longPeri: rad(14.27495244), node: rad(100.29282654) };
let jupRt = { a: -0.00002864, e: 0.00018026, incl: rad(-0.00322699), meanLong: rad(3034.90371757),
              longPeri: rad(0.18199196), node: rad(0.13024619),
              b: rad(-0.00012452), c: rad(0.06064060), s: rad(-0.35635438), f: rad(38.35125000) };
let jd = julianDate(2023, 11, 3.0);
let s = planetAt(jupEl, jupRt, jd);          -- s.pos (AU), s.vel (AU/day), ecliptic J2000
let flag = elementsAt(jupEl, jupRt, jd).meanOrbit   -- false inside 3000 BC-3000 AD
let g = eclipticToGalactic(s.pos);           -- the same vector in the galactic frame

-- The Earth's centre, not the EMB (moonEl: JPL's Moon mean elements, see
-- "Earth and Moon" below); ~4,700 km apart:
let earth = earthAt(embEl, embRt, moonEl, jd)   -- heliocentric State
let moon = moonAt(embEl, embRt, moonEl, jd)

-- Where Jupiter is seen from the Earth-Moon barycentre (light left ~33 min ago);
-- embEl/embRt are the EMB's Table 2a row, built like Jupiter's:
let seen = retarded(\t. planetAt(jupEl, jupRt, t).pos, planetAt(embEl, embRt, jd).pos, jd);
-- seen.pos, seen.lagDays * secondsPerDay() (= 1986.4 s; Horizons: 1987.3 s)

-- Its brightness: the Sun's 1 AU illuminance comes from the caller, e.g.
-- sunholo/relativity illuminanceFromV(-26.74) = 127057.41 lux. rSunAU = |s.pos|,
-- dObsKm = |seen.pos - earth| * auKm(), phaseRad the Sun-Jupiter-observer angle.
let eJup = discIlluminance(127057.41, 0.538, 71492.0, rSunAU, dObsKm, phaseRad, 1.0)  -- lux
```

Inner planets (Mercury-Mars) have b = c = s = f = 0.

## Exported surface

| Module | Exports |
|---|---|
| `kepler` | `Vec3 {x,y,z}`, `State {pos, vel}`, `Orbit {a, e, incl, node, argPeri, meanAnom, gm}`, `Drift {a, e, incl, node, argPeri}`, `solveKepler(M, e)`, `stateFromElements(el)`, `driftingState(el, drift)`, `noDrift`, `meanMotion(gm, a)`, `period(gm, a)`, `orbitRadius(el)`, `orbitNormal(el)`, `wrapPi`, `pi`, `twoPi`, `absf`, `dot`, `norm`, `cross`, `scale`, `add`, `sub` |
| `ephemeris` | `MeanElements {a, e, incl, meanLong, longPeri, node}`, `ElementRates {a, e, incl, meanLong, longPeri, node, b, c, s, f}`, `Ephem {orbit, meanOrbit, drift}`, `elementsAt(el, rates, jd)`, `planetAt(el, rates, jd)`, `SatElements {a, e, argPeri, meanAnom, incl, node, epochJd, meanAnomRate, periRate, nodeRate, poleRa, poleDec}`, `satelliteElementsAt(s, jd)`, `satelliteAt(s, jd)`, `julianDate(y, m, d)`, `auKm`, `j2000`, `windowStartJd`, `windowEndJd`; 0.1.1: `EarthMoon {earth, moon}`, `earthMoonSplit(emb, moonGeo)`, `earthAt(embEl, embRt, moon, jd)`, `moonAt(embEl, embRt, moon, jd)`, `earthMoonMu`, `earthMoonMassRatio` |
| `lighttime` | `Retarded {time, pos, lagDays}`, `retarded(srcFn, obs, t)`, `retardedTime(srcFn, obs, t)`, `lightTimeDays(srcFn, obs, t)`, `cAuPerDay`, `secondsPerDay` |
| `gravity` | `GravBody {gm, radius, posAt}`, `Gravity {acc, inside, body}`, `accelerationAt(bodies, x, jdTDB)`, `accelerationRelativeTo(bodies, x, ref, jdTDB)`, `pointAcceleration(gm, rKm)`, `gmSunNominal`, `gmEarthNominal`, `gmJupiterNominal`, `radiusSunNominal`, `radiusEarthNominal`, `radiusJupiterNominal` |
| `reflect` | `starIlluminanceAt(e1AU, rAU)`, `lambertPhase(alpha)`, `lambertRadiance(rho, lux, cosI)`, `minnaertRadiance(rho, k, lux, cosI, cosE)`, `minnaertPhase(alpha, k)`, `phaseFunction(alpha, k)`, `rhoFromGeometricAlbedo(p, k)`, `geometricAlbedoFromRho(rho, k)`, `bondAlbedo(rho, k)`, `bondFromGeometricAlbedo(p, k)`, `discIlluminance(e1AU, p, R, rAU, d, alpha, k)` |
| `rings` | `ringLitIF`, `ringUnlitIF`, `ringLitRadiance`, `ringUnlitRadiance` (all `(w0, phaseP, tau, mu0, mu[, lux])`), `ringTransmission(tau, mu)`, `RingBand {rIn, rOut, tau, w0}`, `bandAt(bands, r)`, `RingHit {hits, radius, mu}`, `ringPlaneHit(p, dir, pole)`, `ringShadowTransmission(bands, p, sunDir, pole)` |
| `frames` | `obliquityJ2000`, `eclipticToEquatorial`, `equatorialToEcliptic`, `equatorialToGalactic`, `eclipticToGalactic`, `unitFromAngles(lon, lat)`, `LonLat {lon, lat}`, `lonLat(v)`, `PoleTerm {phase0, rate, ra, dec, w}`, `PoleModel {ra0, ra1, dec0, dec1, w0, w1, w2, terms}`, `Spin {pole, ra, dec, w}`, `poleAndSpin(model, jd)`, `rotationPeriod(model)` |

## Kepler

- `solveKepler(M, e)` runs **exactly 8 Newton steps** from E0 = M + e sin M:
  no convergence test, so the VM and the interpreter execute the same
  operations. The residual |E - e sin E - M| is below 1e-14 for |M| <= pi and
  e <= 0.97 (worst 4.4e-16 on a 98 x 4001 grid). M outside [-pi, pi) is
  reduced and the whole turns added back, so E stays on M's branch; there the
  residual is limited by the float spacing of M itself.
- `e = 0` gives `E = M` exactly (for |M| <= pi), and `orbitRadius` of a
  circular orbit is exactly `a`.
- e >= 1 is outside the contract (`requires e < 1`).

## Planets (`elementsAt`, `planetAt`)

- Standish & Williams (1992), JPL "Approximate Positions of the Planets",
  **Table 2a** (3000 BC-3000 AD) and **Table 2b** for Jupiter-Neptune:
  M = L - varpi + b T^2 + c cos(f T) + s sin(f T), omega = varpi - Omega,
  T in Julian centuries from J2000. Do not use Table 1 (1800-2050) rates with
  this function's window.
- **The window is T in [-50, +10]** (`windowStartJd()` .. `windowEndJd()`).
  Outside it, a, e, I, varpi, Omega and the b, c, s, f terms are evaluated at
  the edge (frozen), the mean longitude keeps its rate, and
  `Ephem.meanOrbit` = true. The planet still goes round on a fixed mean orbit,
  so phases advance and positions are continuous across the edge, but it is
  **not an ephemeris** any more: label it (the game shows "mean orbit").
- **`planetAt` DOES NOT CARRY THE `meanOrbit` FLAG.** It returns a bare
  `State`. Outside 3000 BC-3000 AD call `elementsAt(el, rates, jd).meanOrbit`
  as well and label the result "mean orbit"; check the window with
  `windowStartJd()` / `windowEndJd()`.
- `planetAt` velocity is the exact time derivative of its position, including
  the element drifts and the Table 2b terms (checked by central differences to
  1e-7).

## Satellites (`satelliteElementsAt`, `satelliteAt`)

- Elements are JPL SSD "Planetary Satellite Mean Elements": a (km), e,
  omega, M, i, node at `epochJd` (2451545.0 for the current tables), referred
  to the satellite's **Laplace plane**, whose ICRS pole you pass as
  `poleRa`/`poleDec`. For elements referred to the ecliptic (the Moon) pass
  the ecliptic pole: RA 270 deg, Dec 90 deg - `obliquityJ2000()`.
- **You supply signed rates** (radians/day): `meanAnomRate` = dM/dt,
  `periRate` = d(omega)/dt, `nodeRate` = d(node)/dt.
- **Trap: JPL's `P` column is not one quantity.** For the Moon it is the
  sidereal period (27.322 d), so `meanAnomRate = 2 pi/P - periRate - nodeRate`;
  for Io (JUP365) it is the anomalistic period (1.762732 d), so
  `meanAnomRate = 2 pi/P`. `P apsis` and `P node` are tabulated as positive
  magnitudes: nodes regress (negative `nodeRate`), and an apse may regress
  too: Io's does (forced by the Laplace resonance, -2 pi/1.333 yr). The tests
  pin both readings against Io's published sidereal period 1.769137786 d; the
  wrong sign gives 1.756 d.
- The output is planetocentric, ecliptic J2000, AU and AU/day; add the
  planet's heliocentric state for a heliocentric moon. Velocity includes the
  apse and node precession exactly.

## Earth and Moon (`earthMoonSplit`, `earthAt`, `moonAt`; 0.1.1)

- **Standish's "EMB" row is the Earth-Moon barycentre, not the Earth.** The
  Earth's centre is mu |r_geo| = 4,330-4,950 km from it (mu times the Moon's 356,400-406,700 km),
  on the side away from the Moon. 0.1.0 had no way to correct this; 0.1.1
  adds the split:
  Earth = EMB - mu r_geo, Moon = EMB + (1 - mu) r_geo, where r_geo is the
  geocentric Moon (`satelliteAt` with JPL's Moon elements) and
  mu = 1 / (1 + EMRAT) = 0.0121505843958292 (`earthMoonMu()`), with
  EMRAT = GM_Earth / GM_Moon = 81.3005682214972154 (`earthMoonMassRatio()`,
  JPL DE440/DE441, Park et al. 2021).
- `earthMoonSplit(emb, moonGeo)` takes any barycentre state and any
  geocentric Moon state in one frame and returns `{earth, moon}` in the
  barycentre's frame and origin. Positions and velocities split alike, so
  the velocities stay exact derivatives. moon - earth = moonGeo and
  (1 - mu) earth + mu moon = emb, to the float spacing of the barycentre's
  coordinates (1e-15 AU at 1 AU).
- `earthAt(embEl, embRt, moon, jd)` and `moonAt(...)` are the heliocentric
  Earth and Moon from Standish's EMB row and the Moon's mean elements. Like
  `planetAt` they **do not carry the `meanOrbit` flag**.
- **Accuracy.** With exact inputs the split is exact: Horizons' EMB split
  with Horizons' geocentric Moon gives Horizons' Earth to 2e-16 AU. With the
  package's inputs, the Earth-from-EMB offset is within 54, 134 and 49 km of
  DE441 on 2000-01-01.5, 2023-11-03 and 2026-01-01 (the Moon's mean elements
  omit evection and variation: 0.5-1.6 deg and 2,100-2,400 km in the Moon on those dates, so
  ~250 km at worst in the Earth). The **heliocentric** Earth is still only
  as good as Standish's EMB (3,500-12,000 km from DE441 on those dates):
  the split removes a ~4,700 km systematic offset, not Standish's error.
  For a ship 50,000 km above the Earth, place it relative to `earthAt`, not
  relative to the EMB.

## Frames

- `eclipticToEquatorial` rotates about x by the IAU 2006 obliquity at J2000,
  84381.406". `equatorialToGalactic` is the transpose of the Hipparcos
  A_G matrix (ESA SP-1200 Vol 1 eq. 1.5.11), the frame the Stapledon's Voyage
  starfield uses; its 10-digit entries realise the galactic pole to ~1e-9
  rad. The north ecliptic pole maps to (l, b) = (96.383986, 29.811439) deg.
- `lonLat(v)` returns lon in [0, 2 pi) and lat in [-pi/2, pi/2] for any
  non-zero vector.
- `poleAndSpin(model, jd)` evaluates an IAU WGCCRE 2015 model (Archinal et al.
  2018): alpha0 = ra0 + ra1 T + sum ra_k sin(theta_k), delta0 = dec0 + dec1 T
  + sum dec_k cos(theta_k), W = w0 + w1 d + w2 d^2 + sum w_k sin(theta_k), with
  theta_k = phase0 + rate d. **Rates are per day**: convert WGCCRE's
  per-century arguments (Jupiter's Ja..Je, Neptune's N) by / 36525. Models
  whose terms use other trig forms need converting to this shape first.
  `w` is wrapped into [0, 2 pi). Retrograde rotators have negative `w1`, so
  `rotationPeriod` is negative for them.

## Light time (`lighttime`)

- `retarded(srcFn, obs, t)` solves t - t_r = |obs - srcFn(t_r)| / c by a
  fixed-point iteration on the lag s = t - t_r, **exactly 4 steps** from
  s = 0. The error after k steps is (v_radial/c)^k of the lag: < 1e-15 for
  planets (v/c <= 2e-4), still 2.5e-6 at v/c = 0.04. Do not use it for
  relativistic sources.
- `obs` is the observer's position **at t** (observation time); `srcFn`
  and `obs` must share frame and origin (heliocentric ecliptic from
  `planetAt` is fine). For a moon, compose `srcFn` from the planet's and the
  moon's states.
- It iterates on the lag, not on t_r: a JD near 2.46e6 has a 40 us ulp, and
  forming t - t_r from two dates would lose that.
- Newtonian only: no Shapiro delay (< 0.1 ms), no aberration (that is the
  observer's velocity, `sunholo/relativity`).
- Standish positions give the EMB, not the geocentre; light times agree with
  JPL Horizons to 0.9 s (Jupiter 2023-11-03) and 3.0 s (Saturn 2023-08-27).
  For a geocentric observer use `earthAt` (0.1.1); the light time moves by
  at most ~0.017 s (4,950 km / c), well inside Standish's own error.

## Gravity (`gravity`)

- `accelerationAt(bodies, x, jdTDB)` sums GM_i (x_i - x) / |x_i - x|^3 over
  `GravBody {gm (km^3/s^2), radius (km), posAt: (float) -> Vec3 (AU)}`,
  each `posAt` evaluated at `jdTDB`. Result in **m/s^2**.
- **Inside any body's radius it refuses:** `inside` is true, `body` is that
  body's index (the first in list order), and `acc` is zero. Check `inside`
  before using `acc`; zero is not "no gravity". Outside every body `body`
  is -1.
- **Inertial vs. co-moving.** `accelerationAt` is the inertial field. A ship
  holding station co-moving with a body (or flying a line in that body's
  frame) feels `accelerationRelativeTo(bodies, x, ref, jd)`: the field minus
  the acceleration of body `ref`'s centre from the others, i.e. ref's pull
  plus the others' tides. 50,000 km above Earth the inertial field includes
  the Sun's 5.9e-3 m/s^2; relative to Earth only its 4.5e-6 m/s^2 tide.
- The IAU 2015 B3 nominal constants (`gmSunNominal`, ... in km^3/s^2 and km)
  are given for Sun, Earth and Jupiter only; take other GMs from JPL.
- No J2, no 1PN: fine for a drive that cancels the field, not for orbit
  determination.

## Reflected light (`reflect`)

- The surface law is Minnaert, L = rho E cos^k i cos^(k-1) e / pi; k = 1 is
  Lambert (and is computed by the Lambert expression, so it matches
  `lambertRadiance` bit for bit). Unlit (cos i <= 0) and unseen (cos e < 0)
  give 0; at the exact limb (cos e = 0) k < 1 gives 0, not infinity. Just
  inside the limb k < 1 is unbounded (2x Lambert at cos e = 1e-3 for
  k = 0.9, runaway only at sub-pixel cos e): clamp cos e >= 1e-3 in a
  renderer when k < 1.
- **rho is not an albedo you look up.** Convert from the measured
  geometric albedo: `rhoFromGeometricAlbedo(p, k)` = p (2k + 1) / 2 (the
  Minnaert sphere's opposition disc integral equals p). The model's Bond
  albedo is `bondAlbedo(rho, k)` = 4 rho / (k + 1)^2 (Lambert: rho = 3p/2 =
  A_B, the phase integral q = 3/2). Real planets are not Minnaert spheres
  at all phases: Jupiter's p_V is 0.538 (Mallama 2017) but its measured Bond
  albedo is 0.34, while the Lambert model says 0.81. Use p_V for brightness;
  do not feed the model's A_B into an energy balance.
- `discIlluminance(e1AU, p, R, rAU, d, alpha, k)` = e1AU p (R/d)^2 Phi / r^2
  with R and d in the same unit and r in AU. Phi is `lambertPhase` for
  k = 1 and `minnaertPhase` (a 256-interval Simpson integral) otherwise.
  The radius convention matters at the 0.05 mag level (Jupiter equatorial
  71,492 vs mean 69,911 km): use the radius the albedo was derived with.
- Jupiter, p_V 0.538, equatorial radius: V -2.77 at r 5.20, delta 4.20 AU
  (Mallama & Hilton 2018: -2.70) and -2.98 on 2023-11-03 (Horizons -2.91).
  Expect agreement with measured magnitudes to ~0.1 mag, not better.
- **No relativity import.** The star's illuminance at 1 AU is a parameter:
  for the Sun in V, `sunholo/relativity` `illuminanceFromV(-26.74)` =
  127,057.4 lux.

## Rings (`rings`)

- Classical single scattering in a thin layer (Chandrasekhar 1960; Cuzzi et
  al. 1984). Inputs: single-scattering albedo w0, phase function value
  `phaseP` (P; not the geometric albedo p of `reflect`)
  (at the current phase angle, normalised so isotropic = 1), normal optical
  depth tau, mu0 = |sin B_sun| and mu = |sin B_obs| (elevations over the
  ring plane).
- **Lit face** when observer and Sun are on the same side of the plane,
  **unlit face** otherwise: the caller chooses from the signs of the two
  elevations. `*IF` return I/F; `*Radiance` return I/F x E / pi.
- The unlit face has a removable 0/0 at mu = mu0. For |x| < 1e-3
  (x = tau (mu - mu0)/(mu mu0)) it is evaluated as
  e^(-tau/mu0) tau/(mu mu0) (e^x - 1)/x with a series, finite and continuous
  through mu = mu0; elsewhere by the textbook difference of exponentials
  (both <= 1). **Do not use the product form for all x**: with the Sun
  grazing the rings (tau/mu0 ~ 710-745) e^(-tau/mu0) is subnormal and e^x
  overflows, giving Inf (0.1.0's evaluation caught this before release; a
  sweep test pins finiteness). Shaders need the same two branches.
- `ringTransmission(tau, mu)` = e^(-tau/|mu|) is the fraction passing
  through (alpha = 1 - it); 0 edge-on for tau > 0, 1 for tau = 0.
- Shadow inputs: `ringPlaneHit(p, sunDir, pole)` returns where the sunward
  ray from planetocentric p crosses the ring plane (radius, and mu0 for a
  unit direction); `ringShadowTransmission(bands, p, sunDir, pole)` returns
  e^(-tau(r)/mu0) or 1. The globe's own shadow and the Sun's penumbra are the
  caller's. `bandAt` uses rIn <= r < rOut and returns tau = 0 off the bands;
  the first matching band wins.
- Saturn's main rings (NSSDC fact sheet): C 74,658-91,975 km tau 0.05-0.35;
  B 91,975-117,507 km tau 0.4-2.5 (Cassini UVIS: core > 5); Cassini Division
  to 122,340 km tau 0-0.1; A 122,340-136,780 km tau 0.4-1.0.
- Single scattering under-predicts dense rings (tau >~ 1) somewhat; the
  opposition surge must be in P.

## Validation

`ailang test --package celestial` (from `packages/`) runs 98 tests: every
check value is a published date or constant (JPL Horizons, IAU, NSSDC,
Mallama) or a closed-form identity, cited in the test file.
`python3 tools/orbits_ref.py --check` is the independent oracle (bisection
Kepler, angle-built galactic frame, 50-digit Standish elements, root-found
event times; light time by bisection, gravity in SI, disc and sphere
integrals on 2-D grids, the ring layer integrated through its depth); its
output is in `tools/orbits_ref.out`. `_smoke.ail` prints `OK: ...` and holds
`keplerProbe`, `orbitsProbe`, `lightProbe` and `earthMoonProbe`, which must print the same
bytes under the strict VM and the interpreter. From `packages/celestial`:

```sh
ailang run --quiet --relax-modules --caps IO --entry main _smoke.ail
for p in "keplerProbe 64" "orbitsProbe 64" "lightProbe 200" "earthMoonProbe 200"; do
  set -- $p   # zsh: set -- ${=p}
  ailang run --quiet --relax-modules --entry $1 --args-json $2 _smoke.ail > /tmp/$1.interp
  ailang run --quiet --relax-modules --bytecode --strict-bytecode --entry $1 --args-json $2 _smoke.ail > /tmp/$1.vm
  cmp /tmp/$1.interp /tmp/$1.vm
done
```

(`--relax-modules`: the module path is the package's, not the directory's.)
