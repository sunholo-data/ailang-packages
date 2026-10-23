# Independent sprint evaluation: M-MAINTENANCE-BENCH-PACKAGE

**PASS — 94/100.** The experimental, repeatable maintenance-analysis instrument meets the package sprint's substantive acceptance criteria. This verdict does not establish that AILANG has fewer bugs or lower lifetime token cost than another language. The comparative survey and held-out maintenance campaigns remain unrun.

## Scope and provenance

- Evaluated implementation: `d9699d5acbb437cc2c4476c570d68ab0c6f7baf5`, `sunholo-data/ailang-packages`, `packages/maintenance-bench`.
- Source PR: https://github.com/sunholo-data/ailang-packages/pull/156 (open; no main-branch or registry availability claimed).
- Required gate source: **CI**, https://github.com/sunholo-data/ailang-packages/actions/runs/39930266136. Authenticated `gh` independently confirmed successful `maintenance` job, exact matching head SHA, and mergeable PR. The CI log was inspected, rather than substituting a local full-suite run.
- Reviewer used the sprint-evaluator skill independently of the implementer, read the design, plan and sprint state, inspected source/diff/evidence, and ran targeted adversarial probes during correction. No package/source files were changed by this reviewer. Reports/reproducers live outside the source tree.
- Subsequent working-tree changes observed during evaluation are explicitly identified by the implementer as documentation/bookkeeping. This verdict binds the implementation SHA above; a later metadata commit requires its own green CI.

## Scoring

| Category | Score | Evidence |
| --- | ---: | --- |
| Tests | 20/20 | Exact-head CI: 84 passed, zero failed/skipped; two properties with 100 generated cases each. Independent analytical oracle, offline examples, smoke, installed CLI integration, Git/gh protocol integration and 1k/10k scale accounting passed. |
| Lint/format quality | 5/10 | Regular package quality has no gates. Four valid native-test modules have explicit pinned-formatter nil-expression waivers; all four still compile and execute. Production, other tests and examples remain format checked. Partial formatter coverage earns partial credit rather than an unqualified lint-clean claim. |
| Acceptance | 30/30 | All 37 substantive criteria are evidenced by source, tests, fixtures, documentation, exact-head PR/CI and this independent review. M1–M7 contain 32 criteria marked passed. M8's five criteria are evidenced but its bookkeeping intentionally awaits this verdict; no circular deduction for the review's own pending completion entry. Required closeout is listed below. |
| Code quality | 15/15 | Small, separated modules; bounded acquisition; pure analysis; typed failures; explicit unknowns/completeness; no new oversized production file or observed unresolved semantic defect. Scope limitations below remain explicit. |
| Documentation | 15/15 | Changelog, six example entrypoints, README/AGENT/schema/validation/gap documentation and package license exist. Relative package/study links checked. The parent multi-phase study remains planned, with its companion plan beside it, under the skill's multi-phase exception. |
| Design fidelity | 9/10 | Core design delivered. Minor explicit adaptations: incompatible testing_utils dependency removed in favour of native tests, a narrow formatter waiver, and declared compiler metadata requiring external runtime attestation. No hidden downgrade to heuristic bug/authorship inference or tuned generation evals. |
| **Total** | **94/100** | **PASS; no hard fail.** |

Compiler-regression conditional category is not triggered: this package does not modify shared compiler infrastructure. Performance-optimization conditional category is not triggered: this sprint builds a measurement instrument, with bounded scale accounting rather than an implementation speedup acceptance goal. Its non-comparable exploratory timings are explicitly not a verified optimization claim.

## Scientific and implementation checks

The instrument distinguishes confirmed application repairs, features, uncertain/mixed work, compiler repairs, and pre-acceptance interception. It preserves unknown authorship, attempts, usage and outcomes rather than converting missing observations into zero. Repair links require matching project/language and valid chronology. Mature/censored denominators are explicit, and raw Git committer age cannot silently stand in for accepted-change exposure. Pairing preserves model/harness/trial identity, rejects duplicate arms and reports unmatched/unknown arms. Descriptive deltas retain direction; zero denominators are unavailable; no unsupported inferential claim is emitted.

