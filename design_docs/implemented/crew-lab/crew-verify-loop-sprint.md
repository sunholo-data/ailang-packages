# S-CREW-VERIFY-LOOP: claims, long runs and wording samples

Design: [crew-verify-loop](crew-verify-loop.md). Authorised by Mark 2026-10-12 ("yes continue").
Branch `sprint/crew-verify-loop`, stacked on PR #131. AILANG v0.54.5; prompt version v0.16.7.
Estimate about 900 changed lines, 1 day.

## M1: long sessions and allowance (crew_core, ~150 lines)
- [x] Bank compaction on complete/cancel; tests for long runs, retries and id uniqueness.
- [x] callLimit 0..64; watch default 12; crew-lab bounds follow.
- [x] `crew-sim --turns 60 --seeds 1..5`: zero errors.

## M2: claims (`claims.ail`, `crew-sim --check`, ~350 lines)
- [x] Decode/validate `crew_claims/1` against the scenario; evaluate stats; tests.
- [x] `crew-sim --check`; `data/watch-claims.json`; `make claims-test`.

## M3: wording samples (`crew-sample`, ~300 lines)
- [x] crew_sim keeps (bounded) the requests it heard; varied selection; library fetch.
- [x] `crew_sample/1` lines, `--report`, `--offline`, `--max-calls`; `make sample-test`.

## M4: landing (~100 lines)
- [x] README/AGENT/CHANGELOG (crew_core 0.1.0 amended, crew-lab 0.7.0); validate (local, keyless); evaluation.
- [ ] CI green on PR #132 and merge (after #131).

## Outcome (2026-10-12)

M1–M3 done; M4 open on CI and merge. `validate` passes locally with no provider keys.
Independent evaluation round 1: PASS 77/100
(`.ailang/state/evaluations/eval_S-CREW-VERIFY-LOOP_round_1.json`). Fixed after it:
refusal codes are a closed set (a typo no longer passes as 0); per-crew relief and reply
measures (`crew.<member>.relief_asked|granted|denied`, `crew.<member>.replies.<reaction>`),
used by three pack claims that named one person; non-string claim fields rejected;
crew-sample fails loudly when a seed cannot play; help texts no longer name the default
ship; claims tests on the strict VM too; tests for id-quoting words and for the watch
playing a non-default crew. That last test found a real bug: `isWatch` recognised only the
default ship's scenario id, so any other `--scenario` fell into a retired menu; fixed.
Known limit kept: after compaction an id of a dropped answer may be asked again (callers
never reuse ids; enforcing it would mean keeping every id).

Also delivered: a draft Stapledon scenario pack (`examples/crew-lab/scenarios/stapledon/`).
