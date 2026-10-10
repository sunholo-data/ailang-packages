# Crew watch: native controls and terminal graphics

| Game pillar | Score | Reason |
|---|---:|---|
| Choices Are Final | +1 | Deliberate confirmation separates browsing from committing work. |
| The Game Doesn't Judge | +1 | Show facts and concerns, without a victory or morality meter. |
| Time Has Emotional Weight | +1 | Work timelines make the preparation watch understandable. |
| The Ship Is Home | +2 | Bridge and existing Commons provide a human setting for five specialists. |
| Grounded Strangeness | 0 | Schematics introduce no astronomy or alien-generation claims. |
| We Are Not Built For This | +1 | Qualitative crew observations preserve human ambiguity. |
| **Net** | **+6** | **Aligned; implemented and accepted.** |

**Status:** Implemented and accepted after row-alignment correction, 2026-10-10.
**Release:** local crew-lab 0.3.1; terminal_ui0.2.1 merged, registry release pending
explicit approval. A real terminal screenshot invalidated the earlier visual check;
the companion sprint records the corrective acceptance and round2 evaluation.
**Milestone:** S-CREW-NATIVE-UI. **Priority:** P0, human usability.
**Estimate:** 1,800 changed lines, including meaningful controls and documentation;
three development days plus asynchronous CI/review, not a delivery promise.

