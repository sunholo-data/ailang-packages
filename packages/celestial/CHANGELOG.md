# Changelog

## 0.1.1

Feature: the Earth-Moon barycentre split. Standish's "EMB" row is the
Earth-Moon barycentre, so 0.1.0 put the Earth (and anything placed relative
to it) mu |r_geo| = 4,330-4,950 km from its centre. Every 0.1.0 signature
and result is unchanged; the additions are in `ephemeris`.

- `earthMoonSplit(emb, moonGeo)` -> `EarthMoon {earth, moon}`:
  Earth = EMB - mu r_geo, Moon = EMB + (1 - mu) r_geo, positions and
  velocities alike. `earthAt(embEl, embRt, moon, jd)` and
  `moonAt(embEl, embRt, moon, jd)`: the heliocentric Earth and Moon from
  Standish's EMB row and the Moon's JPL mean elements (`satelliteAt`).
  `earthMoonMu()` = 1 / (1 + EMRAT) = 0.0121505843958292 and
  `earthMoonMassRatio()` = EMRAT = GM_Earth / GM_Moon = 81.3005682214972154
  (JPL DE440/DE441; Park et al. 2021, AJ 161, 105).
- Tests (5 more, 98 in all), against JPL Horizons (DE441) vectors on
  2000-01-01.5, 2023-11-03.0 and 2026-01-01.0 TDB: DE441's Earth-from-EMB
  is -mu times its geocentric Moon (1e-12); Horizons' EMB split with
  Horizons' Moon gives Horizons' Earth and Earth + Moon (1e-13 AU,
  1e-15 AU/day); `earthAt` - EMB is within 200 km of Horizons'
  Earth-from-EMB (54, 134, 49 km; the Moon's mean elements omit evection and
  variation); over 400 dates moon - earth = the geocentric Moon and
  (1 - mu) earth + mu moon = the EMB to 1e-15 AU; `earthAt`'s velocity is
  its derivative. Five hand mutations of the split (mu = 0.01215,
  mu = M_moon/M_earth, the Earth's sign, 1 - mu -> 1, an unsplit Earth
  velocity) are each killed.
- `tools/orbits_ref.py`: `earth_moon()` re-derives the split in 50-digit
  Decimal from the Horizons values (query recorded) and the mean-element
  offset with its own Kepler and plane rotation; `tools/orbits_ref.out`
  gains those rows (additions only).
