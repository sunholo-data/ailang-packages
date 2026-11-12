# sunholo/worlds

## When to use

Use for teaching or simulating the Drake chain with explicit priors and
reproducible histories. All public functions are pure and deterministic;
`_smoke.ail` and the validation test probe print results. Callers own and key their RNG. This package
has no instrument model, world catalogue or game preset. `selection` supplies the
mechanics of drawing and testing a universe; the acceptance bands and everything
about detection are the caller's.

Version 0.2.1 preserves the published 0.2.0 propagation API and all its
AILANG source, tests and smoke byte-for-byte. Only the exact celestial
dependency changes from 0.6.0 to 0.7.0, allowing consumers to share the
additive TAN projection module. Worlds imports only `ism.poissonDraw`;
that celestial module is byte-identical across both dependency versions.
No physical assumptions, numerical results, public exports or effects change.

Validation of 0.2.1 on AILANG v0.56.1 (`05c860a`), 2026-11-12: 19 files
checked; 65 native tests passed, 0 failed, 0 skipped. Strict-VM smoke output
is byte-identical to published 0.2.0 and the interpreter, including exact
and Markov arrival predictions. Normal quality has no gates. Its 78
interface signatures, 43 pure exports and IO ceiling match 0.2.0. Contract
evidence also matches: 1/19 verified, 18 skipped, 0 errors/refuted, 24
uncontracted exports (existing PUB011 warning). Skipped contracts remain
runtime assertions, not proofs. Celestial has no further dependencies.

## Modules and units

