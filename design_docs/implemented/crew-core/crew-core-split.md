# crew_core: a publishable captain/crew host, with the scenario as data

| Game pillar | Alignment | Constraint |
|---|---:|---|
| Choices Are Final | +1 | The journal and replay rules move unchanged; the scenario hash joins the run identity, so a replay cannot silently use different tuning. |
| The Game Doesn't Judge | 0 | No score is added. The batch report lists outcomes side by side and never ranks policies. |
| Time Has Emotional Weight | 0 | Turn mechanics are unchanged. |
| The Ship Is Home | +2 | The same crew host can later run inside the Godot simulation, so the crew the player communicates through is the one tuned here. |
| Grounded Strangeness | 0 | No content change. |
| We Are Not Built For This | +1 | Fast batch runs let fatigue, stress and refusal be tuned against many seeds instead of one play-through. |

Scores are provisional; rescore with `game-vision-designer` before sprint planning.

**Status:** Implemented 2026-10-12 (S-CREW-CORE-SPLIT, ailang-packages #129, #130); crew_core first published as 0.3.0.
**Target:** `sunholo/crew_core` 0.1.0 (new, published) and crew-lab 0.5.0 (stays local,
never published). **Priority:** P1.
**Direction (Mark, 2026-10-12):** a good way to make narrative and social games, with
quick iteration and AI elements. In order: tuning data first, then background AI replies, then wording as data.
**Estimate:** four milestones, about 2–3 development days; not a delivery promise.

## Authorization and problem

Mark decided on 2026-10-12 that crew-lab stays a local app and is not published, and
asked for something lighter and more composable that can be published. Facts measured on
crew-lab 0.4.1 (main `75ecc46`):

- Publishing it returns HTTP 503 because the registry validator runs out of memory: its
  limit is 512 MiB, and `ailang check --package .` alone peaks at 351 MB locally (social-dynamics
  153 MB, terminal-ui 73 MB, decisions 76 MB).
- It has 48 `.ail` files: 25 modules (about 250 KB) plus 23 test files. About 146 KB of the modules are three
  generations of front end (journey, play, watch). 25–53% of each presenter file is quoted wording.
- The reusable host logic is tied to one scenario. `session.ail` imports both `scenario` and
  `watch_scenario` and switches between them by config id (`modern(s)`). Crew members, OCEAN traits,
  recipes, resources and names are Ailang literals.
- One precedent works already: the response policy is the JSON file
  `response-policy-watch-v2.json` (schema `crew_response_policy/1`). It's created from a default
  on the first run and read back on later runs (`store.ail:108`).
- Offline play is fast: 0.8 s to start, 1.5 s for an 8-input watch. Tuning is slow because
  each change to the logic or numbers means editing Ailang, a full recheck (18 s) and a reinstall,
  then a hand-played watch to see the effect.

## Design

### 1. `packages/crew-core` → `sunholo/crew_core` (published, pure)

Effects: none in the public API (`max = ["IO"]` only for a private `_smoke.ail`, as in
social-dynamics). Dependencies: `social_dynamics`, `content_library`, `decisions`.

| Module | From | Change |
|---|---|---|
| `scenario` | new; data from `scenario` + `watch_scenario` | `Scenario` record (actors, OCEAN traits, starting values, recipes, worker→recipe rights, resources, names, purposes), `decodeScenario(string) -> Result[Scenario,string]`, `validateScenario`, `scenarioHash` |
| `session` | `session.ail` | Every scenario lookup reads `s.scenario`; `modern()` and both scenario imports are removed. `start` takes a `Scenario`. |
| `policy` | `reactions.ail` (decoder + scoring only) | The default policy wording moves to JSON; there is no hardcoded default policy. |
| `actor_policy`, `personality_host`, `conversations`, `codec` | as is | Import paths only. |

Not in the package: `store` (FS), every presenter, flow and UI module, `narrative`
(the player-facing text). Tests come along with their modules and use small fixture scenarios written inline.

The package doesn't read files or assets. The caller decodes the scenario JSON and
passes the value in. The app reads a file; the Godot simulation could send it over NDJSON.
That keeps the host pure and deterministic. It also avoids `std/package.assetPath`, which picks
the most recent *installed* version lexically, not the locked one (report this upstream).

### 2. crew-lab 0.5.0 (local only)

- Depends on `crew_core` by path. Its default data lives in `examples/crew-lab/data/`:
  `watch-scenario.json`, the existing `response-policy-watch-v2.json` default, and
  conversation topics and starter replies.
- `--scenario PATH` and `--policy PATH` override the defaults. The journal header records both hashes.
- Untangle the watch from `play.ail`: `native_watch` currently imports
  `play (openWatch, applyWatch, ...)`, which pulls in journey and play presenters. Move the
  watch's run loop into a `watch_run` module.
- Front ends: keep `crew-watch` and `crew-watch-offline`. Retire `crew-lab`, `crew-view`,
  `crew-play*` and `crew-journey*` (D1). Their recordings move to `recordings/retired/` as history;
  replay tests that only cover retired front ends are removed along with them.
- Set `[release]` aside and add a README note that the example is local only.

### 3. `crew-sim`: batch tuning without AI (in crew-lab)

```sh
crew-sim --scenario data/watch-scenario.json --policy data/policy.json \
         --captain consent|orders|random --seeds 1..200 --turns 24 > runs.ndjson
crew-sim --summary runs.ndjson      # medians and spreads per measure, no ranking
```

The captain strategies are small pure functions over `Session` that choose offers, starts,
relief and authority. Replies use the authored policy draw only, with no wording generation. Each
line is one seed: refusals, relief requests granted and denied, projects completed, final
fatigue, stress, morale and trust per crew member, and resource stock-outs.
Same inputs give byte-identical output.

## Acceptance criteria

1. `cd packages/crew-core && ailang publish --dry-run` reports `✓ no gates`.
2. Peak memory for `ailang check --package .` and `ailang verify --package . --json` in
   `packages/crew-core` is each under 250 MB (`/usr/bin/time -l`, recorded in evidence).
3. `ailang test` passes in `packages/crew-core` on both engines (the VM and the interpreter), with the same results.
4. `git grep -nE 'watch_scenario|modern\(' packages/crew-core` has no matches.
5. In `examples/crew-lab`, every installed test script that exists today passes against the
   JSON defaults (`test-native-watch.sh`, `test-watch.sh`, `test-conversation-replay.sh`, the PTY
   harness). The existing recordings replay byte-identically.
6. Changing one trait in a copy of `watch-scenario.json` changes `crew-sim` output for a fixed
   seed, and the original file reproduces the original output byte-for-byte (`cmp`).
7. `crew-sim --seeds 1..200 --turns 24` runs in under 30 s offline.
8. A malformed scenario (an unknown recipe, a missing resource, an out-of-range trait) is rejected
   with a named error before the first turn (`test-scenario-errors.sh`).
9. After the attended review, `ailang publish` for `sunholo/crew_core` 0.1.0 succeeds and
   `ailang pkg versions sunholo/crew_core` lists it.

## Milestones

1. **crew_core extraction.** Add the `Scenario` type, its decoder and validator, and the parameterized session; move the logic tests. (Criteria 1–4)
2. **crew-lab on JSON.** Add the data files, the flags and the journal hashes, and split `watch_run` out from play. (Criteria 5, 8)
3. **crew-sim.** Add the strategies, the NDJSON output and the summary. (Criteria 6, 7)
4. **Publish crew_core (attended).** Land the change.

## Decisions

- **D1, answered yes (Mark, 2026-10-12).** Retire the older front ends; keep only the watch.
- **D2, answered later (Mark, 2026-10-12).** Tuning data comes first; narrator and UI wording
  move to data in a later pass.

## Next: background AI replies (a follow-on sprint, not this one)

The approved design `crew-reply-inbox` (2026-10-10, approved by Mark) lets the captain keep
playing while crew replies are generated, and allows several replies to be fetched in parallel.
Its M1 gate failed on AILANG v0.52.0: background workers outlived the host process. AILANG
v0.54.4 (M-BACKGROUND-WORKER-LIFECYCLE) and v0.54.5 (M-WORKER-FOLLOWUP) fix this. On
2026-10-12, the original repro was rerun on v0.54.5. In both cases (`asyncExecProcess` with
`selectEvents`, and `spawnProcess` with `closeProcessStdin`), the worker was live before the
quit and absent after the host exited. `std/process.cancelProcess` and
`std/stream.cancelProcessSource` now provide the explicit cancellation the design needed.

This split keeps that path clean. `crew_core.session` already models replies as pending
requests: `ask` adds a `Request` that carries its frozen context and revision, and
`complete(s, id, body, roll)` resolves it later. So the inbox is purely an app-layer
worker pool that turns pending requests into `complete` calls, and it needs no core change. It can also prefetch the
wording for likely next requests while the player reads. That's safe because a request's
context is frozen and checked against the session revision, so a stale prefetch is discarded,
not applied. After crew_core lands, bring `crew-reply-inbox.md` into this repo, rerun its M1 gate
on the pinned v0.54.5, and plan M2–M4 against the crew-watch app.

## Out of scope

- Wiring `crew_core` into the stapledons-godot simulation. That needs its own design doc there and a
  strict-bytecode check. M1 records whether `crew_core` already passes `--strict-bytecode`.
- Background AI replies: the next sprint (see above).
- Raising the validator's memory.