- `_smoke.ail`: `earthMoonProbe(n)` (strict VM = interpreter, bit for bit)
  and the Earth-from-EMB check against Horizons in `main`'s OK line.
  Private test helpers named `earthAt` in `_smoke.ail` and
  `gravity_test.ail` are renamed (`unitEarthAt`, `earthPosAt`) so they do
  not shadow the new export (ailang#1461).

## 0.1.0

New package: orbits (part 1) and light, gravity and rings (part 2).

Part 1, orbits:

- **kepler**: `solveKepler(M, e)`, Newton with exactly 8 iterations from
  E0 = M + e sin M (no data-dependent loop exit, so the strict VM and the
  interpreter take the same path); residual < 1e-14 for |M| <= pi and
  e <= 0.97 (worst 4.4e-16 over a 98 x 4001 grid in the oracle); e = 0 gives
  E = M exactly. `stateFromElements(el)` gives position and velocity
  (perifocal -> reference frame); `driftingState(el, drift)` adds the exact
  velocity of drifting a, e, i, node and argument of periapsis. `Vec3`,
  `State`, `Orbit`, `Drift`, `meanMotion`, `period`, `orbitRadius`,
  `orbitNormal`, `wrapPi` and vector helpers.
- **ephemeris**: `elementsAt(el, rates, jd)` and `planetAt` from the JPL
  approximate elements (Standish & Williams 1992, Table 2a with Table 2b's
  b, c, s, f). The window is T = -50 .. +10 Julian centuries (3000 BC-3000 AD);
  outside it a, e, I, perihelion and node freeze at the edge, the mean
  longitude keeps advancing, and `meanOrbit` is true. The velocity is the
  exact derivative of the position. `satelliteElementsAt` and `satelliteAt`
  take JPL SSD mean satellite elements with signed apse and node rates on a
  Laplace plane given by its ICRS pole (the ecliptic pole for the Moon).
  `julianDate` (Meeus 7.1, proleptic Gregorian), `auKm`, `windowStartJd`,
  `windowEndJd`.
- **frames**: `eclipticToEquatorial` (IAU 2006 obliquity 84381.406"),
  `equatorialToGalactic` (Hipparcos 1997 A_G), `eclipticToGalactic`,
  `equatorialToEcliptic`, `unitFromAngles`, `lonLat`, and
  `poleAndSpin(model, jd)` for IAU WGCCRE 2015 models with periodic terms
  (`PoleModel`, `PoleTerm`, `Spin`), `rotationPeriod`.
- Tests (42): Kepler residual grid and corners, vis-viva, angular momentum,
  orientation, derivative checks; Meeus Julian dates; Jupiter's opposition
  2023-11-03 and Mars's 2020-10-13 (+-2 d); Saturn's ring-plane crossings
  2009-08-11 and 2025-05-06 (+-10 d); Earth's and Saturn's obliquities; the
  mean-orbit flag and window edges; the Moon inside 356,375-406,720 km and its
  8.85 yr perigee period; Io's sidereal period 1.769137786 d (1e-4 d); the
  north ecliptic pole at galactic (96.38, 29.81); WGCCRE Saturn and Jupiter.
  `tools/orbits_ref.py` re-derives each with independent code.

Part 2, light, gravity and rings:

- **lighttime**: `retarded(srcFn, obs, t)` (time, position and lag),
  `retardedTime`, `lightTimeDays`: the light-travel equation solved by a
  fixed-point iteration on the lag, exactly 4 steps from 0 (error
  (v/c)^4 of the lag). `cAuPerDay` (299,792.458 km/s over the IAU 2012 au),
  `secondsPerDay`.
- **gravity**: `accelerationAt(bodies, x, jdTDB)`, the Newtonian point-mass
  sum in m/s^2 over `GravBody {gm, radius, posAt}` (AU positions, km^3/s^2,
  km), refusing within any body's radius (`inside`, the body's index, zero
  acceleration); `accelerationRelativeTo` (the field in a body's co-moving
  frame: its pull plus the others' tides); `pointAcceleration`; IAU 2015 B3
  nominal GM and radii for the Sun, Earth and Jupiter.
- **reflect**: `starIlluminanceAt`, `lambertPhase`, `lambertRadiance`,
  `minnaertRadiance`, `minnaertPhase` (separable photometric-coordinate
  integral, 256-interval Simpson), `phaseFunction`,
  `rhoFromGeometricAlbedo` / `geometricAlbedoFromRho` (rho = p (2k+1)/2),
  `bondAlbedo` (4 rho/(k+1)^2), `bondFromGeometricAlbedo`, and
  `discIlluminance` (e1AU p (R/d)^2 Phi / r^2). The star's 1 AU illuminance
  is a parameter: no dependency on sunholo/relativity.
- **rings**: `ringLitIF`, `ringUnlitIF` (finite and continuous through
  mu = mu0 via a series for (e^x - 1)/x when |x| < 1e-3, the bounded
  difference of exponentials otherwise, so it stays finite with the Sun
  grazing the rings; swept over mu0 1e-4..1, mu 0.01..1, tau 0..10), `ringLitRadiance`,
  `ringUnlitRadiance`, `ringTransmission`, `RingBand` and `bandAt`,
  `ringPlaneHit` and `ringShadowTransmission` for ring shadows.
- Tests (51 more, 93 in all): light times to Jupiter (2023-11-03, 1987.3 s)
  and Saturn (2023-08-27, 4372.8 s) against JPL Horizons; the closed-form
  uniform-motion lag; the iteration count pinned by its (v/c)^4 error; the
  design's idealised Jupiter lag 2095.8 s and 27,400 km displacement; g =
  0.1254 m/s^2 at 50,000 km above Earth and 11.0 m/s^2 at 1.5 R_J; NSSDC
  surface gravities; `inside`; superposition, inverse square and symmetry;
  the solar tide in Earth's frame; Lambert Phi(0) = 1, Phi(pi/2) = 1/pi,
  Phi(pi) = 0 and q = 3/2; Minnaert k = 1 = Lambert to 1e-15; the rho <-> p
  round trip to 1e-12 and both albedo normalisations by numerical disc and
  sphere integrals; Jupiter's V -2.77 (r 5.20, delta 4.20, p_V 0.538;
  Mallama & Hilton -2.70) and within 0.1 mag of Horizons on 2023-11-03;
  the ring lit face -> Lommel-Seeliger at tau -> inf, both faces -> 0 at
  tau -> 0, the unlit face's finite mu -> mu0 limit, transmission limits,
  Saturn's NSSDC/Cassini ring bands and the solstice ring shadow, and precision at the removable singularities. All 32 hand mutations of the part-2 modules are killed.
  `tools/orbits_ref.py` re-derives each with independent methods.
- Pre-release fixes from the independent evaluation (round 1, 89/100): the
  unlit ring face no longer overflows to Inf for tau/mu0 ~ 710-745 (B1);
  rings' phase-function parameter is `phaseP` and illuminance parameters are
  `lux` (no clash with `reflect`'s albedo p or `kepler`'s e); `planetAt` and
  `bondAlbedo` carry explicit warnings; the documented `_smoke.ail`
  commands include `--relax-modules` and `--caps IO`.
