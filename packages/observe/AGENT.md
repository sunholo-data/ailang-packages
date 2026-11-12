# AGENT.md: sunholo/observe

## When to use

Use this package when something far away is seen or heard by light: when the
light arrives (`lightcone`), whether there is enough of it to measure
(`photon`, `link`, `wasteheat`), and what a set of measurements says about a
world (`belief`).

**Timing (`lightcone`, c = 1, light-years and years):**
- When the light now arriving left a static source: `seenAt(t, obs, src)`
  = t − |obs − src| (the newest news from home, its age).
- When a signal sent after a ship left catches it on a straight outbound
  cruise: `catchUp(delta, oneMinusBeta)` = delta / (1 − β).
- How much history from home a moving ship receives per second of its own:
  `earthRate(pos, heading, phi)`, the Doppler factor γ(1 + β cos θ) for home's
  direction. Below 1 receding (e^−φ straight away), above 1 approaching.
- Relaying a plan via home: a plan sent from port a reaches home |a| later,
  and home's reply reaches port b |b| after that. `linkWindow(a, b, legT,
  covered)` is the wait at b after arriving, max(0, |a| + |b| − legT);
  `triangleExcess(a, b)` is the pure geometry |a| + |b| − |ab|.
- Whether a point is on the ray of a beam home aims at a port:
  `onBeamLine(port, p, angTol)`.

**Budgets (`photon`, `link`, `wasteheat`, SI units):** an instrument's reach is
the output of a budget for stated inputs, never an authored range.
- Photons from a star into a telescope: `photonRate(src, distanceM, apertureM,
  band, throughput)`; a star is a `Blackbody`, a band is a top-hat `Band`
  (`bandOf`, `resolutionElement`).
- How faint a planet is beside its star: `planetContrast(geomAlbedo,
  planetRadiusM, orbitM, phaseRad)`.
- How long a spectrum takes: `planetBudget(...)` gives the signal, background
  (residual starlight + local zodi + exozodi) and dark rates; then
  `snr(S, B, D, seconds)` and `timeToSnrS(target, S, B, D)`. The thresholds
  are `constants.snrHint()` (5) and `snrStrong()` (10).
- Whether the planet can be separated from its star at all: `observable(...)`,
  `iwaLimitDistanceM(...)`; and the noise floor, `noiseFloorContrast`.
- How far a transmitter is heard: `linkSnr(eirpW, distanceM, areaM2,
  bandwidthHz, tSysK)`, `integratedSnr`, and the inversion `reachM(eirpW,
  targetSnr, areaM2, tSysK, nPol, bandwidthHz, seconds)`.
- How much a civilisation's waste heat brightens its star in the infrared:
  `wasteHeatExcess(gamma, lambdaM, starTempK, wasteTempK)`.

**Belief (`belief`, a game model):** `posterior(prior, host, observations)` is
Bayes over the eight planet states. `likelihood(signal, host, state)` is the
chance a world in that state shows a signal. Every number in this module is a
design value awaiting review; none comes from the physics registry.

It is pure: no effects, deterministic, and the same bits on the bytecode VM
(`--strict-bytecode`) and the interpreter.

Do NOT use it for:
- Moving sources. `seenAt` is exact only for sources static in the frame. For
  Solar System bodies use `sunholo/celestial`'s `lighttime` (a retarded-time
  iteration).
- Aberration, the Doppler factor of an arbitrary direction, or 1 − β itself:
  use `sunholo/relativity` (`optics`, `kinematics`).
- Accelerating legs in `catchUp`: it assumes the whole outbound path is a
  straight cruise at one β from departure.
- Real stellar spectra, real filters, or mission planning. The star is a
  blackbody, bands are top hats, throughput is grey, noise is plain Poisson
  (stapledons-design `physics/observation.md` §5 lists every simplification).
- Science claims from `belief`. Its table is a game's model of how often each
  kind of world shows each signal.
- A detection radius. Nothing here returns "this telescope sees N
  light-years" except as the output of a budget you state.

## Units and conventions

- **Two unit systems, one per job.** `lightcone` is c = 1 in light-years and
  years. `photon`, `link` and `wasteheat` are SI, and every parameter name
  ends in its unit: `distanceM`, `apertureM`, `tempK`, `eirpW`, `bandwidthHz`,
  `phaseRad`, `...Arcsec2`. Convert a distance with `constants.lightYearM()`
  or `parsecM()`. Rates are counted photons per second in one resolution
  element.
- **Phase angle** is star–planet–observer: 0 at full phase, π/2 at quadrature.
- **A belief** is eight probabilities in `stateIndex` order (Sterile,
  Microbial, Complex, PreTech, Technological, Remnant, Transcended, Ecocide,
  the order of `sunholo/worlds` `PlanetState`), summing to 1.
- **An `Observation`** is `{signal, detected, snr}`. For a detection, `snr` is
  the detection's SNR. For a non-detection it is the SNR the instrument would
  have reached had the signal been there (from `photon` or `link`).
- **`lightcone`: c = 1. Light-years, years**, the galaxy (rest) frame, float64.
- **Home is the origin.** Every position is measured from it.
- **heading** is a unit vector along the ship's velocity; **phi** is its
  rapidity (β = tanh φ), 0 ≤ φ ≤ 700.
- **Pass 1 − β, never compute it.** `catchUp` takes 1 − β; get it from
  `kinematics.oneMinusBeta(phi)` (exact at γ in the millions). `1.0 - beta`
  rounds to 0 near c.
- **At home** (|pos| < `atSolLy()` = 1e-12 ly) `earthRate` takes home's
  direction as −heading: leaving home reads e^−φ, continuous with just outside,
  and a ship at rest reads 1.

## Pitfalls

- `triangleExcess` is not the wait when b lies on a beam's ray: a port beyond
  a or between home and a gives an excess of 2|a| or more, but home is already
  aiming along that ray. Test coverage with `onBeamLine` and pass it to
  `linkWindow` as `covered`.
- `covered` is the beam home was aiming when the plan was sent (the previous
  plan's port), not the one it aims at when the ship arrives: by then home has
  usually heard the new plan, and every port would look covered.
- Choose `angTol` for the beam, not for float64: the atan2 form resolves
  angles down to about 1e-15 rad, so 1e-7 rad (about 4 AU off a 40 ly ray) is a
  physical choice.
- `onBeamLine` excludes home itself and the far side of home (p · port ≤ 0).
- `linkWindow` needs the leg's galaxy time T from your journey model; at high
  γ, T ≈ |ab| and the wait is the triangle excess.

- `planetBudget` is the photon budget only. It will give an integration time
  for a planet inside the inner working angle (OB-19); test `observable`
  first, and compare the contrast with `noiseFloorContrast`.
- `photon.snr` is the SNR of the planet's continuum in one resolution
  element, not of an absorption band. What a spectrum means is `belief`'s job.
- The band integral's domain is band edge × T ≤ 0.7 m K (121 µm at 5772 K).
- Zodiacal light does not depend on aperture or distance. Pass `noZodi()` for
  none, or set `localLevel: 0.0` for a ship in interstellar space.
- `linkSnr` is one channel after one coherence time (t = 1/B). Use
  `integratedSnr` for longer; it needs B t ≥ 1. The budget assumes the
  transmitter points at you for the whole integration: whether it does is a
  likelihood (`belief`'s `Leakage` row), not a budget.
- `wasteHeatExcess` needs γ < 1.
- `belief`: record `O2CH4` or `O2` for one spectrum, never both. Looks at the
  same signal saturate at the table's value; different signals multiply.
- `belief` does not import `sunholo/worlds`. Its `State` has the same
  constructor names; import one set of constructors and map by `stateIndex`.
- `posterior`'s `movedMost` is an index into the list you gave (−1 if nothing
  moved the prior).

## Example

```ailang
import pkg/sunholo/observe/lightcone (earthRate, linkWindow, onBeamLine)
import pkg/sunholo/relativity/kinematics (rapidityOfOneMinusBeta)

