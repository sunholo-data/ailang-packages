# sunholo/worlds

## When to use

Use for teaching or simulating the Drake chain with explicit priors and
reproducible histories. All public functions are pure and deterministic;
`_smoke.ail` alone prints results. Callers own and key their RNG. This package
has no instrument model, selection policy, world catalogue or game preset.

## Modules and units

- `baseline`: `baselineVersion`, `baseline`, `medianOf`, `quantileOf`. Factors
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

## Example

```ailang
import pkg/sunholo/worlds/baseline (baseline)
import pkg/sunholo/worlds/dial (applyDial, zeroDial, luckDex)
import pkg/sunholo/worlds/disc (starsWithin)
let p = applyDial(baseline(), zeroDial());
let n = starsWithin({rho0Pc3:0.079,scaleHeightPc:300.0},1000.0)
```

## Evidence and known corrections

Native tests include LW check rows, the historical feature tables, a 10,000-
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

Current release handoff: local native tests 20/20 (including 100 generated
property cases), package check 11/11 and direct strict-VM/interpreter smoke
pass. `pkg quality` reports PUB015 for its staged smoke: the staging manifest
rewrites the local celestial path to registry `sunholo/celestial@0.6.0`, which
is not published yet. Do not waive or remove the smoke gate. Publish celestial
at the attended handoff, then regenerate this lock and rerun full quality
before considering worlds ready to publish. The native tests and local smoke
are distinct from staged release validation. Contracts currently carry no SMT
proofs (0/7 verified, 0 refuted; float/encoding limits); do not claim proof.

AILANG v0.54.18 formatter limitation: named test bodies with let-bound records
produce `nil expression node` in `ailang fmt` although check/test accept them.
Reported with a reduced reproduction to the upstream GCP inbox; no VM or
interpreter workaround is present in package logic.
