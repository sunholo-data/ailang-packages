# Sprint — sunholo/decisions 0.4.0 (use-case map)

Design doc: [v0.4.0-decisions-use-case-map.md](v0.4.0-decisions-use-case-map.md).
Scope per the approved plan; single release, `[release] kind = "breaking"`.

| # | Task | Status |
|---|---|---|
| 1 | Rich questions: `NoulCriteria`, `NoulR`/`ChoiceR`/`ScoreR` through `questionJson`/`noulJson`, `questionSchema`, `degradedAnswer` | done |
| 2 | Analytics: `probabilityOf`, `best`, `ranked`, `topK`, `margin`, `entropy`, `renormalise` | done |
| 3 | Detection: `Detection`, `detect` (three-way, caller cut points) | done |
| 4 | `compositeScore` + `featuresOf` (+ `Feature`) | done |
| 5 | Self-consistency: `Spread`/`VoteReport`, `noulSpread`, `choiceVotes` | done |
| 6 | `retryable`/`retryAfterMs`, `listModelsDirect`, `x-typesafe-sdk` 0.4.0 | done |
| 7 | Tests: 14 new native tests (33 total); `_smoke.ail` `smokeChecks()` | done (author-side; type-check + execution pending operator) |
| 8 | Docs: AGENT.md (use-case map table, rich questions, analytics, availability, API surface), CHANGELOG 0.4.0, manifest 0.4.0/breaking, README row | done |
| 9 | Operator: live probe `.ailang-scratch/decisions_live.ail` (Net,Env,IO; either API key) | pending |
| 10 | Operator: rebuild STALE binary → `ailang lock` → `check --package .` → `test --package .` → `_smoke.ail` → `ailang pkg quality .` | **done** — first run (binary e12e033, still ≠ HEAD) caught 2 real bugs: `entropy` missing the −p·log₂p negation (fixed + `ensures >= 0.0` added), `bodyDeptTechnical` fixture answering 1 of 3 questions (fixed). Re-run: tests **33/33** attested, smoke ✓, **no gates**. On the record: PUB016 10 contracts Z3-skipped (runtime assertions, not proofs), PUB011 22 uncontracted. Binary rebuild to HEAD still outstanding |
| 11 | Operator: git branch/commit/push, `ailang publish` | in progress — first publish refused by the registry's tool-name scan (featuresOf's `${…}`/dotted name-field templates; Bedrock/Vertex name rules). Feature names renamed to underscore-joined provider-safe (`<q>_p`, `<q>_probabilities_<key>`, …), built via `concat` with no interpolation; grace flag deliberately not used. Awaiting re-test + republish |

Definition of done for the release: quality report exit 0 (no PUB006 refuted contracts; PUB016 counts
reported honestly), smoke prints `OK: sunholo/decisions 0.4.0 boot probe`, live probe prints `LIVE OK`,
published 0.4.0 on the registry, CHANGELOG + AGENT.md shipped with it.