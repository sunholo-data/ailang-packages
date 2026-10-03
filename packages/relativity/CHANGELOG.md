# Changelog

## 0.8.1

Fix: the glow-spectrum check values now carry the canon they are labelled with. Every
function is unchanged, and so is every output for the same arguments: no code changed, only
tests, the oracle and documentation. 0.8.0 asserted the first D-29 value, eps = 1e-11,
under the HB-102..110 labels. The canon (stapledons-design physics/higgs-bubble.md §6,
PR #7) moved to **eps = 1e-10** after Mark's D-29 follow-up of 2026-10-03, which chose it
from a rendered comparison. So 0.8.0's labels pointed at rows that now hold different
numbers.

- `glow_spectrum_test.ail`: the luminance, radiance and canon rows are at eps 1e-10:
  - HB-102 9.63e-6 W/m^2 and HB-103 0.1125 W/m^2;
  - HB-104 7.14e-8 cd/m^2 and HB-105 1.65e-3 of the dark sky;
  - HB-106 1.56 cd/m^2 and HB-107 3.61e4 of the dark sky;
  - HB-108: the pole equals the dark sky at gamma 16.2;
  - HB-109 2.41e-6 W/m^2 and HB-110 2.81e-2 W/m^2;
  - new HB-112: the pole reaches 0.3 of the dark sky at gamma 13.5, bracketed.

  The linear-in-eps check now compares eps 1e-9 with 10 x eps 1e-10. HB-95..101 do not
  depend on eps and are unchanged.
- `tools/glow_spectrum_ref.py`: EPS is 1e-10. It prints the rows at 1e-10, 1e-11 and 1e-9,
  and `--check` asserts HB-102..112 at 1e-10, including HB-111 (eps) and HB-112.
  `tools/glow_spectrum_ref.out` is regenerated.
- `medium.glowLuminanceAt`'s doc comment, AGENT.md and the `_smoke` main check now quote the
  eps 1e-10 values. `glowSpectrumDigest` is unchanged (it is a parity digest).
- Correction to the 0.8.0 entry below: "eps 1e-9 -> 1e-11" should read "eps 1e-9 -> 1e-11,
  then 1e-10 (HB-111)", and the canon range is HB-95 to HB-112.

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
