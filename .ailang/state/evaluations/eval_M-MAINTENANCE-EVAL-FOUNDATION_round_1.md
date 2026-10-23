# Independent sprint evaluation: M-MAINTENANCE-EVAL-FOUNDATION

**PASS — 90/100. No blocking defect remains in the evaluated foundation.** This approves the experimental source candidate's ledger and qualified public task assets. It does not establish an AILANG bug-rate or lifetime token-cost advantage, and does not approve a model campaign, registry upload or merge.

## Evaluated revision and independent gate

- Repository/PR: https://github.com/sunholo-data/ailang-packages/pull/160, `sprint/maintenance-eval-foundation`.
- Exact evaluated head: `162db5255f3b75d7d3ee2a309607b9ea0bf3c649`.
- Analysis implementation/source pin: `40e1e74932a6e6860030d8fca5d78bba2b49248f`; the later evaluated commit adds externally source-pinned real-report provenance.
- **Gate source: CI.** [Maintenance run 39971346946](https://github.com/sunholo-data/ailang-packages/actions/runs/39971346946) completed **successfully** at the exact head above. Authenticated `gh` independently confirmed the head, all job steps, successful conclusion, and mergeable open PR. CI log inspected and retained outside source. No local full-suite substitute or whole Go suite was run.
- Read-only independent reviewer applied the sprint-evaluator skill, reviewed both designs, approved plan/state, implementation/evidence and amendments. Earlier v0.1 approval was not reused as this sprint's verdict. No implementation files/shared state, models, coordinator inbox or external publication were changed by the reviewer.

## Score

| Category | Score | Concrete evidence/deduction |
| --- | ---: | --- |
| Tests | 20/20 | Exact-head CI: 185 native tests passed, zero failed/skipped; five properties × 100 cases. Compile/examples/smoke/oracle, installed commands, ledger/Git/gh integration, both native taskpack qualifiers,1k/10k accounting, quality and packaging passed. |
| Lint/format quality | 5/10 | Four inherited native-test formatter exclusions remain explicitly limited; tests still compile/execute and no new waiver was added. This is partial format coverage, not an unqualified lint-clean result. Regular required gates pass; strict limitation is separately stated below. |
| Acceptance | 30/30 | All 45 substantive criteria evidenced. M1–M13 mark 41 criteria passed. M14's four criteria have actual quality/PR/CI evidence and this independent evaluation; post-verdict bookkeeping is not circularly treated as missing implementation. |
| Code quality | 11/15 | Bounded, separated pure analysis and effectful adapters; no source file exceeds 800 lines or new TODO/HACK/FIXME observed. Rubric deducts2each for resource `oracle.py:17` validate, 82 lines and resource `references/s3/python/main.py:12` run, 52 lines. Both contain cohesive nested helpers; nonblocking opportunities to shorten control flow. |
| Documentation | 15/15 | Versioned changelog, manifests/locks, eight package examples, native task examples, AGENT/schema/validation/gap/protocol/stage docs and actual qualification receipts exist. New local doc links resolve. Parent designs correctly retain unexecuted runner/campaign phases. |
| Design fidelity | 9/10 | Ledger/scopes/accounting/pairs and two native families delivered. Standalone economic-card qualification was deliberately narrowed to require bound controlled reports; cards remain attested review drafts. This is a justified, explicit deviation from the broader proposed card boundary. |
| **Total** | **90/100** | **PASS; threshold 70, no hard fail.** |

Shared-compiler regression category is not triggered: no compiler/parser/typechecker/runtime/core-executor implementation is modified. Performance-optimization category is not triggered: this is a measurement foundation, not an implementation speedup sprint. Scale accounting is exercised; no verified optimization or language-speed claim is made. CI's descriptive1k/10k timings were2,025/20,735ms and are not pooled with local-machine timings.

## Verified behavior and evidence boundaries

The explicit index partitions selected changes into mature/censored/unresolved/excluded populations without allowing ordinary later work to enlarge that denominator. Reviewed intent is distinct from an introduced-defect link. Follow-up windows, rename-aware observed artifact identity, workload and missing tokens are named separately. Source exhaustion does not establish defect ascertainment; no clean-program count is inferred by subtraction. Git history cannot reveal complete local edits/attempts.

Neutral receipts preserve original source/contract identity, knownness, cache/reasoning scheme and decimal currency/basis. Inclusive/exclusive arithmetic agrees on fresh 50, generated 10, accounted 160 and fresh+generated 60. Combined output is not charged reasoning twice. Leaf requests are charged once; parent integrity, ambiguous overlap, mixed cost bases, failed retries, preparation/infrastructure and unmatched work remain visible. Missing generation withholds the token headline; incomplete cost/identity/outcomes withhold affected economic comparisons. Zero successes is unavailable. Invented accounting-control amounts are explicitly not observed model spend.

The finite ledger validates every scheduled stage, its own retained artifact, matching stage/oracle and attempt identities. It separates failed, blocked, invalid, budget-stopped and never-started states, as well as visible checks and independent oracle verdicts. Matched arms preserve family/variant/repeat/protocol/settings/provider constraints and retain unknown/unmatched arms. Repeated families are not promoted to independent populations.

Both task families execute native AILANG and Python components with shared bounded responsibility, competent starters and externally specified semantic obligations. Qualification uses fresh build directories and successful compilation/execution before counting semantic negatives. Resource controls passed 16 positive runs and 14 negative executions (12 public-green), with 1,136 assertions; text controls passed 98 reference assertions and 144 deliberate assertion failures across 22 variant sets. Six host-oracle tests per family passed. Neither family is a historical Python repair or sealed holdout. Actual executor isolation and a model campaign remain future work.

The native Parse replay is a separate observational result: 3 selected mature changes, 14 later touch changes, 1 confirmed repair touch, 13 unknown-intent touches; workload 53 rows with 3 known token rows totaling1,114,042 and 50 missing. It is not a 1/3 language bug-rate estimate or a controlled language comparison. Frozen mature/pilot paths have no changes; independent old-toolchain replay records six byte-identical reports.

## Independent adversarial review

Seven material pre-pass issues were corrected before this verdict:

1. Contradictory/unbound card identities and economic promotion: immutable/distinct IDs validated; standalone economic claims refused.
2. Dropped generated-token component: aggregate/report freshGenerated; unknown output blocks headline, input-only remains diagnostic.
3. Out-of-window supported correction: bounded follow-up inclusion applied.
4. Rename/post-rename touch loss: shared observed artifact lineage used; copy/delete/recreation policy explicit.
5. Python bool/int equality loopholes: type-aware oracle comparison in both families, with planted controls.
6. Qualification evidence overwrite: F1 exclusive creation and pre-execution overwrite refusal; default qualifier is offline, package-quality lookup separate.
7. Local edit precision overflow: exact bounded aggregation refuses excess before JSON serialization.

Independent recheck passed nine direct CLI probes and four small host tests. Exact-bound acceptance, intended overflow refusal, missing-output withholding, direct rename and subsequent edit were tested separately. Repro records remain in `/private/tmp/maintenance-foundation-review/targeted-recheck-1792765933290264000.json`; historical initial outputs document the defects, not their continued presence. Final CI exercises the amended native/host controls.

## Proof, identity and residual limitations

**Strict quality did not pass.** Main package evidence is 3/20 SMT contracts verified under the encoded model, 17 unsupported-encoding skips, zero counterexamples/errors and 75 uncontracted exports. PUB011 remains the sole permitted strict gate, at its unchanged ceiling 75. Unsupported encodings are not proofs; runtime-contract execution coverage is unmeasured, and numeric-model/runtime equivalence is not established. Taskpack cap/edge predicates are narrow proofs, not proofs of FS ownership or whole-program correctness.

Report IDs bind raw inputs, declared package/metric/compiler identity, section/role and protocol/direction via input digests. They do not attest their own source or actual runtime. For this source-candidate scope, the external exact implementation commit/lock/compiler provenance is sufficient and explicitly documented. The recorded lock SHA matches the checkout; actual local compiler binary SHA matches provenance; pinned real report ID matches its provenance record. Both qualification records match current amended oracle/qualifier/protocol hashes. A report ID alone must not be used as a self-attesting build signature.

Other residuals: four inherited formatter exclusions; observed-history/same-timestamp ambiguity; incomplete real-world ascertainment and usage; exposed development cases; tiny correlated family set; no protected worker/oracle boundary or staged model adapter yet. These prevent stronger scientific/proof/production claims but do not block this foundation candidate.

## Closeout

Record this verdict, complete M14 and sprint state/notes/timestamps, retain honest actual-velocity limits and retrospective, and correct the plan's stale historical `execution_authorized=false`/unstarted paragraph. The implementer reports that correction is already staged as documentation-only closeout. Keep planned downstream phases explicit. Commit evaluation and bookkeeping, then require green CI on that new head; this exact-head verdict does not predeclare a future CI result. Reviewer performs no merge or registry publication.

EVALUATION_RESULT: pass
EVALUATION_SCORE: 90/100
EVALUATION_ROUND: 1
GATE_SOURCE: ci
