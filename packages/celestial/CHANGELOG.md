# Changelog

## 0.1.0

New package (not yet published; this section grows until the 0.1.0
release). Part 1, orbits:

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
