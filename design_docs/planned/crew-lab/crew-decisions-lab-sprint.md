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
