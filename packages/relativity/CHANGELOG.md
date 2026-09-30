# Changelog

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
