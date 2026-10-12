# Sprint S-CREW-CORE-SPLIT: crew_core, crew-lab on JSON, crew-sim

**Design:** [crew-core-split.md](crew-core-split.md). **Authorization:** Mark, attended,
2026-10-12: keep crew-lab local; publish a lighter, composable package; retire the older front ends (D1);
tuning data before wording (D2). **Status:** Planned; awaiting approval before execution.
**Estimate:** about 1,900 changed lines over 6 milestones. That's 2–3 working days with review buffer;
much of it is moved code and deletions. Not a delivery promise.
**AILANG:** standalone v0.54.5 (crew-lab already requires >= 0.54.0). Teaching prompt loaded:
v0.16.7 (`ailang prompt --version-active`), including its JSON section.

## Velocity basis

- crew-watch-v2: estimated 2,000 lines over 3 days; actual 2,047 changed in 1 day (sprint JSON
  `S-CREW-WATCH-V2`).
- Last 7 days in `examples/crew-lab` and `packages/social-dynamics`: 31 commits, +11,583/−651
  lines (this includes evidence and recordings, so it overstates code velocity).
- The plan assumes about 700 lines a day of mixed move and new code, plus a 30% buffer, because moving
  code across a package boundary tends to reveal hidden coupling (`modern()`, the shared `codec`).

## Registry reuse (gate 0)

`ailang pkg search` for scenario, crew, narrative, "batch simulation" and "game config" found
no packages (2026-10-12).

| Milestone | Action | Package | Reason |
|---|---|---|---|
| M1 | none | — | No scenario/config package exists. The scenario format is crew-specific, so it's new code inside crew_core. |
| M2 | depend | sunholo/social_dynamics 0.3.0, sunholo/content_library 0.1.0, sunholo/decisions 0.4.0 | crew_core composes the published kernel, content selection and decisions. |
| M3 | depend | sunholo/crew_core (path) | The app consumes the new package. |
| M4 | depend | sunholo/terminal_ui 0.3.0 | The watch UI is unchanged. |
| M5 | depend | sunholo/crew_core (path) | The batch runner drives the pure session API; no new package. |
| M6 | none | — | Landing and publication. |

## Gates every milestone runs (focused; CI runs the rest)

- `cd packages/crew-core && ailang test` (both engines) and `ailang pkg quality .` with no gates.
- `make -f examples/crew-lab/Makefile validate` once crew-lab is touched (M3 onward).
- `make -f examples/crew-lab/Makefile mutations` at M4 and M6 (CI runs it).
- Keep every `.ail` file under 800 lines. `session.ail` is 35 KB on few lines, so split any
  new module before it grows past that.

## Milestones

### M1: the Scenario type and its JSON format (~400 lines, ~1 executor run)

Create `packages/crew-core/` with `ailang.toml` (`sunholo/crew_core` 0.1.0, experimental,
effects max `["IO"]` only for `_smoke.ail`) and `scenario.ail`:
`Scenario` record, `decodeScenario(string) -> Result[Scenario,string]`, `validateScenario`,
`scenarioHash` (sha256 of the canonical re-encoding). The record holds actors, OCEAN traits (0–100),
starting fatigue, stress and morale, recipes (duration, allocation, costs, effects),
worker→recipe rights, resources, names and purposes.
Follow the decoding pattern in `reactions.ail` (`fields`, `integer` and `readRules`):
exact field sets, bounded integers, named errors.

- Contracts: `ensures` on `decodeScenario` (Ok implies validateScenario is Ok) and on
  `scenarioHash` (length 64). Effects: none. Tests: round trip; rejection of an unknown recipe, a missing
  resource, an out-of-range trait, a duplicate actor id and extra fields; the hash is stable under
  re-encoding.
- Fixture: `testdata/watch-scenario.json`, generated once from `watch_scenario.ail`'s current values.
  A test asserts that decoding it reproduces `watch_scenario.actors()`, `resources()` and
  `workerRecipe` for all 5×N pairs, so nothing drifts during the move.

**Acceptance:** `ailang test` passes in `packages/crew-core`; the fixture-equivalence test passes.

### M2: move the host into crew_core and make the session take a Scenario (~450 lines, mostly moves)

Move `session`, `actor_policy`, `personality_host`, `conversations` and `codec`, plus the decoder
and scoring half of `reactions` (renamed `policy`), with their tests. Remove the `scenario` and
`watch_scenario` imports and `modern()`. `Session` gains `scenario: Scenario` and
`scenarioHash`. `start` takes the scenario. Delete the legacy `crew-<policy>-v1` scenario path:
it served only the retired front ends (D1).

**Acceptance (design 1–4):**
- `ailang publish --dry-run` in `packages/crew-core` reports `✓ no gates`.
- `/usr/bin/time -l ailang check --package .` and `verify --package . --json` each peak under
  250 MB; numbers recorded in `design_docs/implemented/crew-lab/core-split-evidence/`.
