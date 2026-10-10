# Changelog

## 0.13.0

Fix: float64 domain bounds documented for the seven auto-generated property
failures recorded as known under 0.10.1, and `hyper.sinh` no longer saturates
355 rapids early. `ailang test --json --seed 0 .` (the whole-directory
property suite) now reports 0 failures: the seven
(`hyper.expm1`, `hyper.sinhc`, `kinematics.accelerate`,
`optics.doppler`, `dopplerApparent`, `cmbSeenTemperature`,
`cmbSeenTemperatureApparent`) either pass on their documented domain or
discard out-of-domain inputs instead of reporting an Inf/NaN as a violated
`ensures`.

- **hyper (fix).** `sinh`'s `e (e + 2) / (2 (e + 1))` form overflowed once
  `e^|u|` passed about 6e153, i.e. |u| = 355: it returned +Inf where the true
  sinh is finite to |u| = 709.09 (e^709.5/2 = 6.8e307), and NaN past exp's
  own saturation at 709.78. Above |u| = 350 it now returns `e^|u| / 2` — the
  e^-u half is far below one ulp of e^|u|, so this is the correctly rounded
  sinh — bit-identical below 355 and correctly saturated to +Inf past 709.78.
  Every other export's values are unchanged bit for bit.
- **Domain bounds (0.13.0, in each function's `requires`).** `expm1(u)`:
  u <= 700.0 (exp saturates at 709.78; the Kahan ratio's numerator
  (e^u - 1) u overflows past ~703.3; very negative u underflows exp to 0 and
  returns exactly -1.0). `sinhc(u)`: |u| <= 700.0 (sinh is finite there and
  sinh(u)/u >= 1 throughout). `kinematics.accelerate(m, a, dtau)`: dtau >= 0
  as before, and BOTH rapicities `m.phi` and `m.phi + a dtau` within +-700.0
  (cosh/sinh finite; mid, their midpoint, too; |a dtau| <= 1400 keeps
  `sinhc(h/2)` finite; the old failure was sinhc's NaN at |a dtau| ~ 6.6e4).
  For rapidities near the 700 bound with very long steps, t and x can still
  saturate to +Inf — float64 exhaustion, the monotone-time ensures holds
  throughout. `coast` carries the same incoming-rapidity bound (it forwards
  to accelerate). `optics.doppler`, `dopplerApparent`,
  `cmbSeenTemperature`, `cmbSeenTemperatureApparent`: 0 <= phi <= 700.0 and
  the direction pair's dot product within [-1, 1] — n and bh are UNIT
  vectors (AGENT.md conventions); an unnormalised pair's dot is not a cosine,
  and the counterexamples passed dot products like -9847 into
  `gammaOnePlusBetaCos` outside its own contract, where the c = -1 branch
  multiplied a saturated sinh by 0 (NaN). The optics bounds also mean
  `doppler` now calls `gammaOnePlusBetaCos` strictly inside its own
  contract, and D lies in [e^-phi, e^phi], finite and positive throughout
  (T_CMB D finite too, at most 2.76e304 K).
- **kinematics**: `Motion` derives `Eq` (additive; for the boundary tests
  below).
- Tests: new `domain_bounds_test.ail` (10), values proved as float64
  identities rather than oracle constants: expm1/sinh/cosh/tanh/sinhc at
  their domain edges (expm1 = -1 exactly at -709 and finite at 700; sinh =
  cosh = e^700/2 bit for bit at 700 and +Inf at 710 where it was NaN;
  tanh = +-1 from 20 to 700), a zero-length accelerate/coast step as the
  identity at rest and at the +-700 edge (would have been NaN at 709 with
  the old sinh: sinh(700) * 0), an exact one-step burn across +-350 (x
  unchanged, t = sinhc(350) ~ e^350/700), betaOf/gammaOf/oneMinusBeta at the
  edge, and unit-vector doppler/dopplerApparent/cmbSeenTemperature(Apparent)
  at rest (2.725 K) and at the 700 edge (D = e^phi ahead, e^-phi astern —
  the astern edge is the NaN before the fix).

## 0.12.0

Feature (stapledons ledger D-60, D-61, Mark attended 2026-10-09): the
Higgs bubble in a structured interstellar medium, and dust-grain impacts.
Additive: every existing function and digest is value-identical to 0.11.0.
Check values: stapledons-design higgs-bubble.md section 5 (HB-130..HB-137)
and section 6b (HB-124..HB-129, HB-138..HB-149), ism-structure.md (IS-25,
IS-26); oracle tools/ism_dust_ref.py in stapledons-godot (stdlib Python).

- **medium.** `massEquivalentDensity(nH, muH, deltaDust)` = n_H (mu_H +
  delta): the wall reflects every massive particle, dust included, so drag
  and glow follow the whole mass flux (3.4706e5 m^-3 at 0.247 cm^-3, 1.4,
  0.0051). `columnDragEnergy(nCol, phi, r)` = N sinh(phi) m_p c^2 pi R^2,
  equal to `cruiseDragEnergy` for N = n d (1e-12). `tripEnergyColumn(p, mEff,
  nColCoast, r)`, equal to `tripEnergy` for a uniform medium.
  `driveHoldMaxPhi(mEff, a, n, r)` = asinh sqrt(m_eff a / (n m_p c^2 pi R^2)):
  `brakeHoldsAgainstDrag` flips there (tested 1e-9 either side); canon drive
  gamma 16,858 in the hot gas, 2,117 in the warm clouds, 19.3 at 4,200 cm^-3.
- **dust (new module).** `grainMassOf(a, rhoGrain)`, `grainKinetic(m, phi)`
  = 2 sinh^2(phi/2) m c^2 (1 um at 2,500 kg/m^3: 2.011e4 J at 0.999c, 6.646e5 J
  at 0.999999c), `sweptCount(nGrainCol, r)` (frame-independent),
  `grainRate(nGrain, phi, r)` per ship second. The wall afterglow G-AG,
  labelled a game approximation: `afterglowTemperature(ke, rSpot, tau, t)`,
  `afterglowEmittance(ke, eps, fIn, rSpot, tau, t)` (its integral over spot
  and time is eps fIn KE), `afterglowLuminance` (through
  `blackbody.luminousEfficacy`, as the glow), and `visibleRadius(aMin, aMax,
  rhoGrain, phi, eps, fIn, rSpot, tau, bgLuminance, contrast)`.
- `_smoke.ail`: `dustDigest` (strict VM = interpreter) and a dust check in
  main.
- Tests: `medium_column_test.ail` (8), `dust_test.ail` (10).

## 0.11.0

Feature (stapledons ledger D-58, Mark attended 2026-10-09): a star's radius
from its V magnitude, distance and Teff, for the stars without a measured
radius (D-54 stops that show relative size); the Schwarzschild ISCO as a
function; the integrator's step-size note corrected. Additive: every existing
function and digest is value-identical to 0.10.1 (`photometry_table` gains two
node lists; the BP-RP and B-V chains are byte-identical).

- **photometry.** `bolometricCorrectionV(teffK)`: BC_V by linear interpolation
  in Teff in the Pecaut & Mamajek 2022.04.16 dwarf table's BCv column (L5V-O3V,
  1,710-44,900 K; Pecaut & Mamajek 2013, ApJS 208, 9), clamped to the ends, NaN
  to the hot end. `luminositySunFromV(v, distancePc, bc)`: L/L_sun from
  M_bol = V - 5 log10(d/10 pc) + BC with M_bol,sun = 4.74 (IAU 2015 B2,
  `solarBolometricMagnitude`). `radiusSunFromLuminosity(lSun, teffK)`:
  sqrt(L) (5772 K / Teff)^2 (Stefan-Boltzmann, IAU 2015 B3 nominal
  T_eff,sun, `solarTeffNominal`). Extinction is ignored (fine inside ~100 pc).
- **Validation against measured radii** (photometry_test.ail; V, distance and
  Teff as cited there): the Sun -0.3 %, alpha Cen A -0.3 %, alpha Cen B -1.6 %
  (Kervella 2017), Aldebaran -4.5 % (Richichi 2005), Arcturus +3.7 %
  (Ramirez & Allende Prieto 2011), Barnard's Star +0.3 % (Ribas 2018),
  TRAPPIST-1 about +10 % (Agol 2021), Proxima Cen -31 % (Kervella 2017 radius,
  Segransan 2003 Teff 3042 K). M dwarfs are the limit: BC_V falls about 0.5 mag
  per 100 K there, so a 100 K Teff error is about 25 % in R. Validated range:
  about 2,500-7,000 K (dwarfs) and K giants; hot stars (above 7,000 K) follow
  the same table but are not validated here.
- **Why not Flower/Torres.** Torres (2010, PASP 122, 1158; Flower 1996
  corrected) was measured: it agrees with Pecaut & Mamajek to 0.1 mag above
  4,000 K, but its cool polynomial (giants and supergiants) gives M dwarfs
  radii up to 7x too large (TRAPPIST-1 +670 %, Barnard's Star +94 %), and most
  stars within 100 pc are M dwarfs.
- **schwarzschild.** `isco()` = 3 r_s (6 GM/c^2; MTW section 25.6); the
  circular-orbit speed there is exactly 0.5 (tested).
- **Docs fix (geodesic, AGENT.md).** The integrator note said h = 0.005 is
  "about 5e-7 rad worst case". The error grows toward the shadow edge as
  1/eps for b = b_c (1 + eps) and falls as h^4: seen from r = 1000, eps = 1e-8
  gives 1.3e-4 rad at h = 0.005 and 8.2e-6 rad at h = 0.0025 (the stapledons
  lens tables use 0.0025; measured once against `escapeAzimuthExact` for an
  ingoing ray, too slow for the suite); eps = 1e-6 gives 1.3e-6 and 8e-8
  (now tested).
- `tools/mamajek_to_ail.py` emits the BCv chain (`bcTeffNodes`, `bcVNodes`).
- Tests: 6 new (BC nodes and clamps, the definitions, FGK and giants, M dwarfs,
  three killed mutants, ISCO) plus the step-size check.

## 0.10.1

Fix (documentation only; no API or behaviour change, every function and digest
is bit-identical to 0.10.0). The 0.10.0 `ai_summary` and AGENT.md said the
exact null geodesics hold "for a static observer at any radius". They do not:
`escapeAzimuthExact`, `deflectionExactAt`, `imageAngle`, `einsteinAngle`,
`imageMagnification` and `inverseRow` require r >= 2 r_s (closer to the photon
sphere the outgoing quadrature loses accuracy, 8.5e-6 rad at r = 1.51); the
integrator (`escapeAzimuth`, `lensDeflection`, `lensRegular`) requires only
r > 1.5. The summary and AGENT.md now say so.

Known, unchanged: seven auto-generated property tests in older modules
(`expm1`, `sinhc`, `kinematics.accelerate`, `optics.doppler`,
`dopplerApparent`, `cmbSeenTemperature`, `cmbSeenTemperatureApparent`) fail
under `ailang test <module>.ail` because the random generator reaches
|rapidity| ~ 900 where cosh/exp overflow and an `ensures` sees Inf. They are
not part of the package test suite (`pkg quality` 219/219) and predate 0.10.0;
tightening those contracts is left to a later release.

## 0.10.0

Feature: Schwarzschild null geodesics and the closed forms for a crewed visit
(stapledons R1 milestone M3, ledger D-11/D-13/D-53). Additive: every existing
function and digest is value-identical to 0.9.0, except `hyper.tanh` beyond
|u| ~ 355 (fix below).

- **geodesic (new module).** Rays traced back from a static observer at r,
  at angle psi from the hole direction.
  - The integrator (spec section 3): `binetStep` (one RK4 step of
    u'' = -u + 1.5 u^2 in azimuth), `escapeAzimuth(r, psi, h)` (tail-recursive,
    a cubic-Hermite root on the last step, steps shrink only for near-radial
    rays so |du| <= 0.05), `lensDeflection` (delta = dphi - (pi - psi)),
    `deflectionFromInfinity(b, h)`, and `integrateRay` (the integrator's own
    capture verdict, for tests).
  - Capture is analytic: `escapes(r, psi)` (outgoing, or ingoing with
    b > b_c). `escapeAzimuth` takes the verdict from it; if the integrator
    disagrees the azimuth is NaN, never a silent fallback.
  - The exact form (the oracle, about 50x cheaper): `carlsonRF` (duplication,
    a fixed 40 iterations, NaN in gives NaN out), `deflectionExact(b)`
    (Darwin: 2 I(0, u2) - pi), `escapeAzimuthExact(r, psi)` (Carlson when the
    cubic has three real roots; 20-point Gauss-Legendre on the smooth
    outgoing integral otherwise) and `deflectionExactAt(r, psi)`. Roots for
    b >= 4 get two Newton steps (the trig form alone is 1e-10 relative at
    b = 1e6).
  - The lens map: `lensRegular(r, psi, h)` = delta + ln tanh((psi -
    alpha_sh)/alpha_sh), finite from 1e-8 alpha_sh to the antipode at every r
    (what a table stores); `imageAngle(r, beta, order)` (order 0 primary,
    order 1 secondary, 64 bisections), `einsteinAngle(r)`,
    `imageMagnification(r, psi)`; `inverseRow(r, nFwd, nOut)`: one row of an
    inverse lens table (psi - alpha_sh and dpsi/dF on F in [-pi, pi]) by
    Fritsch-Carlson monotone inversion of nFwd exact forward samples
    (`inverseRowLogMin` = ln 1e-8 is the first column).
  - Accuracy (oracle: stapledons-godot tools/geodesic_ref.py, a Python RK4,
    Carlson in float64 and a 50-digit Decimal truth): the exact form is
    within 1e-15 of the truth at b = 100 and 1000; the integrator is within
    3e-13 of it at h = 0.001 and 1.3e-11 at h = 0.005 (check45 rays).
    Near the critical impact float64 conditioning sets the floor: at
    b = b_c (1 + 1e-8) one ulp of the input moves the deflection by ~1e-9.
  - **The weak-field fact.** At b = 100 r_s the exact deflection is
    0.02029996623954 rad, 1.5 % above 2/b: the second-order term
    15 pi/(16 b^2) is exactly that size. `weakDeflection2` (below) is within
    2.7e-4 of it; at b = 1000 2/b is within 0.148 %.
- **schwarzschild**: `impactFromStaticAngle`, `turningRadius`,
  `weakDeflection2` (2/b + 15 pi/16b^2), `weakDeflectionFinite` ((1 + cos
  psi)/b, finite observer), `strongDeflectionBbar` (Bozza 2002,
  -0.400230039755), `circularOrbitSpeed` (local, sqrt(1/(2(r-1))),
  `circularOrbitClockRate` (sqrt(1 - 1.5/r)), `orbitalAngularVelocity`,
  `movingClockRate`, `radialCoordinateRate`, `hoverAcceleration`,
  `rsPerSolarMassMetres` (2953.25008 m, IAU 2015 nominal GM_sun),
  `tidalRadial` (1/r^3), `tidalTransverse`, `tidalRadialOrbit` (1.5 x static
  at 3 r_s), `tidalAccelSI(mSun, r, lenM)` and `tidalOrbitAccelSI` (m/s^2;
  the bubble wall does not shield tides), the inversions `tidalSafeRadius`
  and `tidalMinMass`, `hoverAccelSI` and `hoverPowerPerKg` (via
  `medium.hoverPower`). Sgr A* (4.297e6 Msun) with a 100 m lever: tide
  5.691e-6 / 4.553e-5 / 2.108e-4 g at 10 / 5 / 3 r_s; hover 4.8189e5 m/s^2
  and 1.4447e14 W per kg of m_eff at 3 r_s. Gaia BH1: 4.205e7 g at 3 r_s,
  0.1 g only beyond 2247.6 r_s.
- **hyper (fix)**: `tanh(u)` returns exactly +-1 for |u| > 20 (it already
  rounded to 1 there); beyond |u| ~ 355 it was NaN (expm1 overflow, Inf/Inf).
- Tests: `schwarzschild_ext_test.ail` (23: check49, check51 to check53 and the
  canon rows HB-72 to HB-90) and `geodesic_test.ail` (19: check41 to check48,
  check50, the inverse row, tanh). Smoke: `schwarzschildDigest`, `lensDigest`
  (strict VM = interpreter bit for bit; the oracle agrees to 2e-14).

## 0.9.0

Feature: a gentle final approach and timed legs (stapledons ledger D-46,
attended 2026-10-06: in-system legs of equal rhythm, and arrivals that are
not sudden). Additive: every existing function, `TripPlan` value and digest is
bit-identical to 0.8.0 (`journeyDigest` 177359.65222313255 before and after).

- **Why.** Under one constant brake the remaining distance falls with the
  square of the time left, so a target grows explosively in the last
  seconds: Jupiter from about 3 degrees to 60 degrees in the final ~8 s.
- **journey**: `planBurnCoastBrakeApproach(distance, a, phiCruise,
  aApproach, phiApproach)`. Accelerate at a, coast, brake at a down to
  phiApproach, then brake at the gentler aApproach to rest. Each segment is
  the constant proper-acceleration closed form already used by
  `planBurnCoastBurn`; nothing physically new. Without a usable approach
  (phiApproach <= 0, >= phiCruise, NaN, or aApproach <= 0) it is
  `planBurnCoastBurn` bit for bit; if the segments do not fit it falls back
  to it with `fellBack = true`.
- **journey**: `TripPlan` gains `aApproach`, `phiApproach`, `tauApproach`
  and `dApproach`, all 0 for the other profiles. `motionAt` is closed form
  in every segment, each measured from its own start, and keeps its 0.8.0
  code path verbatim when `tauApproach` is 0. `phaseAt` is unchanged: the
  approach is `Decelerating`, so existing matches on `TripPhase` stay
  exhaustive. `inApproach(p, tau)` marks [tauTotal - tauApproach, tauTotal).
- **journey**: `rapidityForTimedLeg(distance, tBoost, tCruise)` solves
  2 tBoost (cosh phi - 1)/phi + tCruise sinh phi = distance (the boost lasts
  tBoost at a = phi/tBoost), and `rapidityForTimedApproach(distance,
  tApproach)` solves tApproach (cosh phi - 1)/phi = distance. Both use 200
  fixed bisection halvings (VM = interpreter) and return 0 for non-positive
  or NaN input. Sun -> Jupiter (4.4 AU, 30 s + 60 s): phi 4.0807, 0.99943c;
  Jupiter's approach from 4 degrees across, 25 s: phi 0.4981, 0.46c.
- Tests: `approach_test.ail` (13). Oracle: `tools/approach_ref.py`
  (float64 against 50-digit Decimal). Smoke: `approachDigest`.

## 0.8.0

Feature: the wall glow's spectrum (stapledons ledger D-30, attended
2026-10-03), so a renderer takes the glow's colour and luminance from the
package instead of GDScript (the M4.2 evaluation's gate-3 finding). Additive;
every existing function and digest is bit-identical to 0.7.0
(`glowEmittanceAt` is parameterised by eps, so the canon change of D-29,
eps 1e-9 -> 1e-11, lives in callers and check values, not here). Canon:
stapledons-design physics/higgs-bubble.md section 6, HB-95 to HB-111.

- **Model.** The wall is a greybody of emissivity eps. By Kirchhoff's law it
  emits light as well as it absorbs it, and the wall is transparent, so the
  emissivity is the same small eps that thermalises the impacts. The energy
  balance eps K cos theta = eps sigma T^4 cancels eps:
  T = (K max(0, cos theta) / sigma)^(1/4), the temperature a black surface
  would reach if it thermalised the whole forward beam. eps and fIn set only
  the brightness: the inner face emits eps fIn sigma T^4 = `glowEmittanceAt`.
  Game approximation: real GeV impacts give hadronic cascades, not a Planck
  spectrum. Rejected: T from the per-particle energy (about 7e13 K at 0.99c,
  a fixed Rayleigh-Jeans blue) and a black wall radiating only the glow flux
  (2 K at 0.99c, invisible at every speed).
- **medium**: `glowTemperatureAt(n, phi, cosTheta)` (K), by two square roots
  (no pow; VM = interpreter bit for bit): 290.27 K at 0.5c, 1357.52 K at 0.99c,
  2481.90 K at 0.999c, 14114.02 K at 1 - beta = 1e-6 (pole); cos^(1/4) off
  the pole; 0 at rest, aft, on the equator and for phi < 0; NaN in, NaN out.
- **medium**: `glowRadianceAt(n, phi, eps, fIn, cosTheta)` = `glowEmittanceAt`
  / pi (Lambertian wall, W m^-2 sr^-1).
- **medium**: `glowEfficacyAt(n, phi, cosTheta)` (lm/W) = `luminousEfficacy`
  at the glow temperature: 0.02331 at the 0.99c pole, 43.68 at the cap (the
  M4.2 placeholder white was 182.57).
- **medium**: `glowLuminanceAt(n, phi, eps, fIn, cosTheta)` (cd/m^2) =
  radiance x efficacy. At eps 1e-11, n 0.1 cm^-3, fIn 1/2: 7.1437e-9 cd/m^2
  on the 0.99c pole (1.65e-4 of the 23.5 mag/arcsec^2 dark sky, HB-105) and
  0.15643 at the cap (3.61e3, HB-107); the pole reaches the dark sky at
  gamma 24.7 (HB-108).
- **blackbody**: `stefanBoltzmannSI()` = 5.670374419e-8 and
  `luminousEfficacy(kelvin)` = pi photopicRadiance(T) / (sigma T^4) (lm/W),
  finite and >= 0 for every input (0 at T <= 0, NaN, +Inf and below the
  visible underflow near 25 K). 95.455 lm/W at 6600 K, the CIE blackbody
  maximum (about 95 lm/W near 6,600 K).
- Tests: `glow_spectrum_test.ail` (17 tests): temperature, radiance,
  efficacy and luminance at 0.5c, 0.99c, 0.999c and the cap at 0 to 90 deg
  against the oracle to 1e-12; sigma T^4 = K cos theta and emittance =
  eps fIn sigma T^4; T = T_pole cos^(1/4); the canon rows HB-95 to HB-110 to
  their printed digits; the dark-sky and Draper crossings bracketed; edges
  (rest, aft, equator, phi < 0, clamp, NaN, eps 0, linear in eps); finite,
  >= 0 and <= the pole over 26 x 11 points of [0, phiCap] x [-1, 1].
- tools/glow_spectrum_ref.py (output tools/glow_spectrum_ref.out): the
  oracle, 60-digit Decimal. sigma from exact SI h, k, c (agrees to 3e-11);
  Stefan-Boltzmann checked by integrating Planck's law in the package's
  normalisation (6e-8, from the package's rounded c2); the 1 nm sum against
  a 0.1 nm Simpson integral (5e-9 at 1357 K, 5e-7 at 14,114 K, reported);
  efficacy maximum 95.46 lm/W near 6,650 K. `--check` asserts the canon
  digits.
- `_smoke.ail`: `glowSpectrumDigest(n)` (interpreter and strict VM print the
  same bits) and a spectrum check in `main`.

## 0.7.0

Feature: the apparent disc of a nearby sphere, and hover power. Additive; every
existing function is unchanged. (0.6.0 is M4's `medium.glowEmittanceAt`; this
release follows it.)

- **optics**: `apparentDisc(cosTheta, alpha, phi)` returns `ApparentDisc
  {centre, radius}` (rad) for a sphere of angular radius alpha centred at
  rest-frame polar angle theta. Aberration is conformal, so the outline stays
  a circle whose meridian edges are the aberrated theta -/+ alpha; the centre
  is their mean, which is not the aberrated centre. Check values (the M5
  design's RS-24 to RS-29, for stapledons-design physics/relativity-spec.md):
  0.9c, theta 90, alpha 5: centre 25.9277296298034 deg, radius
  2.18394056339431 deg (aberrated centre 25.8419327631671); 0.99c: 8.14017747175280,
  0.707096852084493; 0.9c, theta 150: 82.0207127068368, 9.94041081060385.
  Identity at phi = 0 to 1e-15 rad; finite with radius > 0 and centre in
  [0, pi] over phi to the 1 - beta = 1e-6 cap; a disc over a pole keeps it
  inside.
- **optics**: `angleSeen(theta, phi)`, the angle form of `cosSeen` by the
  half-angle law tan(theta'/2) = e^-phi tan(theta/2). It never forms
  1 - beta, is exact next to both poles and at the cap, and is continuous and
  odd over (-2 pi, 2 pi), so edges past a pole need no branch.
- **medium**: `hoverPower(mEffKg, gMs2)` = m_eff |g| c (W), higgs-bubble.md
  §10 P_hover (HB-90): the photon-drive power that holds the ship against an
  unfelt acceleration. 0.1254 m/s^2 gives 0.1254 c W/kg to 1e-15; rebuilt
  from HB-10, Sgr A* at 3 r_s gives HB-88 4.82e5 m/s^2 and HB-90 1.44e14 W/kg.
  M3's planned black-hole `hoverPowerPerKg` can compose it.
- Tests: `optics_test.ail` (12 tests) and three `medium_test.ail` tests.
  Expected values come from the new `tools/optics_ref.py` (output
  `tools/optics_ref.out`): the rest-frame circle built in 3D, each photon
  direction Lorentz-transformed in 60-digit Decimal, the nearest and farthest
  image points found by search, and the outline checked circular to 1e-30
  rad, a different method from the package's. Agreement 1e-12 relative (1e-11
  at the cap). The oracle reproduces the M5 design's printed digits, also
  asserted (`--check`). D at the apparent centre via the unchanged
  `dopplerApparent` is checked too (2.2871, 7.0623, 0.4981); at the cap it
  holds to 1e-9 only, from `dopplerApparent`'s own gamma^2-ulp conditioning
  near the forward pole (noted in AGENT.md, not changed here).
- `_smoke.ail`: `discDigest(n)` (strict VM = interpreter, bit for bit) and an
  apparent-disc and hover check.
## 0.6.0

Additive: no signature changes; every 0.5.2 result is bit-identical. The
wall glow's angular profile, so a renderer can draw the forward glow from the
package instead of deriving it (stapledons-godot milestone M4.6a, sprint
R1-M4-JOURNEY; design m4-first-journey.md, Forward glow). Check values:
tools/glow_ref.py (stdlib Python, 60-digit Decimal; output in
tools/glow_ref.out) and the canon IDs HB-n of stapledons-design
physics/higgs-bubble.md section 6.

- **medium**: `glowEmittanceAt(n, phi, eps, fIn, cosTheta)` = eps fIn K
  max(0, cos theta) (W/m^2), the inward glow emittance of the wall element
  whose outward normal is at angle theta from the travel direction (ship
  frame), K = `kineticFlux(n, phi)`. A sphere in a forward beam intercepts
  K max(0, cos theta) per unit area, so the profile peaks at the forward pole
  and is 0 on the aft hemisphere and at rest. Its value at cos theta = 1 is
  exactly 4 x `glowInwardFlux` (bit for bit) and its mean over the sphere is
  `glowInwardFlux`, since the sphere mean of max(0, cos theta) is 1/4.
  cosTheta is clamped to [0, 1]; NaN gives NaN (tested first, ailang#1419).
  With n = 0.1 cm^-3 (HB-3), eps = 1e-9 (D-15) and f_in = 1/2: pole
  9.628776871706523e-5 W/m^2 at 0.99c (the M4 design's 9.62878e-5) and
  1.1250843031053144 W/m^2 at 1 - beta = 1e-6 (design 1.12508).
- Tests (`medium_test.ail`, 9 new): the profile at 0, 45, 80, 90 and 120
  degrees at 0.5c, 0.99c and the cap against the oracle to 1e-12; pole =
  4 x mean exactly at four speeds and another (eps, fIn); the sphere mean by a
  4000-bin midpoint sum over cos theta equals `glowInwardFlux` to 1e-12, with
  the aft half exactly 0; zeros at rest, on the equator, aft and at eps = 0;
  the clamp; NaN in cos theta or phi; finite, >= 0 and <= the pole over
  201 x 41 points of [0, phiCap] x [-1, 1]. The 10^4-point medium sweep also
  covers the new function.
- `_smoke.ail`: `glowDigest(n)` (interpreter and strict VM print the same
  bits) and a pole check in `main`.
- tools/glow_ref.py: the oracle. It checks the 1/4 sphere mean independently
  by a Simpson quadrature in theta (not in cos theta) and asserts the M4
  design's printed digits, HB-45 (K at 0.99c) and HB-61 with `--check`.

## 0.5.2

Fix: the 0.5.0 evaluation's follow-ups. No API change. Results are
bit-identical to 0.5.1 for every blackbody temperature below ~1.7e9 K and for
every photometry input; the only numeric changes are above that, listed here.

- **blackbody**: `planck` (and so `xyz`, `luminance`, `chromaticity`,
  `rgbUnitLuminance`, `pointFluxRatio`, `surfaceBrightnessRatio`,
  `photopicRadiance`) is finite and accurate for every T > 0, +Inf included.
  For e = c2 / (lambda T) < 1e-5 (T above ~1.7e9 K at 830 nm) the
  denominator is `hyper.expm1(e)` instead of exp(e) - 1, and T is clamped at
  the Planck temperature 1.416784e32 K (CODATA 2018); NaN is tested first and
  never clamped. 0.5.1 lost digits there (relative error ~1e-16 / e) and was
  +Inf above ~1.6e20 K, where exp(e) - 1 rounds to 0. Behaviour changes, all
  above 1.7e9 K: `photopicRadiance(1e12)` 6.4955697458e18 -> 6.4955697453e18
  (-6.5e-11), `(1e15)` 6.49557196e21 -> 6.49556983e21 (-3.3e-7), `(1e20)`
  7.711e26 -> 6.4956e26 (0.5.1 was 19% high), +Inf -> 6.4956e31 at 1e25 K,
  9.2028e38 flat from T_P up and at +Inf. New values match the expm1 Simpson
  oracle to 9.8e-7 (the 1 nm sum's own offset; tested at 2e-6) and scale exactly as Rayleigh-Jeans (x10 per decade to
  1e-12); photopicRadiance now rises strictly up to the clamp. The comment
  claiming "finite for every finite T" is now true and tested.
- **photometry**: `pointThresholdIlluminance` and `limitingMagnitude`
  document that Crumey's fit is not monotone over 0.022-0.108 cd/m^2 (the
  scotopic branch peaks at (-r1 / 2 r2)^4 = 0.02184 cd/m^2, dips 22% to the
  0.0708 split; the photopic branch regains the peak at 0.1077). Code
  unchanged; AGENT.md says the same.
- Tests (`photometry_sky_test.ail`): the Crumey test is split into one named
  test per regime (dark cut-off, scotopic branch, photopic branch, transition,
  naked-eye limit) with values at 0.03 and 0.05 cd/m^2 that pin which branch
  serves the split (the 0.0708 -> 0.03 mutation now fails 3 tests, it passed
  all before); a non-monotone test pins the peak, the dip ratio 0.7799 and the
  limiting magnitudes across it. Proxima has its own test: no check value in
  stapledons-design physics/relativity-spec.md, so the reference is Boyajian
  et al. 2012 (3054 K); asserted at both catalogue colours (B-V 1.82 Jao 2014,
  1.97 Boyajian 2012) within 6%, the spread B-V saturation itself produces,
  with the interpolation pinned to 1e-9 K. Two new tests cover the extreme
  temperatures (oracle rows 1e9-1e25 K and T_P, Rayleigh-Jeans ratio, clamp,
  a 1e6-1e308 K finite and rising sweep, +Inf).
- tools/photometry_ref.py prints the new rows; tools/photometry_ref.out is
  regenerated (additions only; every 0.5.0 row is byte-identical).

## 0.5.1

Fix: `photometry`'s private table helper is renamed `lookup` → `tableLookup`. In 0.5.0 it
clashed with `blackbody_photometry`'s private `lookup` (different arity) under
`ailang test` when a package imported both modules (ailang#1461, a test-runner
scoping bug; `ailang run` was unaffected). No API change. New `cross_module_test.ail`
imports both modules together as a regression guard.

## 0.5.0

Additive: no signature changes. Photometry for a rendered relativistic sky in
absolute units. Check values: tools/photometry_ref.py (stdlib Python; output
in tools/photometry_ref.out), the canon IDs HB-n of stapledons-design
physics/higgs-bubble.md, and the cited literature.

- **photometry**: `teffFromBV(bv)` and `bvInTable(bv)`: dwarf temperature
  from Johnson B-V, linear in the same Pecaut & Mamajek 2022.04.16 table's B-V
  column (O3V-M9V, -0.33-2.17), clamped, NaN to the cool end. Sun 0.65 ->
  5770 K; alpha Cen B, Barnard's, Proxima, Sirius A within 5% of literature
  T_eff. `luminanceFromSurfaceMag(mu)` (V mag/arcsec^2 -> cd/m^2 on the
  package zero point; mu 22 -> 1.7252e-4) and `surfaceMagFromLuminance`;
  `vFromIlluminance` (inverse of `illuminanceFromV`);
  `pointThresholdIlluminance(lb)` (naked-eye point-source threshold in lux
  against background luminance, Crumey 2014 MNRAS 442, 2600, Eqs. 53 and 33
  with the Blackwell constants of Eqs. 26-27, dark cut-off at 1e-5 cd/m^2)
  and `limitingMagnitude(lb, f)` (6.942 at 2e-4 cd/m^2, f = 1; Crumey 6.93 on
  his zero point).
- **photometry_table**: `bvNodes`, `bvTeffNodes`, generated by
  tools/mamajek_to_ail.py from the same source file (BP-RP chain unchanged,
  byte for byte).
- **blackbody**: `photopicRadiance(kelvin)`: absolute luminance in cd/m^2,
  683 lm/W x integral B_lambda ybar. 0 for T <= 0, NaN and the CMB's 2.725 K
  (underflow), so a CMB term never divides by ~0. Matches a 0.05 nm Simpson
  oracle to 2e-7; within 0.33% of the CIE 1931 table at 1,900-6,000 K; the
  platinum point (2041.4 K) gives 5.98e5 against the pre-1979 candela's 6.0e5.
- **optics**: `cmbSeenTemperature(n, bh, phi)` (rest-frame direction,
  T_CMB D) and `cmbSeenTemperatureApparent(nSeen, bh, phi)` (apparent
  direction, per pixel). 3,853.7 K on the pole at 1 - beta = 1e-6 (HB-63),
  38.44 K at 0.99c (HB-62), gamma T_CMB = 1,926.9 K at rest-frame 90 deg and
  at apparent 1/gamma rad (HB-68), T_CMB / gamma at apparent 90 deg.
- Behaviour fix: `teffFromBpRp` and `gMinusV` now map NaN to the cool end node
  on both engines (the VM used to return NaN, the interpreter 2420 K;
  ailang#1419).
- `_smoke.ail`: `photometryDigest(n)` (strict VM = interpreter, bit for
  bit), `photopicFinite(n)` (10,000-point sweep, run on the VM), and a
  sky-photometry check.

## 0.4.0

Additive: `Trip`, `flipAndBurn`, `burnCoastBurn` and `coastAt` keep their
signatures. Check values: tools/journey_ref.py (stdlib Python, float64 closed
forms cross-checked against 50-digit Decimal; output in tools/journey_ref.out)
and the canon IDs HB-n of stapledons-design physics/higgs-bubble.md.

- **journey**: `TripPlan` (trip totals plus `a`, `phiPeak`, `tauBurn`,
  `tauCoast`, `tauTotal`, `dBurn`, `dCoast`, `fellBack`),
  `planBurnCoastBurn(d, a, phiCruise)` (cruise speed as a rapidity; falls back
  to flip-and-burn with `fellBack` when 2 dBurn >= d), `planFlipAndBurn(d, a)`,
  `TripPhase` (`Accelerating | Coasting | Decelerating | Arrived`),
  `phaseAt(p, tau)` (left-closed boundaries) and `motionAt(p, tau)` (closed
  form per phase, clamped to [0, tauTotal]; exact at the boundaries and at
  arrival). `flipAndBurn` and `burnCoastBurn` are now `planX(...).trip`.
- **hyper**: `acosh1p(u)` = acosh(1 + u) without forming 1 + u.
  `flipAndBurn` uses it, so short trips keep their low bits.
- **kinematics**: `rapidityOfOneMinusBeta(e)`: the rapidity of a speed given
  as 1 - beta, never forming 1 - e.
- **medium** (new, SI): constants `cSI`, `protonMassKg` (CODATA 2018),
  `lightYearM` (IAU), `julianYearS`, `astronomicalUnitM`, `cmbTemperatureK`
  (2.725 K, HB-5); `accelSI` (c/yr to m/s^2); `photonDriveEnergy`,
  `loadScale`, `kineticFlux`, `mirrorDragForce` (specular sphere, half a flat
  mirror), `mirrorDragPower`, `cruiseDragEnergy`, `glowInwardFlux`,
  `TripEnergy`, `tripEnergy` (boost = brake = m_eff c^2 phi, drag over
  dCoast), `brakeHoldsAgainstDrag`.
- **optics**: `forwardDoppler(phi)` = e^phi, `cmbForwardTemperature(phi)`.
- Behaviour change within rounding: `burnCoastBurn`'s burn distance is now
  2 sinh^2(phi/2)/a instead of (cosh(phi) - 1)/a (same value, no cancellation
  at low speed), and `flipAndBurn` forms acosh via `acosh1p`.
- NaN: `brakeHoldsAgainstDrag` is false for NaN; `planBurnCoastBurn` with a
  NaN input takes the fallback branch on both the VM and the interpreter
  (ailang#1419: the interpreter answers NaN >= x with true); `phaseAt` and
  `motionAt` treat a NaN tau as 0.
- `_smoke.ail`: `journeyDigest(n)` (strict VM = interpreter, bit for bit) and
  a cruise-trip check.

## 0.3.0

- **blackbody_photometry**: blackbody white-dwarf temperature and V from Gaia
  BP-RP (`bbTeffFromBpRp`, `bbTeffFromBpRpExact`, `bbGMinusVFromBpRp`,
  `bbVFromG`, forward `bbBpRp` / `bbGMinusV`, `bbBpRpInvertible`,
  `bbClampTeff`, `bbTeffMin`, `bbTeffMax`), plus the generated
  `blackbody_photometry_table` (tools/gaia_bb_to_ail.py).
- Convention: Gaia EDR3 VEGAMAG, photon counting (response x wavelength),
  published passbands (Riello et al. 2021) at 5 nm, Bessell & Murphy 2012
  photonic V at 10 nm, trapezoid quadrature. Colour zero point is
  ZP_BP - ZP_RP = 0.5906467146 (Vega route agrees to 5.2e-5 mag). Inversion
  bracket 3,000-100,000 K; out-of-bracket and non-finite colours clamp.
- Accuracy (blackbody vs GF21 photometric T_eff, 1,780 WDs within 50 pc):
  median ratio 1.038, 68% in [1.006, 1.052], 95% in [0.988, 1.065], 99.2%
  within 10%; up to +17% above 25 kK; against CALSPEC model T_eff for 7 hot
  WDs 0.92-1.15. G-V against real SEDs -0.006 to -0.039 mag (-0.09 for a
  strong-line DA). Stated product accuracy: T_eff +-10% (typically 4% hot),
  V +-0.1 mag. Numerical: quadrature <= 2.6e-4 mag, table <= 5e-4 relative T.
- Not corrected: Gaia's EDR3 BP systematic for bright blue sources
  (about -0.018 mag in BP-RP).

## 0.2.0

- **photometry**: pure Gaia BP-RP to dwarf effective temperature and G-V,
  Johnson V conversion, visual illuminance and magnitude flux ratios.
- Generated from Pecaut & Mamajek's 2022.04.16 dwarf sequence. Raw rows
  with both Gaia colours span B9V–M9.5V; the strictly increasing table used
  for interpolation spans B9V–M8.5V (M9V and M9.5V are dropped because their
  BP-RP colours reverse). Values clamp at the retained endpoints.
- The Riello et al. 2021 Gaia EDR3 cubic differs from the interpolated table
  by up to 0.10 mag across BP-RP 0.4–3.0 (0.1015 at 3.0, in the M dwarfs), so
  that cross-check uses 0.11 mag; across F–K (0.4–1.3) it uses 0.05 mag.

## 0.1.0

First release: pure, tested special- and general-relativity maths.

- **hyper**: `sinh`, `cosh`, `tanh`, `atanh`, `acosh`, `expm1`, `log1p` and
  `sinhc`, accurate near zero (Kahan constructions). `std/math` has none of
  these.
- **kinematics**: rapidity-based straight-line motion under constant proper
  acceleration.
  - Steps are exact at any step size, and symmetric burns return to rest to
    rounding.
  - `oneMinusBeta` stays exact at γ ≈ 10⁸.
- **journey**: ship time vs galaxy time for flip-and-burn, burn–coast–burn and
  pure-coast trips.
- **optics**: aberration and inverse aberration, and Doppler from both rest
  and apparent directions. Written without cancellation, so it stays accurate
  near c.
- **blackbody**: Planck × CIE 1931 → XYZ and linear sRGB. Visual-band
  brightness ratios for point sources and extended sources under a Doppler
  shift.
- **schwarzschild**: photon sphere, critical impact parameter, shadow angular
  radius for a static observer (including inside the photon sphere),
  weak-field deflection, static-observer blueshift and clock rate.
- 40 tests against independent reference values, plus a smoke check for a
  clean workdir.
- Planned: exact null-geodesic deflection (a Binet-equation integrator) and
  Terrell rotation for extended objects.
