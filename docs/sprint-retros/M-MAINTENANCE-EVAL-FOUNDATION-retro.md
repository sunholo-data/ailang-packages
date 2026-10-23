# M-MAINTENANCE-EVAL-FOUNDATION retrospective

The native maintenance evidence foundation is implemented in source. The ledger and two real-requirement component taskpacks are qualified; executor integration and actual model trials remain later work. Registry 0.1 remains published; 0.2 is a source candidate.

Planning estimated 3,700 source/test/config lines and 6–8 engineering days. The implementation adds 4,665 and removes 12 physical .ail/.py/.sh lines against the reviewed design revision: net 4,653, excluding docs/JSON/config. Those units differ slightly from the estimate; versioned native reference snapshots, independent oracles and integrity controls account for the larger scope. No source file exceeds 800 lines. Productive engineering-day velocity is unmeasured. Attended-agent elapsed time at this checkpoint is3596 seconds; it is not human-days, CPU time or a controlled productivity result.

| Workstream | Milestones | Evidence |
|---|---|---|
| Controller integration | M1/M2/M5–M8/M13/M14 | Strict scopes, lineage, staged identities, paired analysis, draft cards, reports and repository integration |
| Usage worker | M3/M4, comparison support | Neutral source contracts, exact counters/money, failure/parent/dedup laws, matched versus unmatched/overhead |
| Resource worker | M9/M10 | Native baseline+three checkpoints, 16 positives, 14 negatives, 1,136 independent assertions |
| Text worker | M11/M12 | Native logical-text/event boundary, 22 variants, 98 positive assertions, 144 intended semantic failures |
| Independent reviewer | Pre-pass and final review | Seven planted measurement issues found, corrected and rechecked; final exact-head CI/score recorded in sprint state |

Local workers owned isolated task/usage paths; integration, manifests and CI remained with the controller. No empirical parallel speedup was measured. Distinct worktrees were integrated by scoped commits; no user work was stashed, reset or switched. The original core active sprint remained untouched.

Independent review mattered: type-checking and 185 passing native tests alone would not certify the accounting/oracles. Controls caught contradictory cards, a fresh-input-only headline, missing-generation eligibility, out-of-window supported corrections, missed rename history, Python bool/int equality, overwritten evidence and inexact edit sums. These pre-acceptance instrument corrections are not cross-language defect-incidence data. Runtime/compiler/stdlib semantics were not changed.

Formatter friction was handled with private boolean helpers behind native test/property bodies, keeping all new modules format-checked. show(record) was replaced by explicit JSON for machine identities after a truncation collision control. Native lock generation intentionally preserves metadata for unchanged dependencies; this source candidate regenerated its backed-up dependency-free lock under the actual runtime. New strict object helpers stayed in the package.

Verification: 185 native tests and 500 generated cases, installed/offline integration, eight examples, strict ledger controls, bounded 1k/10k scale cases, both native qualifiers and 6 host controls/family passed. All six prior reports replayed byte-for-byte on actual locked 0.1/v0.54.17. Regular quality and packaging dry run pass; strict PUB011 / 75 uncontracted exports and 3/20 proved / 17 unsupported remain explicit. No registry upload or benchmark model campaign occurred; development-agent usage was not reconstructed from commits or treated as zero cost.

Next sprint should reuse existing executor/provider parsers for the finite stage adapter, prove worker/oracle isolation and qualify live receipt sources before a priced 8-trajectory/24-change campaign. Public source-known tasks remain development controls; broader everyday-workload claims require new prospectively sampled real requirements and family-aware uncertainty.

Final independent evaluation: **PASS90/100**, no blockers, reviewed head162db525 and successful CI39971346946. Deductions: inherited four formatter exclusions(-5), two long Python functions(-4), deliberately narrower standalone economic-card boundary(-1). Exact-head final closure CI is checked separately; no implementation code changes follow the reviewed source.