The repeat-touch requirement is implemented using structured file changes and chronological observed artifact identities, with separate confirmed repair and feature touches. Renames, copies, deletion/recreation and simultaneous rename swaps have regression coverage. This is observed history, not reconstruction of unseen creation or local edit attempts.

The analytical fixture is hand-counted and synthetic: nine eligible, eight mature, one censored, one excluded mirror; AILANG four mature/one linked repair versus Python four mature/two linked repairs gives -25 percentage points. It tests the instrument, not language superiority. The four source-attributed real cases are an incomplete recent fixture, retain unknown causal/authorship fields and do not support comparative incidence. Merge times for the Parse and Docparse cases were independently verified through `gh` rather than inferred from commit dates.

## Independent defects found and resolved

All initial material findings were addressed before this verdict; prior notes are historical, not assertions of remaining defects.

1. Report identity omitted comparison direction. Fixed; reversed comparisons now produce different identities.
2. Independent expectations allowed a duplicate group to replace another group. Fixed with unique exact repository/language/cluster coverage.
3. A fractional JSON count near the exact-integer bound could round before validation. Fixed with raw numeric-lexeme preflight; the adversarial literal `9007199254740990.5` is rejected.
4. Duplicate JSON keys allowed order-sensitive completeness. Fixed with recursive duplicate-key rejection.
5. Git committer dates could falsely create mature acceptance exposure. Fixed by explicit time basis and reviewed acceptance corrections; uncorrected commit-time cohorts are rejected.
6. Distinct paths substituted for artifact identity and repeated repair touches. Fixed with structured file changes and chronological identity/touch summaries.
7. Unknown defect identities contributed to known repair rounds. Fixed; unknown defects are excluded from known-round accounting.
8. Sequential alias mutation mishandled a simultaneous rename swap. Fixed transactionally using pre-episode aliases; the independent two-file swap repro yields two identities with two touches each.

Targeted rechecks used the current required schema so that refusal was caused by the intended predicate, not by obsolete missing fields. `recheck.py` and the `1792746226626514000` repro/output set in the review directory retain the independent cases. Exact-head CI also contains the corresponding regression tests.

## Material residual limitations

- **Strict quality did not pass.** `VALIDATION.md:11` records PUB011: **75 exported functions have no contract**. Regular quality passes and one meaningful contract is verified with zero counterexamples/errors; these facts do not imply universal proof of decoder/join/lineage correctness. Native/adversarial/oracle tests provide the principal evidence for those functions. CI permits only the documented PUB011 gate and caps the count at 75.
- `VALIDATION.md:12`: the four formatter waivers are tool limitations, not disabled tests. A future compiler/formatter version should remove them.
- `README.md:52` and `SCHEMA.md:9`: compiler identity in the manifest is declared. Campaign execution must externally attest the actual toolchain.
- `SCHEMA.md:11`: artifact history before the snapshot and ambiguous same-timestamp order are not established. Accepted history does not reveal abandoned/uncommitted model work, hidden repair rounds or complete lifetime token/cost usage.
- `VALIDATION.md:15`: scale fixtures reuse paths; high-cardinality immutable-map cost is not characterized. Single-machine timings do not demonstrate cross-language efficiency or a causal optimization.
- The broad real-life cohort, matched comparator sampling, independent annotations, and held-out maintenance/token campaigns remain research work. Existing saturated language-development evals are not used as comparative scientific evidence here.

These are nonblocking for the clearly labelled experimental instrument. They would block stronger scientific, proof-completeness or production-scale claims.

## Required closeout

After recording this verdict, the implementer should mark M8 passed/completed with notes, set sprint status completed, record actual velocity/retro and preserve the distinction between the completed package and the unexecuted parent study. Commit the evaluation report and documentation-only closeout, then require successful CI on that new head. This review does not perform a merge, registry upload or external message.

EVALUATION_RESULT: pass
EVALUATION_SCORE: 94/100
EVALUATION_ROUND: 1
GATE_SOURCE: ci
