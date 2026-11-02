# sunholo/worlds 0.1.0

Pure models for cited astrobiology priors, anthropic offsets, local-disc counts,
planet occurrence, immutable world histories, and clearly labelled synthetic
stellar/planet mass approximations. The package takes uniforms;
it does not own a random generator or choose game presets or strategies.

The normative source is Stapledon's Voyage's
[life-and-worlds registry](https://github.com/sunholo-data/stapledons-design/blob/feat/life-and-worlds/physics/life-and-worlds.md),
version `baseline-2026.11`. Scientific uncertainty, adopted approximations and
game assumptions remain separately labelled. In particular the nominal M-star
share 0.75 has an **unverified empirical attribution**; do not cite it as Reylé's
measurement. Sandberg's life model is a normal prior on log abiogenesis rate,
not a log-uniform life fraction. The technological-lifetime prior deliberately
uses canon 100–100 million years rather than Sandberg's 100–10 billion years.

The synthesis helper's mass distribution is an adopted 128-cell log-mass
prior with a linear-radius Gaussian likelihood around Chen & Kipping's median
coefficients. It is **not Forecaster's posterior**. Its selected 18-knot dwarf
mass sequence is an approximation to Pecaut & Mamajek2022.04.16, not Mann 2019's
K-band calibration. Neither helper overwrites measured planets.

See [AGENT.md](AGENT.md) for units, API, exact uniform slots and limitations.
Publication is an attended handoff; this checkout is not a published version.

`epoch_statistics` supplies the exact finite-window probabilities for an
inhabited background, technology intersecting a future interval, technology
at now and surviving collapse traces. Its clipped log-uniform trace integral
also handles deterministic and narrow persistence intervals. It describes the
existing history model; it adds no detection assumption or new physics.
