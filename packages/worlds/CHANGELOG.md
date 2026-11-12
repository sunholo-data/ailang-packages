# Changelog

## 0.3.0 — 2026-11-12

Universe selection, and the closed forms a calibration needs. Additive: every
0.2.0 export returns the same bytes for the same inputs (a 311,423-byte probe
of all of them is identical before and after, on the VM and the interpreter).
Built on 0.2.1: it keeps that release's `sunholo/celestial` 0.7.0 dependency.
Not published from this branch.

New module `selection`:

- `drawParams(baseline, [u1,u2,u3,u4])` is one **draw**: the prior quantile of
  life, minds, tech and lifetime at the four uniforms, bit for bit, with
  complex life following minds as `applyDial` moves it. Nothing is selected.
- `dialOf(baseline, params)` writes a parameter set as an `applyDial` dial and
  checks the round trip to 1e-12. It refuses (`NotADial`) what no dial in
  `applyDial`'s [-100, 100] dex domain can give. **2.25 % of draws are in that
  class**: a life fraction more than 100 dex below its median (the life prior
  is that wide). Such a draw is still a valid `Params` for `historyOf`.
- `priorMeans`, `luckOverMedianDex`, `luckOverMeanDex`, `luckProbability`: the
  three statements of luck. The prior means are 0.5020 (life), 0.1446 (minds),
  0.2150 (tech) and 7.238e6 yr (lifetime); their product is 1.130e5, 2.752 dex
  above the product of the medians (199.9).
- `statisticsOf(setting, params)` and `accepts`: the acceptance test's three
  expected counts (found, ended, late) and whether each is inside its band,
  edges included.
- `acceptanceProbability(baseline, setting, grid)`: the prior probability that
  a draw is accepted, by the closed-form distribution of a sum of two uniforms
  inside Gauss-Legendre panels over the life factor and the lifetime, the panel
  ends placed on the kinks. `productTail(baseline, threshold, grid)` is the
  same for a threshold on the product, through a sum of three uniforms. Both
  return `{p, error}`, `error` being the change when the grid is doubled, and
  refuse (`NotConverged`) a change above 1e-6 of `p`. `expectedDraws` is 1/p.
- `sumUniformCdf`, `sumUniformSurvival`: a sum of one, two or three uniforms of
  given widths, with full relative accuracy in both tails.
- Every function returns a `Result`; nothing returns a default in place of an
  answer. `SelectionError` names the twelve reasons.

Values computed here, with the change on doubling the grid (all run, none
tuned):

| Quantity | Value | Change on doubling |
|---|---|---|
| P(fLife·fMinds·fTech·L ≥ 3.2e7), the calibrated universe (proposed LW-55p) | 2.79607e-4, **1 in 3,576** | 0 (below rounding) |
| the same at 10^7.5 | 2.88440e-4, 1 in 3,467 | 0 |
| Calibrated universe over the product of medians | 5.204 dex | — |
| Calibrated universe over the prior mean | 2.452 dex | — |
| P(product ≥ the median product) | 0.27392 | 0 |
| P(product ≥ the prior mean product) | 0.05787 | 0 |

The review's estimate for LW-55p was "about 2.9e-4, 1 in 3,500"; the computed
value is 2.796e-4.

`epoch_statistics` gains, each returning `Result[_, EpochError]`:

- `endedShares(params)` and `endedWorlds(params, hzWorlds)`: Remnant, Ecocide
  and Transcended at epoch 0 for the one-lineage history model.
- `lateShare(gapYr, lifetimeYr)`: min(1, G/L).
- `lineageShares(params, lineagesPerWorld)`: alive and remnant shares for
  evenly spaced lineages on one world, in closed form. It is not a generator
  and not `history`'s model.
- **A correction to a printed table.** seti-factors §3.4 prints 15 % and 80 %
  for the share of living contacts that end within 16,000 years at lifetimes of
  1e5 and 1e4 years. Those are 1 − exp(−G/L), a memoryless lifetime. With the
  fixed lifetime this model has they are 16 % and 100 %. Every other cell of
  the four rows is reproduced at its printed figure.

`baseline` exports `abiogenesisSigmaDex()` (50, the width of the life prior's
log-rate); `lifeQuantile` reads it, with no change in any quantile.

Evidence: `selection_reference_test.ail` holds `acceptanceProbability` and
`productTail` to an independent Python oracle (`tools/selection_oracle.py`:
clipped areas inside adaptive Gauss-Kronrod, and a 1e7-draw Monte Carlo of the
priors) at 12 regions with p from 0.98 down to 2.2e-6, to 1e-8 of the value
and within 3 Monte Carlo standard errors; the largest measured gap is 1e-11.
`tools/selection_mutants.sh` applies 28 deliberate faults; every one fails a
test. `tools/selection_validation.md` has the tables and commands.

