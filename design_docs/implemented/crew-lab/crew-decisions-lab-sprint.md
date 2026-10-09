# CREW-DECISIONS-LAB sprint

Base packages/main5d01829. Isolated branch, new example only. Mark selected the
crew CLI and instructed continue following JEV integration proposal: saved synthetic
decisions only; no live calls, game edits, registry publication or demo changes.
Independent design quorum (2026-10-09): review_a PASS, review_b PASS after one
revision. Remaining risks consent-guard bypass and transaction atomicity have tests.
Both refusal policies remain labelled experiments pending user steering.

| Milestone | LOC | Dependencies | Acceptance |
|---|---:|---|---|
| M1_POLICY | 300 | none | Strict typed answer, confidence, normalized endpoints and exact codec controls |
| M2_HOST | 450 | M1 | Bound consent, private requests, stale/retry/cancel and atomic failure controls |
| M3_CLI | 250 | M2 | Five traces, interpreter/strict VM parity, replay and installed CLI controls |
| M4_EVALUATE | 200 | M3 | Strict quality, existing lab regression and independent final evaluation |

Total estimate1,200 LOC/four working days; not attended-session duration forecast.
M1 reuses decisions0.4.0 request/parser/gate; M2 social_dynamics0.1.0 lifecycle;
M3 repository runner patterns; M4 native test/quality tools. Registry search/API
verification is in design V1–V8. Runtime0.52.0/bf2436a, teaching prompt0.16.6.
Pure contracts and inline examples; proofs and runtime assertions reported separately.
Test-first; executor skill permits delegating independent policy/codec modules.
Final judge must not have implemented any code. Run scoped Makefile validate and
existing social lab regression; retain actual totals, skips and limitations.

Execution evidence: 56/56 native tests on evaluator and strict VM, no skips or
fallbacks; seven scenario-source inline checks; five complete paths replay and
match across engines; installed CLI works from another cwd. Eight compiling
mutants killed. Original kernel110 and consumer8 plus five original paths pass.
Only regression-generated lock timestamps were restored to baseline; original
sources and signatures remain unchanged. Actual code/test/harness LOC1,485.

Solver:5/28 verified,22skipped,one encoding error for function-valued Policies,
zero counterexamples. Strict quality has no gates, with informational no isolated
publishing smoke because social kernel remains a local unpublished dependency.
Installed CLI boot checks cover the repository graph. This is not a registry release.
Scoped CI workflow adds these CLI gates without building the game; remote CI result
is separately recorded at landing. Final independent evaluation is pending.

Independent final evaluator: PASS100/100, no blockers. Added readable crew-view
at Mark's request; installed-wrapper controls pass for all five paths and malformed
inputs. Cancellation is shown as a host action without a fabricated response/roll.
Cold recorded six-command process: interpreter1.45s, strictVM1.40s on this machine;
not a cross-machine performance guarantee. Full evidence in accompanying folder.
