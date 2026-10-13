# A verification loop for crew tuning: claims, long runs, wording samples

| Game pillar | Alignment | Constraint |
|---|---:|---|
| Choices Are Final | 0 | No rule change; replay and determinism unchanged. |
| The Game Doesn't Judge | +1 | Claims state what the designer expects of the simulation (trust erodes under orders); they never score the player or rank captains. |
| Time Has Emotional Weight | +1 | Runs can last a voyage-length number of turns, so slow drift (fatigue, trust) can be checked. |
| The Ship Is Home | +2 | Crew wording is sampled across situations and reviewed before it reaches the game. |
| Grounded Strangeness | 0 | No content change. |
| We Are Not Built For This | +1 | Strain thresholds become checkable statements instead of impressions. |

**Status:** Planned 2026-10-12; Mark: "yes continue" to the proposed verification-loop sprint,
with game integration to follow once the loop is good.
**Target:** `sunholo/crew_core` 0.1.0 (still unpublished; amended before its first publish) and
crew-lab 0.7.0 (local only). Stacked on PR #131 (crew-lab 0.6.0).

## Problem

Tuning today means reading `crew-sim --summary` and judging by eye; an agent can't say whether
a change did what was intended. Sessions refuse new answers after 64 (about 12 turns). Nothing
samples the AI wording for review. The AI allowance per watch is at most 8 calls.

## Design

1. **Long sessions (crew_core).** The answer bank keeps idempotent retries and unique ids. A
   request expires one turn after it is asked, after which a retry can never be applied, so when
   the bank reaches 64 the session drops answers whose requests have expired (oldest first) before
   adding the new one. A retry of a dropped answer reports `unknown request` instead of a no-op;
   ids are unique among retained and pending requests (the watch and crew-sim never reuse ids).
2. **Allowance.** `crew_response_policy/1` `callLimit` may be 0..64 (was 0..8); the watch policy
   default rises from 6 to 12 so prefetch (reserve 3) has room. crew-lab bounds follow.
3. **Claims (`crew_claims/1`).** A JSON list of expectations, each about one captain:
   `{"id","captain","metric","stat","op","value"}` where `stat` is median, mean, min or max, or
   `{"stat":"share","when":{"op","value"}}` for the share of seeds meeting a condition. Metrics are
   paths in `crew_sim/1` lines (`crew.medic.trust`, `refused`, `relief.denied`, ...), validated
   against the scenario (unknown crew, indicators or fields are rejected, so a typo can't pass as 0).
   `crew-sim --check claims.json [--scenario F] [--policy F] [--seeds A..B] [--turns N]` runs each
   captain once per seed, prints one line per claim (PASS/FAIL, observed value) and exits 1 if any
   fail. `data/watch-claims.json` records what the default ship is known to do.
4. **Wording samples.** `crew-sample` plays the consent captain without AI, collects the requests
   crew members were asked and their authored reactions, picks a varied subset (distinct crew and
   reaction first), and fetches words through the same library and prompts as the watch, within
   `--max-calls` (saved words are free). Output: one `crew_sample/1` line per sample (crew member,
   project, reaction, fatigue/stress/morale at the time, words, source, calls, the narrative check)
   and `--report` for reading. `--offline` uses authored words (tests, no provider).

## Out of scope

Automatic judging of prose quality, game integration, the AILANG bump in the game (v0.52 to
v0.54.5; its own sprint), publishing crew_core (attended).

## Acceptance (commands)

- `make -f examples/crew-lab/Makefile core-tests`: compaction tests (100+ answers across turns,
  retries before compaction still no-ops, ids unique among retained/pending), callLimit 0..64.
- `crew-sim --turns 60 --seeds 1..5` has `errors == 0` in every line.
- `make -f examples/crew-lab/Makefile claims-test`: the shipped claims hold for the default ship;
  a deliberately changed ship makes a named claim fail with exit 1; malformed claims and unknown
  metrics are rejected.
- `make -f examples/crew-lab/Makefile sample-test`: offline samples are varied, bounded and
  deterministic; with the AI stub, rejected words are reported and calls are counted.
- `validate` green locally and in CI; independent evaluation.
