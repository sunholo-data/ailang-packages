# Sprint S-CREW-NATIVE-UI

**Status:** Completed and accepted, 2026-10-10; approved by Mark before execution.
**Design:** [crew-native-ui.md](crew-native-ui.md).
**Visual:** [crew-native-ui-mockup.txt](crew-native-ui-mockup.txt).
**Goal:** Make the five-person preparation watch readable and enjoyable with pure
AILANG native arrow controls, terminal graphics and visible decision consequences.
**Duration:** three development days, 1,800 changed lines, medium risk; CI and
independent review add elapsed time. No new AI concurrency or cleanup implementation.

## Current state and velocity

Watch-v2 implemented five specialists, three concrete resources, qualitative
personality presentation and preserved legacy journeys. PR119 subsequently fixed
Start/Decide later wording. Native terminal PR117 is merged with successful crew
CI; core PR1756 and official AILANG v0.54.0 released. Registry search/info/docs on
2026-10-10 confirm terminal_ui0.2.0 is published; older VALIDATION.md's pending
registry wording is stale evidence, not a current blocker. Installed demo uses
registry0.2 and localv0.54.0; root compiled12files and reran39tests on released runtime.

Previous watch sprint recorded 2,047 changed lines in one calendar day (including
tests/docs), while its original estimate was 2,000 over three days. Reply-inbox M1
spent substantial effort on lifecycle evidence and correctly stopped on a hard
runtime gate. Those are poor grounds for promising a one-day UI delivery. Plan at
600 changed lines/day, including controls/review buffer;1,800 total across three days.

## Mandatory registry reuse

Search `ailang pkg search terminal` returned sunholo/terminal_ui0.2.0. Inspect
`ailang pkg info sunholo/terminal_ui` and `ailang pkg docs sunholo/terminal_ui`:
ui/events/widgets/transcript are pure, adapter is IO, native requires v0.54.0.

| Milestone | Decision | Package and reason |
|---|---|---|
| M1 | depend | terminal_ui0.2.0: existing cells/wrap/pad, selection and viewport. Graphics are app projections; no generic package needed. |
| M2 | depend | terminal_ui0.2.0: choose/run/readInput/writeFrame with scoped terminal restoration and one input owner. |
| M3 | depend | terminal_ui0.2.0: exercise the same published API in installed PTY and plain flows. |

Development may use the existing sibling path source; publication must pin exact
registry0.2.0 and validate a clean registry consumer. Retain existing social_dynamics,
content_library and decisions dependencies and all domain authority boundaries.

## Syntax and demonstration evidence

**AILANG prompt version loaded: v0.16.7**, using official v0.54.0 `ailang prompt`
and `ailang prompt --version-active`. Executor reloads the complete prompt at start.

| Showcase module | Contracts | Effects | Inline tests |
|---|---|---|---|
| native_watch_ui.ail | include: bounded cursor; navigation/resize/no-input retain session and emitted command None | include: `! {}` | include: empty/menu bounds, resize and safe initial decision examples |
| native_watch_presenter.ail | include: frame rows/cells within measured viewport; progress0..size helper | include: `! {}` | include: progress0/half/full, tiny terminal, facts vs qualitative descriptions |
| native_watch.ail | skip: user-driven effectful host has no decidable total-run contract; pure helpers above carry invariants | include: `! {IO,FS,Env,AI}`; bounded per-operation adapters, no Clock/Process/Stream | skip: entry loop needs IO; pure inline controls above and installed harness cover it |

Pure named controls must run interpreter and strictVM without fallback. Effectful
adapter/demo uses interpreter because @limit frames are not VM-supported; preserve
budgets. Report actual native/inline counts, skips and Z3 errors separately.

## M1 — Pure UI and graphical information (700 lines) — completed

Estimated450implementation +250controls; day1. Depend on published widgets and
current watch domain, not worker lifecycle. Files: examples/crew-lab/native_watch_ui.ail,
native_watch_presenter.ail, corresponding *_test.ail and sample frame fixtures.

Tasks: create closed view/action UI state; map stable numbered intents; explicit
safe default for proposal decisions; introduction and contextual help; ship schematic,
five-person roster, physical inventory and elapsed-work bars; responsive80x24/40x16
and tiny layout; pure invariant controls. Example fixtures show empty bridge,
agreed offer, two simultaneous jobs and a named capacity shortage.

Acceptance NU1–3/6: actual rendered frames retain highlighted option and consequences;
browsing cannot affect state/RNG/attempts/journal; fivecrew and exact speech reachable;
no numeric psychology in normalmode. Commands: new native-ui-test target and
existing native/strictVM package tests. Verify pure helpers; report proof boundaries.
Risk: dense chrome; reduce schematic before reducing action readability.

## M2 — Native play adapter and additive commands (600 lines) — completed

