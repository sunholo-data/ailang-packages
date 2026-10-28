# Changelog

## 0.1.0

Feature (new package; stapledons-godot R3-EARTH-LINK EL1, stapledons-design
physics/relativity-spec.md RS-26..RS-37, the "Light cone and Earth's link" row). Pure float64,
c = 1, light-years and years in the galaxy frame, home (Sol) at the origin. Depends on
sunholo/relativity 0.12.0 for the Doppler factor; no formula from relativity is repeated here.

- `lightcone.seenAt(t, obs, src)`: t − |obs − src|, the emission time of light from a static source.
- `lightcone.catchUp(delta, oneMinusBeta)`: delta / (1 − β), when a signal sent delta after
  departure reaches a ship on a straight outbound cruise. 1 − β comes from the caller
  (`kinematics.oneMinusBeta`).
- `lightcone.triangleExcess(a, b)`: |a| + |b| − |b − a|, clamped at 0 against rounding.
- `lightcone.onBeamLine(port, p, angTol)`: p on the ray from home through `port`, by
  atan2(|p × port|, p · port) ≤ angTol with p · port > 0 (home and the far side excluded).
- `lightcone.linkWindow(a, b, legT, covered)`: 0 if covered, else max(0, |a| + |b| − legT).
- `lightcone.earthRate(pos, heading, phi)`: γ(1 + β cos θ) for home's direction through
  `optics.gammaOnePlusBetaCos`, the cosine clamped to [−1, 1]; −heading at home (|pos| < 1e-12 ly).
- `sub`, `cross`, `atSolLy`.
- Tests: `lightcone_test.ail`, RS-26..RS-37 against closed forms (rates to 1e-9 relative, written
  from 1 − β so β = 0.999999 is exact), the at-home guard, onBeamLine's 1e-8 rad resolution and the
  α Cen news epoch 0.043984 (stapledons-godot M4.4 AC1).
