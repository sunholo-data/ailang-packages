# Real-world maintenance evidence and proposed eval

The package `sunholo/maintenance_bench@0.1.0` is published. [PR #157](https://github.com/sunholo-data/ailang-packages/pull/157) merged the real-project studies. Existing language-development evals are excluded from this evidence corpus.

- [Availability pilot](pilot-2026-10-23/README.md): why the recent-closed-PR selector cannot establish mature defect rates.
- [Mature study](mature-2026-10-23/README.md): 1,114,042 recorded maintenance-task tokens, one reproduced AILANG causal regression, a reproduced Rust regression, and a small descriptive touch comparison. No demonstrated language-wide bug or lifetime-cost advantage.
- [Study protocol](../../design_docs/planned/m-real-world-language-maintenance-study.md): observational sampling and claim boundaries.
- [Proposed task pack](../../design_docs/planned/m-maintenance-eval-taskpack.md): two real-requirement families, three successive maintenance changes, paired native starter qualification, independent oracles and an opt-in eight-trajectory pilot.
- [Proposed evidence ledger](../../design_docs/planned/m-maintenance-bench-evidence-ledger.md): explicit index/follow-up/workload scopes, honest usage normalisation and evidence-linked roadmap cards.

## Candidate roadmap order

| Item | Evidence | Readiness / next action |
|---|---|---|
| Scope and usage ledger | Excluded-smoke denominator mismatch; repo query misses recoverable tasks; legacy cache/billing unknown | Design drafted; review before sprint planning |
| Real maintenance task pack | Historical ownership and text-fidelity oracles fail before / pass after | Design drafted; qualify both starter arms and scripted stages before a model campaign |
| Resource ownership helper/oracle reuse | Parse #46 introduced file aliasing; #77 already fixed the application | Candidate reuse audit, not an assumed stdlib deficiency or unshipped application repair |
| Resource-authoring diagnostics/guidance | Historical quadratic assembly and frame-retention jobs consumed substantial recorded tokens | Replicate/profile on current pinned tools before choosing an AILANG diagnostic or Motoko extension |
| Requirement-specific invariant coverage | Correct types and existing tests did not reject the two reproduced semantic defects | Develop exact ownership/text-preservation checks; expose these cases only as development evidence |

The eval emits auditable evidence cards, not automatic feature approval. A card must name the failed requirement, reproduction, source/run/oracle identities, cost coverage, recurrence and existing-capability audit before it supports a roadmap design. The resulting design still follows its repository's approval and sprint workflow. A negative result or an application-only fix can be the correct roadmap outcome.

No new model campaign, package implementation or compiler/stdlib behavior is included in these design proposals. The proposed first pilot measures maintenance of existing starters; initial application generation belongs to a separately identified follow-on cohort.
