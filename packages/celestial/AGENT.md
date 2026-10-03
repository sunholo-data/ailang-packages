# AGENT.md: sunholo/celestial

## When to use

Use this package when you need where a planet or moon is, how fast it moves,
or which way its pole points, on a real date, with numbers you can cite:
- Solving Kepler's equation and turning orbital elements into position and
  velocity (`kepler`).
- Heliocentric planet positions from the JPL approximate elements, 3000 BC to
  3000 AD, and a labelled mean orbit beyond (`ephemeris`).
- Planetocentric moon positions from JPL mean satellite elements (`ephemeris`).
- Rotating ecliptic vectors into ICRS or galactic coordinates, and IAU poles
  and prime meridians (`frames`).

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
- Light-time, gravity, reflected light, rings: these arrive later in 0.1.0
  (`lighttime`, `gravity`, `reflect`, `rings`).
- Relativity: that is `sunholo/relativity`; the two never import each other.

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
- `Orbit.gm` is the effective n^2 a^3 that makes the velocity follow the
  mean motion actually used, not a physical GM. `elementsAt` and
  `satelliteElementsAt` set it for you.

## Quick start

```ailang
import pkg/sunholo/celestial/kepler (Orbit, State, solveKepler, stateFromElements)
import pkg/sunholo/celestial/ephemeris (MeanElements, ElementRates, SatElements, elementsAt, planetAt, satelliteAt, julianDate)
import pkg/sunholo/celestial/frames (PoleModel, eclipticToGalactic, poleAndSpin, lonLat)

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
```

Inner planets (Mercury-Mars) have b = c = s = f = 0.

## Exported surface

| Module | Exports |
|---|---|
| `kepler` | `Vec3 {x,y,z}`, `State {pos, vel}`, `Orbit {a, e, incl, node, argPeri, meanAnom, gm}`, `Drift {a, e, incl, node, argPeri}`, `solveKepler(M, e)`, `stateFromElements(el)`, `driftingState(el, drift)`, `noDrift`, `meanMotion(gm, a)`, `period(gm, a)`, `orbitRadius(el)`, `orbitNormal(el)`, `wrapPi`, `pi`, `twoPi`, `absf`, `dot`, `norm`, `cross`, `scale`, `add`, `sub` |
| `ephemeris` | `MeanElements {a, e, incl, meanLong, longPeri, node}`, `ElementRates {a, e, incl, meanLong, longPeri, node, b, c, s, f}`, `Ephem {orbit, meanOrbit, drift}`, `elementsAt(el, rates, jd)`, `planetAt(el, rates, jd)`, `SatElements {a, e, argPeri, meanAnom, incl, node, epochJd, meanAnomRate, periRate, nodeRate, poleRa, poleDec}`, `satelliteElementsAt(s, jd)`, `satelliteAt(s, jd)`, `julianDate(y, m, d)`, `auKm`, `j2000`, `windowStartJd`, `windowEndJd` |
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

## Validation

`ailang test --package celestial` (from `packages/`) runs 42 tests: every
check value is a published date or constant, cited in the test file.
`python3 tools/orbits_ref.py --check` is the independent oracle (bisection
Kepler, angle-built galactic frame, 50-digit Standish elements, root-found
event times); its output is in `tools/orbits_ref.out`. `_smoke.ail` prints
`OK: ...` and holds `keplerProbe` / `orbitsProbe`, which must print the same
bytes under `ailang run --bytecode --strict-bytecode` and the interpreter.
