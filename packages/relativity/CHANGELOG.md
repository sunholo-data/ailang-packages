# Changelog

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
