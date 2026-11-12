# Changelog

## 0.1.1 — 2026-11-12

Update the exact `sunholo/celestial` dependency from 0.6.0 to 0.7.0 so callers
can also use celestial's additive ICRS TAN image projection. All worlds AILANG
source, tests, public APIs, effects and numerical results remain those of
published 0.1.0. The imported celestial `ism` module is byte-identical across
these dependency versions. This patch does not include worlds 0.2.0 features.

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
