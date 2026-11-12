# Changelog

## 0.2.0 — 2026-11-12

New module `propagate`: the prediction at arrival. It moves a belief over the
eight planet states forward by an interval in years. Additive; no existing
output changes.

- `transitionRates(params)` is a continuous-time Markov generator derived from
  the parameters `history` draws from: exits at 1/(mean sojourn) (`1/E[lead]`,
  `1/L` split 0.75/0.15/0.10, `1/E[traces]`) and the sampler's exact epoch-0
  hazard for Complex -> PreTech (`emergenceRatePerYr`).
- `propagate(belief, rates, years)` solves any such chain by uniformisation
  with scaling and squaring: non-negative, sums to 1, the identity at 0 years,
  composable within 1e-12. Two- and three-state chains match their analytic
  solutions to 1e-12; the baseline generator matches a 50-digit Python oracle
  to 6e-16.
- `historyKernel(params, seen, years)` and `propagateExact(belief, params,
  years)` are the sampler's own conditional law, in closed form (one
  Gauss-Legendre piece). They agree with seeded histories drawn by `historyOf`
  within 4 standard errors at eight (state, interval) pairs.
- **The chain is an approximation of the sampler, and not a close one at long
  intervals.** A technological epoch lasts exactly `L`, so the sampler has no
  technological world left `L` years after seeing one; a memoryless chain keeps
  exp(-1) = 0.368. Measured gaps: below 5e-5 for intervals up to 1% of `L`,
  0.011 at 10%, 0.37 at `L` (seen Technological); 0.52 at worst (seen PreTech).
  `tools/propagate_validation.md` has the tables. Nothing was tuned to close
  the gap.
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
