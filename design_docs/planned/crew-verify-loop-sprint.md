# S-CREW-VERIFY-LOOP: claims, long runs and wording samples

Design: [crew-verify-loop](crew-verify-loop.md). Authorised by Mark 2026-10-12 ("yes continue").
Branch `sprint/crew-verify-loop`, stacked on PR #131. AILANG v0.54.5; prompt version v0.16.7.
Estimate about 900 changed lines, 1 day.

## M1: long sessions and allowance (crew_core, ~150 lines)
- [ ] Bank compaction on complete/cancel; tests for long runs, retries and id uniqueness.
- [ ] callLimit 0..64; watch default 12; crew-lab bounds follow.
- [ ] `crew-sim --turns 60 --seeds 1..5`: zero errors.

## M2: claims (`claims.ail`, `crew-sim --check`, ~350 lines)
- [ ] Decode/validate `crew_claims/1` against the scenario; evaluate stats; tests.
- [ ] `crew-sim --check`; `data/watch-claims.json`; `make claims-test`.

## M3: wording samples (`crew-sample`, ~300 lines)
- [ ] crew_sim keeps (bounded) the requests it heard; varied selection; library fetch.
- [ ] `crew_sample/1` lines, `--report`, `--offline`, `--max-calls`; `make sample-test`.

## M4: landing (~100 lines)
- [ ] README/AGENT/CHANGELOG (crew_core 0.1.0 amended, crew-lab 0.7.0); validate; CI; evaluation.
