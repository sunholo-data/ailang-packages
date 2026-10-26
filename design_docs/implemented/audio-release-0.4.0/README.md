# Audio 0.4.0 release record

Published 2026-10-26 with AILANG v0.54.18, after [PR 165](https://github.com/sunholo-data/ailang-packages/pull/165)
merged as `32274caebee029ba3fb8f6a3f70d7113a1bec24b`.
[Source release](https://github.com/sunholo-data/ailang-packages/releases/tag/audio-v0.4.0).
Package sources are immutable at that commit; this record is subsequent bookkeeping.

The publisher reported a successful upload; registry discovery independently
reports audio 0.4.0. A fresh consumer with only the registry dependency resolves
the published content and runs the gain-ramp → delay impulse probe successfully
on the interpreter and strict VM with runtime contracts. No producer path or
sibling checkout is required.

[receipt.json](receipt.json) contains the observed public identities and counts.
It excludes raw publisher logs and credentials.

## Publisher quality, section by section

| Section | Observed result |
|---|---|
| Compile | 32 files pass |
| Contracts | 16/71 verified; 55 skipped (5 missing postconditions, 50 unsupported encodings), 0 refuted/errors; 33 uncontracted exports |
| Interface | 154 signatures; interface-v2 identity in receipt |
| Effects | Declared max [IO], rank IO; processing pure, IO only in smoke |
| Release | Feature, nonempty 0.4.0 changelog |
| Docs | AGENT.md and ai_summary present; heuristic covers 7 exports |
| Style | 100/100 pure processing exports |
| Tests | 192/192 across 14 files, 0 failed/skipped; executed locally, attested to registry |
| Smoke | Present, executed and passed; attested to registry |
| Gates/badges | No gates; PUB016 (55 unproved), PUB011 (33 uncontracted exports) |

[Final pre-merge CI](https://github.com/sunholo-data/ailang-packages/actions/runs/40285431116)
passes. [Implementation evidence](../audio-effects-0.4.0/README.md) records strict-VM
execution (177 named tests, zero fallback), 15 evaluator properties ×100 cases,
independent WAV reference, consumer compatibility and descriptive CLI timings.
The unchanged inline DSP suite separately has 11 passes and one generator skip.

The two new integer cursor/ramp-position helpers are proved. Seven public effect
APIs retain unsupported-encoding skips; mathematical Real/Int proofs do not imply
IEEE-754 equivalence, realtime callbacks, perceptual or physical device quality.
The registry validator does not execute attested tests/smoke.

## Next consumer

The [Audio Tools design in ailang-demos](https://github.com/sunholo-data/ailang-demos/pull/3)
proposes an offline checked processing workbench followed by optional AI inputs.
It uses the exact registry release and an isolated pinned runtime. The design is
reviewable; implementation/deployment have not started. Loop Lab remains a
separate application with its existing release/dependency lifecycle.