## 0.2.1 — 2026-11-12

Update the exact `sunholo/celestial` dependency from 0.6.0 to 0.7.0 so callers
can combine worlds' propagation API with celestial's additive ICRS TAN image
projection. All worlds AILANG source, tests, public APIs, effect ceilings and
numerical results remain those of published 0.2.0. Its only imported celestial
module, `ism`, is byte-identical across these dependency versions.

## 0.2.0 — 2026-11-12

New module `propagate`: the prediction at arrival. It moves a belief over the
eight planet states forward by an interval in years. Additive; no existing
output changes.

- Every propagator returns `Result[Belief, PredictionError]`. A prediction
  that was not computed is an `Err` naming why (`InvalidParams`,
  `InvalidBelief`, `InvalidRates`, `InvalidYears`, `OutsideExactDomain`,
  `SeenImpossible`); the input belief is never returned in its place.
- `transitionRates(params)` is a continuous-time Markov generator derived from
  the parameters `history` draws from: exits at 1/(mean sojourn) (`1/E[lead]`,
  `1/L` split 0.75/0.15/0.10, `1/E[traces]`) and the sampler's exact epoch-0
  hazard for Complex -> PreTech. It is defined for every parameter set
  `history` accepts (`validParams`).
- `propagate(belief, rates, years)` solves any such chain by uniformisation
  with scaling and squaring: non-negative, sums to 1, the identity at 0 years,
  composable within 1e-12. Two- and three-state chains match their analytic
  solutions to 1e-12; the baseline generator matches a 50-digit Python oracle
  to 6e-16.
- `historyKernel(params, seen, years)` and `propagateExact(belief, params,
  years)` are the sampler's own conditional law, in closed form (one
  Gauss-Legendre piece), for a world known only by its label. They are exact
  inside `exactDomain(params, years)` (`windowYr >= 2e5`, `years <=
  windowYr/2 - 1e5`) and refuse outside it. They must be called once with the
  whole interval, never chained. An independent oracle's reference table
  (`propagate_reference_test.ail`, 42 cells, generated by
  `tools/propagate_reference.py`) holds them to 1e-9; seeded histories drawn
  by `historyOf` agree within 4 standard errors at eight (state, interval)
  pairs.
- **The chain is an approximation of the sampler, and not a close one at long
  intervals.** Largest measured gap in one probability at baseline: 0.523,
  seen PreTech, 1e5 years on. Seen Technological it is 0.368 at L years on (a
  technological epoch lasts exactly `L`, so the sampler has none left; a
  memoryless chain keeps exp(-1)), 0.011 at 10 % of `L` and below 5e-5 up to
  1 % of `L`. `tools/propagate_validation.md` has the tables. Nothing was
  tuned to close the gap.
- `history` now exports its fixed constants (`preTechLeadLoYr`,
  `preTechLeadHiYr`, `collapseShare`, `ecocideShare`, `transcendenceShare`).
  Sampler outputs are unchanged.

## 0.1.0 — 2026-11-02

Initial pure life-and-worlds package: cited baseline-2026.11 with Sandberg's
abiogenesis-rate prior, explicit dex offsets and saturated effective luck,
a cancellation-safe exponential-disc count/CDF model, piecewise SAG13 planet
occurrence in the published units, and immutable histories from keyed uniforms
provided by callers. Joint pathway thresholds keep lineages nested across
richer dials with identical technological onsets. Includes scientific source
qualifications and three corrected historical reference-table cells.


Synthesis helpers (`planet_model`, still in initial 0.1.0): selected 18-knot
Pecaut-Mamajek2022.04.16 dwarf mass sequence; the central connected
Chen-Kipping 2017 median-coefficient radius curve; an explicitly adopted 128-cell
log-mass prior and linear-radius Gaussian conditional mass approximation.
This is not Forecaster's posterior or Mann 2019's K-band mass relation, and is
for labelled synthetic values only. Independent source-node/70-digit numeric
checks, finite/endpoints/quantile-order grids and a Python conditional-CDF oracle
cover the helper, with strict-VM/interpreter byte parity.

`epoch_statistics` keeps the reusable finite-window expectations with the
history model: exact clipped technology/trace probabilities and a capped
log-uniform persistence mean, including equal/narrow-bound cases. The game's
census now composes these probabilities rather than owning scientific maths.
Existing sampler outputs and broad-prior float64 expectations are unchanged.