**Implements:** [core pillars](https://github.com/sunholo-data/stapledons-design/blob/main/vision/core-pillars.md),
[crew psychology](https://github.com/sunholo-data/stapledons-design/blob/main/features/future/crew-psychology.md),
the recorded [bridge/Commons scope](/private/tmp/stapledon-human-design-20261009/features/next/human-life-bridge-commons.md),
and the [approved Commons architecture](/Users/voightkampff/dev/sunholo-data/stapledons-godot/design_docs/planned/r1/m4-ship-commons-build.md).
The owned normative design revision remains distinct from this implementation plan;
this sprint does not publish that pending revision. No SR/GR rendering or physics
math changes; the relativity specification remains authoritative for the game.

**Depends on:** implemented watch-v2 and action-clarity fixes, published
sunholo/terminal_ui 0.2.0, AILANG v0.54.0 for the standalone CLI.
**Does not depend on:** the separately owned worker-cleanup fix.

## Problem and evidence

Mark still cannot reliably understand the menus despite the clarity repair:
Start, Leave open and Back were ambiguous, help came too late, and long text hid
available choices. He asks for a terminal game that helps iterate human stories
without Godot builds, with graphics as well as words and pure AILANG throughout.

The current watch presenter uses terminal_ui.ui.screen and line-input menus.
The new published terminal_ui package offers immediate arrows, Enter, normalized
events, scoped terminal ownership, resize, pure selection widgets and sanitized
ANSI rendering. The installed terminal-ui-demo already points at registry 0.2.0
and an AILANG v0.54.0 binary. Root reran package compilation (12 files) and named/
property tests (39 passed, no failures/skips) on the official runtime.

The reply-inbox sprint stopped at its own M1 gate because quit left worker PIDs.
This design changes presentation and input only. It neither implements that fix
nor overrides the downstream gate. Synchronous AI can still block a choice until
the inbox work passes; do not advertise live background interactions prematurely.

## Experience and graphics

Start with a short briefing: you are captain, five specialists are preparing for
possible first contact, and people, Archive capacity and finite equipment compete.
Explain both command styles before selecting one, including the ability to start
despite refusal under authority and the possible cooperation consequences. Describe
the basic flow: choose work, hear a reply, decide whether to start, advance a turn.

Use a restrained ship-console style: cyan selection/focus, amber reservations or
unresolved choices, ordinary neutral text. Every colour has a word or symbol too.
No red/green moral grading. Box drawing and block fills are renderer-owned strings;
AI can provide speech but cannot emit controls, invent inventory or alter layout.
ASCII mode substitutes +-| and # dots, and plain mode emits no ANSI bytes.

The mockup in crew-native-ui-mockup.txt illustrates the main 80x24 composition.
It is a design example, not a capture of implemented code or an assertion of live
crew locations. The main screen contains:

- A small two-level ship schematic: Bridge above Commons, central connection and
  Archive approach. Preserve approved architecture; add no extra playable decks.
  This is a schematic, not a measured cross-section or new physical sky view.
- A roster of all five specialists, their actual assignment and qualitative
  demeanor. Assignment badges are work state, not simulated physical locations.
  Until the host has location evidence, do not place a person inside a room as fact.
- A working-project timeline with elapsed/total turns, plus reusable capacity
  shown free/held and finite stock shown free/held/spent. Labels explain what returns
  and what is consumed. Never use numerical psychological gauges in normal play.
- A highlighted action and a persistent consequence description. Secondary actions
  lead to Crew, Work, Log and Guide screens with context-specific legends.

At widths below 100 columns, prioritize readable choices and consequence text;
the full ship schematic can live in a dedicated Ship view. At 80x24 show a compact
overview. At 40x16 use one column, window the selection list around its cursor,
and page details independently. Header, highlighted choice and concise key legend
stay visible; no "turn page 2 to discover the controls". Below 40x16 use the package's
fitting compact resize/quit screen, retaining all state until enlargement.

The eight-turn marker is a **preparation review**, not arrival or a deadline.
Show turns remaining until that review only when before eight; afterwards say
"Review available; continue if you wish." A first-contact countdown must wait for
an actual scenario event with a real scheduled time. Timeline progress currently
represents elapsed turns; effects occur on completion, not gradually.

## Decision clarity and controls

Use native arrows to highlight, Enter to choose; h opens context help, b returns
to the pending decision or bridge, q opens a quit confirmation. Escape backs out
of the current screen; at the root it opens quit confirmation. No new interpretation
of Escape as relief, cancellation or undo. Existing number shortcuts preserve
their action meaning when displayed. Browsing or resizing never commits an action.

For a pending project, show "Agreed; not started" or "No current agreement" above
the exact crew reply. The consequential screen offers:

1. Start now — assign the named person, hold the named slots/supplies; time stays
   unchanged; explicit Advance moves work. Finite supplies are spent at completion.
2. Decide later — keep the offer and agreement; no time or resources used; return
   through Offers. This is the initial highlighted choice.
3. Return to bridge — also keeps the offer, costs nothing; label it explicitly.

Known insufficient capacity must be explained beside Start, naming the resource,
what is held and how work can release it. Retain the host guard for stale state.
Rejected actions preserve the decision and explain the failure in this UI; do not
terminate the watch or silently substitute another assignment. A choice preview
describes known commitments and costs only, never previews future sampled feelings
or moral/mission outcomes. Completion reports actual changes, including clipped
effects, alongside released capacity and consumed stock.

Retain five-person qualitative state, actor-local AI perception, OCEAN-informed
authored weights, current OpenRouter model, exact cached quotes and immutable causal
journals. --debug remains the explicit developer entry to raw metrics. UI navigation
must not change domain state, tick, RNG, journal sequence or AI-attempt balance.

## Implementation boundary

Add pure native_watch_ui.ail for UI state/actions and native_watch_presenter.ail
for adaptive frames and graphics; separate from the existing domain model. Reuse
terminal_ui widgets/events/viewport and existing watch catalog/consequence helpers.
Compose app-specific panels from sanitized text using cells/pad/wrap; final Screen
remains bounded. Do not build a second generic terminal package. If a reusable
primitive proves missing, report/contribute it upstream separately rather than
silently adding an unrelated package or broadening this sprint.

Add native_watch.ail with adapter.choose/run and exactly one input owner. Native
uses std/terminal under the package scope; line/plain use readLineOpt with blank
as idle and exact EOF as termination. No concurrent async stdin pump or readLine
inside a native session. Resize updates UI only. Idle causes no redraw, history,
FS write, journal event or time advance. Input-dependent rendering also keeps
replay deterministic without wall-clock animation state or new Clock effects.

Install additive [bin] commands crew-watch and crew-watch-offline; retain existing
crew-journey and crew-play interfaces/recordings. The dedicated standalone CLI may
require v0.54.0 without changing the Godot bundled runtime/CI/lock v0.52.0 trio.
Use isolated durable source/runtime for launchers and compare existing policy/cache
checksums before/after installation. No global checkout updates or game merges.

During synchronous AI requests draw an honest status screen: worker considering
the offer; work has not started; awaiting the reply. Do not show usable navigation
that the blocked call cannot accept. Native key ownership and asynchronous reply
delivery are separate concerns. The future inbox can consume these normalized UI
events after cleanup is verified; this sprint starts no workers or parallel calls.

## Acceptance criteria

Commands below are implemented and passed. AILANG is the
dedicated v0.54.0 binary; make commands use AILANG=/absolute/path/to/that/binary.

| ID | Required evidence | Command |
|---|---|---|
| NU1 | Intro and both styles explain role, offer/start/advance before input at 80x24 and40x16; all five crew accessible | `make -f examples/crew-lab/Makefile native-ui-test` |
| NU2 | Menu cursor stays visible; initial Decide later; Escape/back/resize/idle neither commit nor change domain/RNG/AI/journal | same target; `ailang test --package examples/crew-lab --bytecode --strict-bytecode` |
| NU3 | Graphics match host working/held/spent state, qualitative crew, review-not-arrival; no claimed locations or numeric psychology | `make -f examples/crew-lab/Makefile native-ui-test`; inspect generated frames |
| NU4 | Native 80x24→20x8→40x16→100x30 preserves selection/task state; key+Enter unnecessary; normal quit, Ctrl+C and injected adapter failure restore terminal | `make -f examples/crew-lab/Makefile native-watch-pty-test` |
| NU5 | Actual installed offline offer/start/advance/completion/shortage/relief flows remain playable; no provider calls; finite spend and compute release honest | `make -f examples/crew-lab/Makefile native-watch-test` |
| NU6 | Line/plain blank idle vs EOF, ANSI-free plain, ASCII graphics fit bounds; long quotes reachable, exact originals retained | native-watch-test and native-ui-test |
| NU7 | Existing causal recordings, cache/policies and old launchers preserved; existing composed regression and CI green | `make -f examples/crew-lab/Makefile validate`; recorded checksum comparison |
| NU8 | Independent evaluator checks actual frames/PTY/game flow and no remaining blockers, main merged and durable new launchers installed | sprint-evaluator report plus installed command smoke |

Pure named UI controls run both interpreter and strict VM without fallback. Effects
run interpreter: current VM rejects @limit frames; preserve package budgets, report
the diagnostic, do not claim effectful strict-VM support. Z3 verification is a
separate inventory; report proved, skipped and encoder errors accurately.

## Milestones, risks and deliverables

M1: pure UI, graphics, beginner frames and invariant tests (700 lines).
M2: native adapter and additive launchers, scoped lifecycle, line/plain (600).
M3: installed PTY/game flows, regression, walkthroughs, independent evaluation
and landing (500). Order M1→M2→M3; worker cleanup is not on this critical path.

Risks: dense graphics obscure options (responsive priority and real small frames);
fake crew locations (work badges only); UTF8 width mismatch (conservative existing
cells and ASCII mode); accidental Enter commits (explicit screen state/default);
wrong runtime breaks old commands (isolated installation); waiting screen promises
background freedom (truthful synchronous state). No unanswered gameplay decision
blocks this implemented sprint. Mark approved this bounded sprint before execution.

Deliver design/mockup, pure UI and presenter, effectful adapter, additive commands,
meaningful tests and actual terminal evidence, two playable walkthroughs, updated
README/AGENT/changelog and independent acceptance report. Move implemented docs
after acceptance. Normative roadmap publication uses its existing separate
approval boundary; do not alter the pending public design payload.

## Completion evidence

Reviewed implementation `667491a` passed full local validate and exact-head
[CI 38073025460](https://github.com/sunholo-data/ailang-packages/actions/runs/38073025460),
including behavioural mutations and social regressions. There are 170 named crew
controls in each engine, plus installed shell flows and three native PTY lifecycle
controls. A different agent accepted the actual frames, gameplay and terminal restoration.
[PR120](https://github.com/sunholo-data/ailang-packages/pull/120) merged as `02c8042`.
Only additive `~/.ailang/bin/crew-watch` and `crew-watch-offline` were installed,
using durable owned source and the dedicated official v0.54.0 runtime. Installed
native intro/bridge/quit and live plain EOF startup passed with no provider calls.
All five prior launcher checksums and four sampled policy/cache checksums are unchanged.

Published terminal_ui0.2.0 passed a clean consumer smoke; social/content retain
existing local dependencies because content_library0.1.0 is not published. This
experimental app is not a new registry release. Pure controls run interpreter and
strict VM; the effectful scoped adapter runs interpreter. Exact verification inventory:
127 total, 26 proved, 97 skipped, four unchanged encoder/solver errors, zero
counterexamples. AI is still synchronous. No full voyage or Godot runtime change.
The original report is `.ailang/state/evaluations/eval_S-CREW-NATIVE-UI_round_1.json`.

### Corrected actual terminal acceptance

The original LF-split captures missed raw LF retaining its cursor column. Mark's
screenshot reopened acceptance. Native-only CRLF projection and an independent
visible-cell cursor oracle now cover actual80×24,20×8,40×16,100×30 and220×70 PTYs,
including full-width rules, scrolling, selection and restoration. Old source failed
with eight unintended scroll rows; corrected source passes with zero scrolling.
Full local validate and exact-head CI38075427310 passed at1cd02d9; PR122 merged as
c5ae7eb. Updated installed commands passed12actual native grids, scientist4turn
completion/slot return and clean quit, plus live plain EOF startup; no providercalls.
Five older launchers/four sampled policy/cache checksums remain unchanged. Terminal
controls42eachengine; proof35=12proved22skipped1unchangederror; no whole-proof claim.
Final corrective report: `.ailang/state/evaluations/eval_S-CREW-NATIVE-UI_round_2.json`.

Automatic approval review rejected public registry publication of terminal_ui0.2.1
because a durable public release needs explicit approval. The package is merged and
used locally; publication and a new registry-consumer smoke remain pending. No
registry release is claimed and no approval bypass was attempted.