-- 40 ly out, cruising straight away at beta = 0.999999: 7.0711e-4
earthRate({x: 40.0, y: 0.0, z: 0.0}, {x: 1.0, y: 0.0, z: 0.0}, rapidityOfOneMinusBeta(0.000001))
-- re-planned at a port 40 ly out to one 30 ly off at a right angle: wait 60 yr
linkWindow({x: 40.0, y: 0.0, z: 0.0}, {x: 40.0, y: 30.0, z: 0.0}, 30.0, false)
```

```ailang
import pkg/sunholo/observe/constants (pi, auM, parsecM, lightYearM, earthRadiusM, snrHint)
import pkg/sunholo/observe/photon (sunBlackbody, planetContrast, planetBudget, timeToSnrS,
  referenceInstrument, referenceZodi)
import pkg/sunholo/observe/link (reachM, referenceDishAreaM2, referenceTsysK)
import pkg/sunholo/observe/belief (HostM, O2, posterior, pLife)

-- An Earth twin at 10 pc in the O2 A element (0.76 um, R = 140): 20.68 hours to a hint
let c = planetContrast(0.2, earthRadiusM(), auM(), pi() / 2.0);
let b = planetBudget(sunBlackbody(), c, 10.0 * parsecM(), 0.00000076, 140.0, referenceInstrument(), referenceZodi());
timeToSnrS(snrHint(), b.signal, b.background, b.dark) / 3600.0
-- A 2e13 W radar, 100 m dish, 1 Hz, 1 s: SNR 1 at 376.3 ly
reachM(2e13, 1.0, referenceDishAreaM2(), referenceTsysK(), 1.0, 1.0, 1.0) / lightYearM()
-- O2 alone, strong, around an M dwarf: P(life) 0.0995 -> 0.19 (abiotic O2 is the false positive)
pLife(posterior([0.90, 0.07, 0.02, 0.004, 0.003, 0.002, 0.0005, 0.0005], HostM, [{ signal: O2, detected: true, snr: 10.0 }]).p)
```

## Tests

`ailang test --package .` (and `--strict-bytecode`) runs:
- `lightcone_test.ail`: RS-26..RS-37 against closed forms, the at-home guard,
  the 1e-8 rad resolution and the α Cen news epoch.
- `photon_test.ail`, `link_test.ail`, `wasteheat_test.ail`: every row
  OB-1..OB-52 of stapledons-design `physics/observation.md`, each passing when
  the computed value rounded to the row's printed significant figures equals
  the printed value; and the band integral against Simpson's rule.
- `belief_test.ail`: the posterior sums to 1, no observations return the
  prior, the false-positive bound, quiet worlds, order independence.

`_smoke.ail` prints `OK: ...` in a clean workdir, and its `linkProbe`,
`budgetProbe` and `beliefProbe` must print identical bytes on the strict VM
and the interpreter.
