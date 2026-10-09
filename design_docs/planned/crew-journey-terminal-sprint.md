# S-CREW-JOURNEY-TUI

**Status:** Authorized by attended UI instruction; ready for execution.
**Design:** [Captain's journey terminal](crew-journey-terminal.md).
**AILANG prompt version loaded:** v0.16.6, complete prompt read 2026-10-09.

Three sequential milestones; roughly 1,100 implementation/test LOC and 3 working
days with buffer, estimate rather than a promised chat wall time. The previous
presentation slice had good host tests but poor visual hierarchy; count assertions
are insufficient. Review actual screens and the newcomer flow as acceptance evidence.
No game checkout writes, package publication or live AI calls required for development.

## M1: reusable pure AILANG terminal components (400 LOC)

- `packages/terminal-ui/ui.ail`: safe text, wrapping, dimension clamp, screen/page
  composition, ANSI/plain output. Pure contracts constrain bounded numeric layout
  and page clamps. Native boundary tests and inline controls.
- `packages/terminal-ui/demo.ail`: independent IO-only interactive showcase;
  include meaningful renderer helper contracts, explicit IO effect row, inline tests
  for pure demo navigation; entry contract skip if only vacuous unit return possible,
  explain effectful shell validation in installed control instead.
- `packages/terminal-ui/ui_test.ail`, `AGENT.md`, `ailang.toml`, `CHANGELOG.md`.
- Reuse: **none**, registry terminal/tui searches returned no packages. std/string,
  std/list and std/io reused. Minimal escape/flush execution probe is prerequisite.
- AC1-3 plus native and strict quality gate; preserve honest Unicode limitations.

## M2: focused captain UI and preparation chapter (450 LOC)

- `examples/crew-lab/journey_presenter.ail`: include pure contracts for chapter/page
  bounds, explicit pure effect rows and native inline tests for milestone projection.
- `examples/crew-lab/journey_flow.ail`: include contracts expressing navigation
  preservation, pure effects and inline controls for view/page routing.
- `examples/crew-lab/play.ail`: shared publication and effectful loop; declare existing
  IO/FS/Env/AI ceiling. Shell contracts skip beyond real Result boundary invariants;
  installed controls exercise effectful entry. Existing selectReply contract retained.
- `examples/crew-lab/ailang.toml`: path dependency and new journey `[bin]` commands.
- Reuse: **depend**, existing social_dynamics/decisions/content_library via current
  host; new terminal_ui0.1.0 via path. No social/package protocol changes.
- Depends M1. AC4-7 with meaningful native navigation/projection controls and visuals.

## M3: installed experiments and independent review (250 LOC)

- `examples/crew-lab/test-journey.sh`: installed commands, plain/ANSI evidence,
  navigation-vs-baseline exact payloads, shortage/relief/start/error, journal replay.
- `examples/crew-lab/Makefile`: add new package and journey checks without duplicating
  all prior gate execution unnecessarily. Extend CI path filter if needed.
- `examples/crew-lab/README.md`, `AGENT.md`, `CHANGELOG.md`: newcomer commands and
  concrete example flows; first-contact preparation limits and UI keys + Enter.
- Reuse: **depend**, existing tests/recordings; no new testing utility package needed.
- Depends M2. AC1-8; independently evaluate rendered layout and task/state provenance.

## Delivery

Work only in `/private/tmp/stapledon-journey-tui-20261009`, branch
`sprint/crew-journey-terminal`, based on packages/main e7dd3ff. Preserve active
game/package worktrees and installed command sources until review. After independent
review and checks, the previously authorized package-main PR landing and durable
installation can proceed. Keep the original player available as a compatibility
command and provide the user one explicit new command for this interface.

Report any AILANG limitation to the canonical inbox through ailang-feedback. Core
terminal input/size capability is requested separately, not an implementation in
this packages branch. No live AI spending for tests; library + fixtures suffice.

## Implementation handoff (2026-10-09)

M1 and M2 are implemented; M3 installed evidence is complete at candidate4467372.
Final native controls:125 crew and11 terminal, evaluator and strictVM, zero failures.
Seven installed navigation/baseline journals match exactly and replay both engines;
eight compiled mutants are killed. New inline controls15passed/7generator-skipped.
Strict crew quality16/83proved/64skipped, terminal2/9proved/7skipped; neither has
uncontracted exports or a quality gate. Effectful internal `journey.ail` bin adapters
are excluded from reusable library exports; `play.launchJourney` has a meaningful
supported-mode precondition, with behavior covered by installed controls. Existing
legacy unit contracts are unchanged and are not a behavior proof.

The original full scoped validation log retains its initial PUB011 failure; final
corrected-boundary quality and installed continuation logs establish the correction.
Formatting check passes. Registry overlap DNS lookup and absent clean-workdir smoke
remain informational limitations. Independent acceptance and exact-head CI remain
pending the parent agent's landing stage. No provider calls or durable installs.