Estimated400implementation +200controls; day2, afterM1. Files: native_watch.ail,
ailang.toml/lock, Makefile, test-native-watch.sh, focused PTY harness.
Working examples: installed crew-watch-offline --mode auto; line/plain transcript
with blank input; documented real-model command crew-watch --mode auto.

Tasks: scope adapter.run; one input source; measured resize/Idle; explicit mode
and --ascii selection; quit confirmation/Escape semantics; preserve ongoing decision
through Crew/Work/Log/Guide; reuse exact existing offer/start/advance/relief machinery.
Add [bin] crew-watch/crew-watch-offline; preserve oldcommands. Handle stale host
rejections in-place; truthful synchronous pending screen; no worker API changes.

Acceptance NU4–6: immediate keys, exact blank/EOF semantics, measured tiny mode and
restoration on normal quit/Ctrl+C/injected failure. Installed offline four-turn
science completes, returnsslots, shortage preservesoffer and explanation. Commands:
native-watch-test and native-watch-pty-test. Current app and library scoped regressions
pass. Risk: input-owner conflicts; no secondstdinreader/no selectEvents host.

## M3 — Actual play evidence, documentation and landing (500 lines) — completed

Estimated100implementation/docs +400harness/fixtures; day3, afterM2. Files:
test-native-watch-pty.py (test harness only), Makefile, README, AGENT, CHANGELOG,
two walkthrough recordings and native-ui-evidence. Examples: cooperative science
with competing capacity; authority/objection and a relief choice.

Tasks: run installed realPTY resize80x24→20x8→40x16→100x30 while proposal selected;
assert no accidentalstart/time; test Cursor/alternate-screen/termios restoration;
offer/start/progress/completion/resourcefailure/relief playthrough; line/plain/ASCII;
oldjournals/policy/cache checksums; complete existing validate and CI. Hand to a
different evaluator as project rules require; address blockers before main landing.

Acceptance NU1–8: every behavior above produces evidence, no false location/deadline
claims, no backgroundAI claim. Commands: all three new targets, existing validate,
quality inventory and independent evaluation. Effects interpreter explicitly;
puretests strictVM zero fallback. Preserve current model; automated tests use stub/
cache/authored content, zero external provider calls. Installonlyadditivecommands
from durable ownedsource/runtime after greenCI/acceptance; clean registry smoke.
Risk:20–45minute composedgates; retain60minuteCI rather than lowering requirements.

## Success, resumption and boundaries

Complete when installed native play explains each choice, renders facts accurately
at actual sizes, protects domain determinism, restores the terminal, preserves old
commands/cache, and has passing independent acceptance and CI. No percentage
coverage claim without measurement. No gamebuild/globalruntime bump. No changes in
other agents' worktrees; source lives in /private/tmp/crew-native-ui-20261010 until
durablelanding. Before execution fetchmain and reconcile only this ownedcheckout;
do not reset other ongoing work. No cloud messages or public normative doc push is
needed to approve the UI. Prior reply-inbox approval is separate and remains gated.

Progress: `.ailang/state/sprints/sprint_S-CREW-NATIVE-UI.json`, all milestones passed.
Executor watch_executor and independent judge watch_design_review_a completed their
separate roles. Full local validation and exact-head CI38073025460 passed at667491a;
PR120 merged as02c8042. Two additive durable launchers passed actual installed smoke;
five old commands and four sampled policy/cache files retain original checksums.
Frozen implementation changed1,714 lines (1,704 insertions/10 deletions) in one
calendar day against1,800 over three estimated development days; elapsed working
hours were not measured. See design completion evidence for proof/VM limitations,
registry consumer scope and truthful synchronous AI. Final metadata is a separate
docs-only landing; it does not replace the tested source revision. Normative roadmap
publication remains subject to outstanding destination/content approval.

## Corrective acceptance: raw terminal row alignment

Mark's real terminal screenshot on2026-10-10 invalidated the earlier visual
acceptance: byte-line inspection missed raw LF preserving the cursor column.
This is a repair of approved NU3/NU4/NU6, with no new gameplay or sprint scope.
Root executes the narrow shared adapter correction; a different judge re-evaluates.

- Reproduce with an independent cursor/cell oracle on actual native PTY bytes.
  Old source fails: eight unintended scroll rows at80×24.
- Normalize native output only to idempotent CRLF. Keep pure Screen.lines,
  Line/Plain bytes, simulation, cached dialogue and journal data unchanged.
- Check actual80×24,20×8,40×16,100×30 and220×70 screens, selection, completion
  and terminal restoration; run terminal package controls in both engines.
- Require local validation, exact-head CI and independent correction acceptance
  before updating installed source. Publish terminal_ui0.2.1 after quality gates.

Correction validation and landing are in progress; original evaluation remains
historical evidence, not proof of the failed user screen.