- `baseline`: `baselineVersion`, `baseline`, `medianOf`, `quantileOf`,
  `abiogenesisSigmaDex` (50, the width of the life prior's log10 rate). Factors
  have a stable key, prior, dialled flag, citation and qualification. Measured
  values retain reported bounds but `quantileOf(Measured(...))` returns the
  adopted point: no unreported probability density is invented. `AbiogenesisRate`
  means Sandberg §3.1.1's `log10(lambda Vt)~Normal(0,50²)`, mapped through
  `1-exp(-rate)`. Its median is 0.632120558828558. Acklam's inverse-normal
  approximation and a cancellation-free small-rate branch compute quantiles.
  Its extremely small tail can correctly underflow float64; it is not clamped
  to an invented positive floor. Quantiles accept endpoints [0,1].
- `dial`: `Dial`, `Params`, `zeroDial`, `applyDial`, `luckDex`. Fractions multiply
  their median by 10^dex, saturating at 1. Complex life follows the minds offset
  and never falls below intelligence. Lifetime scales in years. Effective luck
  is the log10 gain in the product AFTER probability saturation. Offsets have a finite [-100,100] dex domain contract; baseline fraction
  medians must be in [1e-100,1], lifetime in [1e-100,1e100], window and remnant
  limits positive and <=1e100, with all required keys present. These numerical
  bounds prevent underflow/overflow without changing calibrated values. No
  presets are hidden here.
- `disc`: `Disc`, `starsWithin`, `radiusQuantile`, `everWithin`, `aliveWithin`,
  `existInWindow`. Radius arguments in light-years; density pc^-3, height pc,
  time in years. Local vertical exponential with no Galactic radial gradient;
  this is not a Galactic-centre model. `perStar` is already the complete
  occurrence × life × minds × tech probability for a technological lineage.
  Counts use a stable series near zero; inverse CDF is fixed 60-step bisection.
  The analytic overlap count `(L+W)/Twin` assumes the observing interval is
  away from the finite epoch-window edges. Do not extrapolate it beyond that.
- `occurrence`: `StarClass`, `etaEarth`, `sag13Expected`, `sag13Sample`,
  `planetCount`. Eta is the adopted point (.4 FGK, .16 M, zero Other). SAG13
  follows NASA ExSDET 2019 Eq1/Table1: d²N/dlnR/dlnP, nominal G-dwarf
  coefficients (.38,-.19,.26) below 3.4 Earth radii, (.73,-1.18,.59) above.
  Period API is DAYS, converted internally to YEARS before the power law.
  Rectangles crossing 3.4 are integrated piecewise. The two-uniform sampler
  is explicitly truncated to .5–16 Earth radii and .5–640 days. Applying a
  G-dwarf fit to other classes is a caller-labelled assumption. Eta-HZ slots
  need their own disjoint population accounting to avoid counting them twice.
  `planetCount` reuses celestial's two-uniform Poisson draw.
- `history`: `PlanetState`, `Mind`, `History`, `historyOf`, `stateAt`, `epochs`.
  Epoch in years relative to now. Uniform vector slots: life, joint complex/
  intelligence pathway rank, reserved, technology, onset, pre-tech lead,
  ending, trace persistence. All eight remain keyed even though one slot is
  reserved. Joint thresholds give P(complex|life)=fComplex and
  P(minds|complex)=fMinds/fComplex, preserving nesting when fractions saturate.
  Invalid Params (fraction bounds/order, positive finite time ranges) or
  a short/invalid vector fail closed as Sterile; habitability vetoes always
  win. Technological onsets are centred uniformly on a 5 Gyr window. PreTech
  lead is log-uniform 1e4–1e5 years; epoch lasts L; ending shares .75/.15/.10.
  Collapse traces fade back into the background biosphere; ecocide and
  transcendence are persistent labels. These shares/persistence are design
  assumptions. State boundaries are half-open [start,nextStart). `epochs`
  returns timed changes only, including collapse trace expiry, not an invented
  start for the long-lived background. It is not a model of repeated epochs.

- `planet_model`: explicitly inferred synthesis priors, not measured values.
  `dwarfInTable` / `dwarfMassSun` linearly interpolate a selected 18-knot subset
  of the Msun column in Pecaut & Mamajek's dwarf sequence, version 2022.04.16,
  2380–7220 K. This sparse approximation differs from omitted source nodes by
  up to 6.34% (M5.5V); it is not Mann 2019's K-band calibration, not a giant or
  compact-remnant relation, and not a measurement of any individual star.
  The applicability flag tests temperature support only; callers must establish
  dwarf class separately before using this relation.
  `centralRadiusEarth` composes Chen & Kipping 2017's Table 1 componentwise
  median coefficients into a continuous three-branch curve (0<m<=4200 Earth
  masses). It is neither an arithmetic mean radius nor the full posterior's
  predictive median. `massForRadius` accepts .5–16 Earth radii and one uniform
  in [0,1). It uses an adopted 128-cell log-uniform mass prior on .001–4200 Earth
  masses and a Gaussian in *linear* radius with widths 4.03%/14.6%/7.37% times
  the central curve. The source paper models scatter in log10 radius and
  propagates hyperparameter uncertainty; this approximation does neither.
  It is not Forecaster and must not be described as its posterior. Source
  coefficient medians are verified against arXiv 1603.08614v2 Table 1 pp 7–9.
  High-radius predictions are broad and prior-dependent. Apply to labelled
  synthetic populations only; never replace archive or curated values.

- `propagate` (0.2.0): the prediction at arrival. `Belief` is a record of eight
  probabilities (`sterile`, `microbial`, `complex`, `preTech`, `technological`,
  `remnant`, `transcended`, `ecocide`); `certain(state)`, `probabilityOf`,
  `validBelief` (non-negative, sum within 1e-9 of 1). Time is in years.
  **Every propagator returns `Result[Belief, PredictionError]`.** A prediction
  that was not computed is an `Err` saying why; the input is never handed back
  in its place. Never show a player a belief you did not get from an `Ok`.
  `PredictionError` is `InvalidParams | InvalidBelief | InvalidRates |
  InvalidYears | OutsideExactDomain | SeenImpossible`.
  There are two propagators and they are not interchangeable:
  - `propagate(belief, rates, years)` is a constant-rate Markov chain. `Rates`
    is an 8×8 generator in `stateIndex` order (the order of `PlanetState`);
    build one with `ratesOf([{src, dst, perYr}])` or take
    `transitionRates(params)` (a `Result`: `Err(InvalidParams)` outside
    `validParams`), read it with `rateBetween`, check it with `validRates`.
    `Ok(belief)` itself at 0 years, linear in the belief, and composable: `a`
    then `b` equals `a+b` within 1e-12 per state. Rates up to 1e100 per year,
    years in [0, 1e100].
  - `propagateExact(belief, params, years)` is the conditional law of the
    `history` sampler, built from `historyKernel(params, seen, years)`.
  - **What the exact law assumes.** It is the population law for a world about
    which nothing is known but its label, observed at an epoch near the centre
    of the onset window. Call it **once, with the whole interval** (light age
    plus travel time). Do not chain it: a belief carries no ages, so a second
    call restarts every clock (seen Technological at baseline, one call over L
    years leaves 0 technological; two half-steps leave 0.25; a test pins
    this). It does not use a second sighting of the same world: if the ship
    has looked twice, the kernel knows nothing of the first look.
  - **Where the exact law is exact:** `exactDomain(params, years)`, which is
    `validParams`, `windowYr >= 2e5`, and `0 <= years <= windowYr/2 - 1e5`.
    Check it first. Outside it both functions return
    `Err(OutsideExactDomain)`, including at 0 years; `transitionRates` and
    `propagate` still answer for every valid parameter set, as the
    approximation they are. `Err(SeenImpossible)` means the parameters allow
    no world in that state at epoch 0 (a Remnant when `lifetimeYr >=
    windowYr/2`); `propagateExact` raises it only if the belief puts weight
    there.
  - `validParams` is `history`'s parameter domain with `epoch_statistics`'
    1e-100 floors on the times. A universe `history` accepts is not refused
    for its window.
  - `transitionRates` maps the sampler to rates: Complex→PreTech at the
    sampler's exact hazard at epoch 0; PreTech→Technological at 1/E[lead];
    Technological→Remnant, Ecocide, Transcended at 0.75/L, 0.15/L, 0.10/L;
    Remnant→Complex at 1/E[traces]. Sterile, Microbial, Transcended and
    Ecocide never change, exactly as in the sampler.
  - The chain only approximates the sampler. Largest gap in one probability
    at baseline (L = 1e5 yr): **0.523, seen PreTech, 1e5 years on**; seen
    Technological 0.368 at L years on (the sampler has none left, the chain
    keeps exp(-1)); seen Remnant 0.321 at 1.9e6 years on. For short intervals
    it is small: seen Technological 5e-5 at 1 % of L, 0.011 at 10 %. The chain
    also allows a second lineage after traces fade; the sampler does not.
    For a prediction about worlds drawn by `historyOf`, use `propagateExact`.
  - One piece of the PreTech and Complex kernels is 16×16-point Gauss-Legendre
    quadrature; the rest is closed form. `propagate_reference_test.ail` holds
    the kernel to an independent oracle's exact law at 42 cells, to 1e-9.
  - Parameters are whatever the caller believes. Passing the true dial gives
    the true law; passing an estimate gives the estimate's prediction.
  - Cost on the bytecode VM (Apple M4 Max; command and output in
    `tools/propagate_validation.md` §6): 3.2 ms per `propagate` call, 0.23 ms
    per `propagateExact` call, 0.78 ms when the quadrature piece is in play.
- `history` also exports its fixed design constants: `preTechLeadLoYr`,
  `preTechLeadHiYr`, `collapseShare`, `ecocideShare`, `transcendenceShare`.

- `selection` (0.3.0): drawing a universe from the priors, testing it, and
  saying how rare an accepted one is. All functions return
  `Result[_, SelectionError]`; an `Err` names why nothing was computed
  (`BadUniforms | BadBaseline | UnsupportedPrior | BadParams | NotADial |
  BadSetting | BadGrid | BadWidths | BadThreshold | ZeroProduct |
  ZeroProbability | NotConverged`). Never use a number you did not get from an
  `Ok`.
  - **What a draw is.** `drawParams(baseline, [uLife, uMinds, uTech,
    uLifetime])` returns the `Params` whose four dialled values are the prior
    quantiles at those uniforms (each in [0,1]), exactly as `quantileOf` gives
    them; the complex-life share follows minds as `applyDial` moves it; window
    and remnant limits are the baseline's. One call is one draw. It does not
    look at any setting, re-draw, or tilt anything. The caller supplies and
    keys the uniforms.
  - **A draw as a dial.** `dialOf(baseline, params)` gives the `Dial` for which
    `applyDial(baseline, dial)` returns those parameters (checked to 1e-12 in
    every field before it answers). It returns `Err(NotADial)` when no dial in
    `applyDial`'s [-100, 100] dex domain does: a zero fraction, constants that
    are not the baseline's, or a life fraction more than 100 dex below its
    median. The last is 2.25 % of draws, because the life prior spans hundreds
    of dex. Such a draw is still valid for `historyOf` (it is a universe with
    no life); use the `Params` from `drawParams` directly.
  - **The acceptance test.** `Setting` is data: `hzWorlds` (habitable-zone
    worlds inside the reference radius: `disc.starsWithin` times worlds per
    star), `reach` (knots of the share of a civilisation's life during which a
    sign is on and within reach, against lifetime in years; interpolated
    linearly in log share against log lifetime, held constant outside the
    knots; one knot is a constant), `endedYr` (the time an ended world's sign
    stays findable, standing in for the lifetime), `gapYr` (light time plus
    travel time) and three `Band`s (`Between(lo,hi) | AtLeast(lo) | AtMost(hi)
    | AnyCount`, edges included). `statisticsOf(setting, params)` returns
    `found = hzWorlds·fLife·fMinds·fTech·(L/W)·share(L)` (that is
    `disc.aliveWithin` times the share), `ended = hzWorlds·fLife·fMinds·fTech·
    endedYr/W` and `late = found·min(1, gapYr/L)`. `accepts` is true when each
    is inside its band.
  - **What the test does and does not guarantee.** It reads the four
    parameters only, never a seed. The three numbers are expected counts over
    all the places things could fall. Passing guarantees that those
    expectations are in the bands, and nothing else: an accepted universe can
    still be empty near any one star, and a refused one can hold a contact. It
    does not model detection; `reach`, `endedYr`, `gapYr`, `hzWorlds` and the
    bands are inputs the caller must have measured elsewhere. A lifetime above
    half the window is refused (`BadParams`): `found` would overstate it.
  - **The probability.** `acceptanceProbability(baseline, setting, grid)` is
    the probability, over the baseline's priors, that a draw is accepted.
    `grid` (1 to 16) is the number of Gauss-Legendre panels per smooth piece;
    1 is enough. The result is `{p, error}`: `p` at twice the grid, and `error`
    the change from `grid` to twice `grid`. `error` is a measured change, not a
    bound, and it says nothing about how well the priors are known. A change
    above 1e-6 of `p` is `Err(NotConverged)`. It needs the published prior
    shapes (the rate model for life; log-uniform minds, tech and lifetime;
    lifetime never above half the window) and returns `Err(UnsupportedPrior)`
    for any other baseline. A region no universe can reach is `Ok({p: 0,
    error: 0})`; `expectedDraws` of it is `Err(ZeroProbability)`.
  - **The one-in-N is a statement about the priors, not about the real
    universe.** `expectedDraws(probability)` is 1/p: how many draws from these
    literature ranges an acceptance region takes on average (the index of the
    accepted draw in one run is geometric with that mean). It is not the
    chance that our universe is like the accepted one, and it changes if the
    priors change (the canon lifetime bound of 1e8 yr against Sandberg's 1e10
    is one such choice).
  - **Three statements of luck** for a parameter set (seti-factors §3.8).
    `luckOverMedianDex`: log10 of fLife·fMinds·fTech·L over the product of the
    prior medians; equal to `luckDex` for a dial. `luckOverMeanDex`: the same
    over the prior mean of the product (`priorMeans`: life 0.5020, minds
    0.1446, tech 0.2150, lifetime 7.238e6 yr, product 1.130e5). A universe with
    no life has no luck in dex: `Err(ZeroProduct)`. `luckProbability`: the
    prior probability of a product at least as large (`productTail` for a bare
    threshold). For the calibrated universe (all fractions 1, L = 3.2e7 yr):
    5.204 dex, 2.452 dex and 2.796e-4, one in 3,576.
  - `sumUniformCdf(widths, x)` and `sumUniformSurvival(widths, x)`: a sum of
    one, two or three independent uniforms on [0, width]. The survival
    function is computed from the far end, so a tail of 1e-9 keeps its digits.
  - `converged(coarse, fine)` is the rule that turns two grid values into a
    `Probability`; it is public so that its refusal can be tested.
  - Cost on the bytecode VM (Apple M4 Max, shared machine): 12
    `acceptanceProbability` calls in 1.2 s. The tree-walking interpreter is
    about 100 times slower (about 9 s a call).
  - Evidence: `selection_reference_test.ail` (generated by
    `tools/selection_oracle.py`) holds `acceptanceProbability` to an
    independent oracle at 12 regions, p from 0.98 to 2.2e-6, to 1e-8 of the
    value (measured gap at most 1e-11) and within 3 standard errors of a
    1e7-draw Monte Carlo; `selection_test.ail` scores seeded draws through
    `drawParams` and `accepts` against the computed p.

## Example

```ailang
import pkg/sunholo/worlds/baseline (baseline)
import pkg/sunholo/worlds/dial (applyDial, zeroDial, luckDex)
import pkg/sunholo/worlds/disc (starsWithin)
let p = applyDial(baseline(), zeroDial());
let n = starsWithin({rho0Pc3:0.079,scaleHeightPc:300.0},1000.0)
```

```ailang
import pkg/sunholo/worlds/propagate (certain, exactDomain, propagateExact, PredictionError)
import pkg/sunholo/worlds/history (Technological)
import std/result (Result, Ok, Err)
-- The picture is 212 years old and arrival is 655 years away: one call.
let shown = match propagateExact(certain(Technological), p, 212.0 + 655.0) {
  Ok(atArrival) => atArrival.technological,   -- 0.99133 at baseline
  Err(why) => -1.0                            -- show "no prediction", never the old belief
}
```

## Evidence and known corrections

Native tests include the closed-form Markov chains and seeded-history comparisons for `propagate`, LW check rows, the historical feature tables, a 10,000-
point occurrence histogram, 10,000 histories' order/duration and state share,
and 10,000 cross-dial nesting checks with identical onsets. The published
feature text has three rounding inconsistencies: at 1000 ly the reference ever
count is 803.838985686 (rounds 804, not 805); at 10000 ly the ever count is 164765.267127 (rounds 1.6e5, not 1.7e5);
at 5000 ly/24000 yr the overlap
is .264501263335 (rounds .26, not .27). Tests explicitly use the corrections;
the physics is not adjusted to reproduce those misprints.

Validation commands: `ailang lock`, `ailang check --package .`,
`ailang test --package .`, `ailang pkg quality .`; run `_smoke.ail` with
`--strict-bytecode` and with the interpreter and compare stdout. Contracts
that involve transcendental functions are runtime assertions, not claimed
SMT proofs. Packages remain unpublished until the attended release handoff.

Validation of 0.3.0 on AILANG v0.56.1 (`05c860a`), 2026-11-12: check 24 files;
native 125 passed, 0 failed, 0 skipped; strict-VM suite 125 passed with 122
named-test bodies on the VM and none falling back. `acceptanceProbability`
agrees with the independent reference table at 12 regions to 1e-11 (tolerance
1e-8) and with a 1e7-draw Monte Carlo within 1.4 standard errors, on both; four
probes and the smoke program byte-identical on VM and interpreter; a
311,423-byte probe of every 0.2.0 export byte-identical to 0.2.0; 28 deliberate
faults all killed. `ailang pkg quality .`: no gates (contracts 1/19 verified, 0
refuted). `tools/selection_validation.md` has the detail. Not published.

Validation of 0.2.0 on AILANG v0.56.1 (`05c860a`), 2026-11-12: check 19 files;
native 65 passed, 0 failed, 0 skipped; strict-VM suite 65 passed with 62
named-test bodies on the VM and none falling back. `historyKernel` agrees with
the independent reference table at 42 cells to 1e-9 on both; `propagate_ref.py`
oracle OK; five probes and the smoke program byte-identical on VM and
interpreter; 3000 histories from `historyOf` byte-identical to 0.1.0. Verifier:
1 verified (`stateIndex`), 0 refuted. `tools/propagate_validation.md` has the
detail. Not published.

Earlier validation of 0.1.0 on AILANG v0.56.0: check 14 files; native 29 passed,
0 failed, 0 skipped; strict-VM suite 29 passed; conditional-CDF oracle 780 quantiles;
VM/interpreter grid JSON byte-identical. Full quality now reports no gates and
staged smoke passed after celestial 0.6.0 appeared in the registry. Contracts:
0/10verified,0 refuted,13 uncontracted; 10 skipped by verifier. Float contracts
remain runtime assertions, not proofs. Worlds publication remains attended;
a clean quality report is not a publication result.

AILANG v0.54.18 formatter limitation: named test bodies with let-bound records
produce `nil expression node` in `ailang fmt` although check/test accept them.
Reported with a reduced reproduction to the upstream GCP inbox; no VM or
interpreter workaround is present in package logic.

- `epoch_statistics`: `Probabilities`, `historyProbabilities`, `traceCappedMean`.
  Reusable exact marginals of `history`'s finite uniform onset window. `life`
  is the immutable inhabited background, including ended lineages;
  `mindsWindow` is a technological epoch intersecting [0,futureWindowYr];
  `tech` and `remnant` are probabilities at t=0. These are per-habitable-world
  probabilities, before occurrence/eligibility; they are not detections.
  Positive finite time inputs span 1e-100–1e100 years; fractions obey the
  history sampler's domain/order. Trace means integrate log-uniform persistence
  with clipping and support equal bounds; a narrow-interval log series avoids
  hi/lo cancellation. The adopted collapse share remains 0.75. No history,
  physical input or RNG result is changed by this statistics module.
  Added in 0.3.0, each returning `Result[_, EpochError]` (`EpochParamsInvalid |
  EpochYearsInvalid | EpochCountInvalid | LineageCountInvalid |
  LineagesOverlap`): `endedShares(params)` gives the probability that a
  habitable-zone world is `Remnant`, `Ecocide` or `Transcended` at epoch 0
  (the remnant value is `historyProbabilities`' own; the other two are their
  ending shares of the lineages already ended, which is (W/2 − L)/W of them);
  `endedWorlds(params, hzWorlds)` multiplies by a world count;
  `lateShare(gapYr, lifetimeYr)` is min(1, G/L), the share of civilisations
  alive now that end within G years when a lifetime is exactly L (a memoryless
  lifetime would give 1 − exp(−G/L); that is not this model);
  `lineageShares(params, lineagesPerWorld)` is a closed form for a lineage
  RATE: n evenly spaced lineages per technology-hosting world in the window,
  alive share n·L/W and remnant share n·0.75·E[min(trace, W/n − L)]/W, each
  times fLife·fMinds·fTech. It is a mean-field statement, not a Poisson
  process and not a generator; `historyOf` still draws at most one lineage.
  More lineages than fit end to end are `Err(LineagesOverlap)`.

Validation caveat on AILANG v0.56.0 (reported as
`inbox_1793648615351_707bec99`): `--verify-contracts` rejects invalid `requires`
inputs on the interpreter but the strict VM currently ignores that check,
even in a minimal same-module function. Valid-domain VM/interpreter numerical
parity is measured; VM rejection of invalid domains is **not** claimed. Keep
caller inputs within the documented domains. No alternate sampler or VM math
workaround is included in this package.
