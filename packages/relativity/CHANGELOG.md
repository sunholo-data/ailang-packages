# Changelog

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
