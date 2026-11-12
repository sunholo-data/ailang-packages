# Changelog

## 0.2.0

Feature (minor bump; stapledons-godot R3-REASONS RT1a and RT1b). Five new modules, nothing
removed or changed in `lightcone`. The photon, link and waste-heat modules implement
stapledons-design `physics/observation.md` (baseline-2026.11) §2 and reproduce its rows
OB-1..OB-52 at the printed significant figures. They work in SI, with the unit in every parameter
name; `lightcone` still works at c = 1 in light-years. No new dependency.

- `constants`: h, c, k, AU, parsec, Julian light-year, jansky, arcsecond and milliarcsecond, the
  nominal solar, Earth and Jupiter values (IAU 2015 B3), hc/k, and the two detection thresholds
  `snrHint` (5) and `snrStrong` (10).
- `photon`: `planckPhotonRadiance(tempK, band)`, the blackbody photon integral over a top-hat band
  by the registry's exact series (relative 1e-6 against Simpson's rule for band edge × T ≤ 0.7 m K);
  `photonFlux`, `photonRate(src, distanceM, apertureM, band, throughput)`; `lambertPhase` and
  `planetContrast(geomAlbedo, planetRadiusM, orbitM, phaseRad)`; `magFactor`, `noiseFloorContrast`;
  `diffractionRad`, `innerWorkingAngleRad`, `separationRad`, `iwaLimitDistanceM`, `observable`;
  the background terms `photometricApertureArcsec2`, `zeroMagRate`, `zodiRate` (one term: local
  zodi or exozodi), `zodiTotalRate`, `residualStarRate`, `backgroundRate`, `darkRate`; `snr` and
  `timeToSnrS`; `planetBudget`, which returns the signal, background and dark rates for a planet
  beside a blackbody star; and the registry's `referenceInstrument`, `referenceZodi`, `noZodi`,
  `sunBlackbody`.
- `link`: `dishAreaM2`, `sefdWm2Hz`, `sefdJy`, `fluxWm2`, `linkSnr(eirpW, distanceM, areaM2,
  bandwidthHz, tSysK)` (the SNR in one channel after one coherence time, OB-30), `linkSnrSefd`,
  `integratedSnr` (the radiometer equation), the reach inversions `reachM` and `reachSefdM`,
  `eirpFromErpW`, and the registry's receivers `referenceDishAreaM2`, `referenceTsysK`,
  `largeArrayAreaM2`.
- `wasteheat`: `wasteHeatFactor` (K(λ), Wright et al. 2014), `wasteHeatExcess`,
  `wasteHeatFractionFor`.
- `belief`: **a game model, not registry physics; every number is a design value awaiting
  review.** `likelihoodRow(signal, host)` is the one table: the chance that a world in each of
  the eight planet states shows each of ten signals, for FGK and M hosts, with the false
  positives of stapledons-design signals-and-instruments §4.2–§4.3 (abiotic O₂ on M-dwarf worlds,
  mineral edges, glint without life, natural infrared excess). `likelihood(signal, host, state)`
  reads it. `confidence(snr)` = 1 − 2^−(snr/5)², capped at 0.999: 1/2 at a hint, 15/16 at strong.
  `posterior(prior, host, observations)` is Bayes over the eight states and returns the belief,
  the index of the observation that alone moves the prior furthest, and how far. Looks at one
  signal are combined before the table is applied, so repeats saturate; a non-detection counts
  by the SNR it could have reached; the result is the same bits for any order of observations.
  `pLifeCeiling` and `lifeOddsGainBound` state the bound on a false positive (O₂ alone around an
  M dwarf multiplies the odds of life against a sterile world by at most 4.5). The states are
  `sunholo/worlds` `PlanetState`'s by name and order, as a local type: map by `stateIndex`.
- Tests: `photon_test.ail` (OB-1..OB-27, OB-41..OB-50, the series against Simpson's rule),
  `link_test.ail` (OB-28..OB-37, OB-51, OB-52), `wasteheat_test.ail` (OB-38..OB-40),
  `belief_test.ail` (normalisation, the prior-only case, the false-positive bound, quiet worlds,
  order independence). 110 tests, the same on the strict bytecode VM and the interpreter.
  `_smoke.ail` gains `budgetProbe` and `beliefProbe`, byte-identical on both.
- Contracts state the physical domains (positive distances and apertures, throughput in [0, 1],
  B t ≥ 1) and hold at run time over the probes (`--verify-contracts`). They are runtime
  assertions for the transcendental formulas, not SMT proofs. Known verifier issue on AILANG
  v0.56.1: float division is encoded as integer division, so eight division-only functions
  report a verifier error and `photon.bandOf` reports a false counterexample
  (width 1/2: 0.5 / 2.0 is taken as 0), which `pkg quality` counts as PUB006. Reported as
  ailang#2277; the contract is true, holds at run time, and is kept as written.

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