- `git grep -nE 'watch_scenario|modern\(' packages/crew-core` has no matches.
- Record `ailang check --strict-bytecode` per module (for future Godot use; not a gate).

### M3: crew-lab uses crew_core and JSON defaults (~300 lines)

- `examples/crew-lab/ailang.toml` depends on `sunholo/crew_core` by path and drops the moved modules.
- `data/watch-scenario.json` (the M1 fixture), `data/response-policy.json` (the current
  `watchPolicyBody()` output, byte-identical), and `data/conversations.json` (topics and starter replies).
- `--scenario PATH` and `--policy PATH` flags in `native_watch_args`. The defaults resolve next to the
  installed package dir. The journal header gains `scenarioHash` and `policyHash`.
- A home folder that already has `response-policy-watch-v2.json` keeps it; existing journals still
  replay.

**Acceptance (design 5, 8):** `make validate` passes; `test-short-reply.sh`,
`test-conversation-replay.sh` and `test-store.sh` pass; recordings replay byte-identically;
the new `test-scenario-errors.sh` rejects three malformed scenarios with named errors before the
first turn.

### M4: retire the older front ends; the watch stands alone (~350 lines, net negative)

- Move what `native_watch` uses from `play` (`Run`, `openWatch`, `openConversationWatch`,
  `applyWatch`, `closeWatch`) into `watch_run.ail`. Keep only the parts of `play_flow` that the
  watch routes through.
- Delete `main`, `viewer`, `terminal`, `journey*`, `play`, `presenter`, `journey_presenter`, `watch_presenter`
  if nothing uses it, and the `scenario` and `watch_scenario` modules, together with their bins (`crew-lab`, `crew-view`,
  `crew-play*`, `crew-journey*`).
- **Risk:** `test-watch.sh` and `test-native-watch.sh` launch `crew-journey-offline` for some
  controls, and `test-cli.sh`, `test-journey.sh` and `test-play.sh` cover only retired front ends.
  Port the watch-relevant assertions to `crew-watch-offline` *before* deleting anything, then remove the rest. Move the
  retired recordings to `recordings/retired/`. Update the Makefile `validate` targets and `test-mutations.py`
  to match.
- `ailang pkg bin list` shows only `crew-watch`, `crew-watch-offline` and `crew-sim` (after M5).

**Acceptance:** `make validate` and `make mutations` pass; the PTY harness
(`native-watch-pty-test`) passes; `git grep -nE 'crew-(journey|play|view)\b' examples/crew-lab`
lists only `recordings/retired/` and the CHANGELOG.

### M5: crew-sim batch tuning (~400 lines)

`crew_sim.ail` + bin `crew-sim` (caps `IO,FS`, no AI). Strategies (pure, over `Session`) are
`consent`, `orders` and `random` (seeded). They cover offer, start, relief, authority and advance.
The authored policy decides each reply, and no wording is generated. Output is one NDJSON line per seed: seed,
turns, refusals, relief granted and denied, projects completed by recipe, per-crew final
fatigue, stress, morale and trust, stock-outs, and both hashes. `--summary FILE` prints the median and
IQR per measure, with no ranking.

- Contracts: `ensures` that strategies only emit commands legal for the current session. Tests: the
  same seed gives identical output; a different trait gives different output; `--seeds 1..3`.

**Acceptance (design 6, 7):** `test-sim.sh` checks the same inputs give a byte-identical `cmp`, that changing a trait
changes the output, and that `/usr/bin/time` for 200 seeds × 24 turns is under 30 s.

### M6: evaluate, publish and land (attended)

An independent evaluator (a different agent or model) runs `sprint-evaluator`. After you approve, run `ailang publish`
in `packages/crew-core` (design 9) and confirm with `ailang pkg versions sunholo/crew_core`.
crew-lab CHANGELOG 0.5.0 (removes `[release]`; README says local only), crew_core CHANGELOG
0.1.0, then move the design and sprint docs to `design_docs/implemented/crew-lab/`. Reinstall the local
bins from the merged checkout so `~/.ailang/bin/crew-*` stop pointing at
`.ailang/cache/reviews/...`.

## Day plan

| Day | Work |
|---|---|
| 1 | M1, M2 (crew_core exists, dry-run publish clean, memory measured) |
| 2 | M3, M4 (app on JSON, front ends retired, controls ported) |
| 3 | M5, then M6 evaluation, publish and landing |

## Risks and open questions

- **Hidden coupling in `session.ail`.** If removing `modern()` or the legacy scenario breaks
  `actor_policy` or conversation context, M2 stops and the coupling is recorded; no shims.
- **Whether the move keeps memory under 250 MB** is unmeasured until M2. If it doesn't, split `policy` and
  `conversations` into a second package; don't raise the validator's limit.
- **Old homes.** Hosts written before watch-v3 already reject unknown profiles. The scenario hash is new in the
  journal; older journals have none and replay against the default only.
- **Out of scope:** background AI replies (next sprint, now unblocked by AILANG v0.54.4/5),
  narration wording as data, Godot integration.
