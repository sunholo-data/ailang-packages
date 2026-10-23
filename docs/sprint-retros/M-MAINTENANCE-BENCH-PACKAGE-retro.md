# Sprint retrospective: M-MAINTENANCE-BENCH-PACKAGE

The instrument is implemented in [source PR #156](https://github.com/sunholo-data/ailang-packages/pull/156). The observational survey and controlled model campaign have not run. This sprint provides a repeatable research package, not evidence that a language has fewer bugs.

## Scope and measurements

- Execution was sequential, with one independent reviewer required by the sprint skills. No parallel implementation or speedup claim.
- Planned: eight milestones, 2,160 source/test LOC, 4–6 focused days. Actual final source: 35 AILANG files / 1,544 physical lines (1,204 production/examples, 340 native tests), plus integration fixtures, documentation and CI. Largest AILANG file: 169 lines. LOC reflects formatting and is not a quality score.
- Recorded session timestamps cover an attended agent session, not eight independently timed engineering tasks or a defensible human-days velocity. Milestones were revisited during adversarial review, so their initial pass intervals below understate total work per subsystem. No LOC/day productivity inference.
- Package validation: 84 native tests, two properties ×100 generated cases, offline/installed integration, independent analytical oracle, one verified SMT contract. Regular quality and source CI pass. Strict quality explicitly fails PUB011: 75 exports have no contracts. Four formatter-only test exceptions are documented; those tests still execute.

## Milestone checkpoint intervals

| Milestone | Planned LOC | Initial checkpoint interval | Result |
|---|---:|---|---|
| M1_SCHEMA | 300 | 5.3 min | Passed |
| M2_GIT | 260 | 2.6 min | Passed |
| M3_GITHUB | 300 | 4.7 min | Passed |
| M4_COHORT | 320 | 3.3 min | Passed |
| M5_METRICS | 340 | 3.3 min | Passed |
| M6_REPORT | 280 | 10.3 min | Passed |
| M7_REPEATABILITY | 240 | 41.3 min | Passed |
| M8_SOURCE_RELEASE | 120 | 14.3 min | Passed |

Per-milestone final LOC is not assigned because schema/report/lineage tests and review fixes cross milestones. Aggregate physical source counts above are the reproducible final measurement.

## Friction and corrections

- The published testing_utils dependency failed on the pinned compiler. Native assertions replaced the proposed dependency; no duplicate assertion framework or unrelated package fix was introduced.
- Deeply nested codec/interpolation formatting stalled. Decomposed helper records and join/concat kept production formatting bounded. Four valid native-test ASTs still hit formatter nil-expression failures; narrow exceptions and minimal repro assets preserve visibility.
- Float-backed JSON conversion could erase fractional evidence. Raw numeric lexemes now require exact nonnegative integer tokens before decoding. Duplicate object keys also fail explicitly.
- Independent review exposed comparison identity, oracle coverage, acceptance-date provenance, rename-swap identity and unknown repair-round errors. Regression tests now exercise each case. Pure observed artifact lineage accounts for repeat touches, confirmed repairs and features separately.
- Git commit times cannot establish accepted exposure. Git acquisition stays labelled commit-time until a reviewed acceptance date is provided; public PR acquisition uses merged_at.
- A per-character strict JSON prototype was slow. Native regex tokenisation passed the same adversarial controls with lower observed time; intervening changes and host load prevent a causal speedup claim. High-cardinality map scaling remains unmeasured.

## Next research slice

Freeze the real-project sampling/annotation protocol, collect bounded public histories with gh, audit feature/repair classifications and provenance, then report availability and named-project descriptive comparisons. Keep unknown agent identity and missing token traces explicit. Select real maintenance tasks for a separately scoped metered campaign only after feasibility. Existing language-development evals remain outside the primary corpus. Use new held-out real tasks when measuring roadmap changes.

The study and companion plan remain together in planned/ because the parent is multi-phase and its survey/campaign are unexecuted. Their package-completion sections distinguish delivered source from planned research; no whole-study implemented claim or registry upload.

Independent evaluation passed; its JSON is committed with the sprint state. Implementation CI run 39930266136 passed. Final completion commits change documentation/state only; consult PR checks for their exact head.
