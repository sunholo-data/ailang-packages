# Captain's journey terminal

| Game pillar | Alignment | Concrete constraint |
|---|---:|---|
| Choices Are Final | +2 | Navigation never changes the host; committed consequences remain. |
| The Game Doesn't Judge | +2 | Arrival review records facts, with no victory grade or best route. |
| Time Has Emotional Weight | +1 | A preparation chapter gives each elapsed lab turn context; it does not invent relativistic clocks. |
| The Ship Is Home | +2 | Conversations, crew needs and work are the primary screen content. |
| Grounded Strangeness | +1 | First-contact preparation is through observation and signals; no material exchange. |
| We Are Not Built For This | +2 | Tired crew retain refusal and relief choices. Indicators are inspectable, not a composite score. |

**Status:** Implemented and merged to packages main in [PR114](https://github.com/sunholo-data/ailang-packages/pull/114), 2026-10-09.
Exact source 3e5659e: [CI37973618460](https://github.com/sunholo-data/ailang-packages/actions/runs/37973618460) green;
independent acceptance 98/100, no blockers. See [evaluation](journey-evidence/evaluation.json).
**Authorization:** Mark requested serious terminal UI work, permitted a new package,
selected a strained crew preparing for first contact, and then explicitly preferred
pure AILANG for the terminal UI. Existing captain/crew rules, AI provider, local
library and package-main landing are already authorized. This slice realizes that
interface instruction. Later journey mechanics below remain a backlog, not newly
ratified game canon.

## Problem and systemic audit

PR112 improved a numbered scrolling menu, but a typical action still prints the
entire dashboard, guide and menus. Dialogue disappears in repeated state output.
The lab offers four recipes without a reason for choosing between them. It is not
an understandable story workshop for a newcomer.

Read `play.ail`, `play_flow.ail`, `presenter.ail`, `scenario.ail`, `test-play.sh` and
the implemented standalone-captain-game design. The existing typed host, staging,
publication, selection and journal are reusable. The interface is the systemic gap:
every phase shares the same scrolling loop. Change presentation for every phase,
not only the science example. Retain the old recording commands and plain player
for compatibility. Introduce an explicit modern entry command.

## Experience

Shipboard console, restrained blue and gold accents with neutral text. One composed
screen replaces the previous frame in ANSI mode. A header locates the player; a
chapter strip locates them in the experiment; views separate decisions from detailed
crew metrics and developer evidence. Colour encodes emphasis, never morality.
No animation or invented ship map. Existing bridge and Commons are the setting.

Opening: **Before the first hello**. The captain has eight lab turns to explore how
the crew prepares for a possible contact. This is an authored preparation exercise,
not a simulated arrival, civilisation or physical travel deadline. Eight turns is
a chapter marker only: nothing expires or fails at it. Past it, a factual preparation
review replaces the introduction; play can continue. The fictional contact is not
guaranteed and no alien words or events are fabricated.

At the outset the scientist values curiosity and autonomy; the engineer values
reliability and fairness. Present those actual values and fatigue, without treating
OCEAN as a validated psychological diagnosis. Describe observations as preparation
for interpreting what the ship might encounter, maintenance as equipment preparation,
and rest as giving people breathing room. Keep existing recipe names in inspect
views and journals. Materials are internal, finite lab supplies, not alien cargo.

Opening screen must answer: who am I, where are we, what is happening, why are these
people asking for my attention, what can I do, what does a turn mean here, and how
can I read more without accidentally moving time? Introduce offer -> hear response
-> decide Start/Leave -> advance -> observe consequences in small steps. Explain
the difference between consent and orders before the policy selection. Default
seed 42 only for the new journey entry, disclose it and allow `--seed` override;
remove the numeric seed questionnaire from onboarding. Policy remains an explicit
human choice with no preselected answer.

```text
  Stapledon's Voyage                         Bridge / turn 0
  Before the first hello                     Preparation 0 / 8
  o----o----o----o----o                       Arrival review is an exercise marker

  Bridge    Crew    Work    Log    Guide
  -------------------------------------------------------------------------
  A crew to prepare, not just equipment
  The scientist wants observations; the engineer wants reliable equipment.
  You have 6 materials. Science reserves 4; maintenance needs 3 to start.
  Both cannot start together. Rest needs time and no materials.

  Latest conversation / consequence
  Scientist: [the exact selected AI wording, wrapped and paged]
  Agreement received. Work has not started.

  Your decision: science observations
  Four turns. Reserve 4 materials now; consume 4 at completion.
  [1] Start work      [2] Leave the offer open      [0] Back

  c Crew   w Work   j Log   h Guide   b Bridge   n Next page   v Previous
  Choose a key, then Enter. Reading views never advances time.
```

The real renderer must handle long text with paging, not clip the meaningful decision
or hide the remainder of a crew reply. Each screen shows page x/y and deterministic
next/previous commands; action keys are visible on every page. Use one-column layout
at small widths and bounded dimensions. Keep the most recent dialogue/consequence
in the main view. A session-local reading log retains a bounded history of published
messages (not a replacement journal). Errors explain recovery on the same decision
screen. Show a waiting frame before an AI lookup/call, after the offer/ask is journalled,
without presenting any uncommitted reply. Failures retain current publication rules.

## Reusable package

Create `sunholo/terminal_ui` under `packages/terminal-ui`, experimental 0.1.0:

- Pure text layout: sanitize controls, conservatively measure terminal cells,
  word wrap with hard breaks for long words, pad, rule/panel and bounded gauge.
- Pure screen composition and paging: dimensions bounded 40..160 columns and
  16..60 rows; text never creates arbitrary terminal controls. Body pages have
  an explicit count and page clamp; footer remains visible. Avoid a dependency
  on crew, decisions, AI or game types.
- ANSI styling/reset and safe home/clear redraw generated by trusted code only.
  No alternate buffer, hidden cursor or raw terminal mode, so interrupt cannot
  leave terminal input broken. Normal recap remains in scrollback on exit.
- Plain mode uses no escapes and preserves readable output for pipes, TERM=dumb,
  NO_COLOR, tests and accessibility. Explicit `--plain` / `--ansi` UI override.
  `--columns` and `--rows` are explicit dimensions; read COLUMNS/LINES if provided,
  default 80x24. Runtime has no confirmed terminal-size query; do not claim
  automatic resizing or TTY detection. Record that a manual refresh/relaunch with
  new dimensions is the supported size change in this release.
- All interaction remains `readLine`: keys + Enter. No Go, Python, Node, shell
  terminal mode manipulation or alternate renderer. Arrow-key reading is a
  separately reported runtime capability request, not required for this slice.

Terminal-cell sizing may conservatively overestimate non-ASCII glyphs. Handle
ASCII, common European punctuation and box drawings correctly; support wide CJK
characters and strip C0/C1/bidi control sequences. Do not claim a full Unicode
grapheme implementation. Exact raw AI text remains in the existing journal; the
display projection removes controls only and wraps it. Do not reinterpret stock
fallback wording as crew speech. Avoid arbitrary source text as ANSI commands.

Package `[bin] terminal-ui-demo` is an independent IO-only showcase using the same
pure renderer, short choice/help/page flows and meaningful inline/native controls.
The package itself needs at most IO for that showcase; core exports are pure.

## App integration

Introduce `journey_presenter.ail` and `journey_flow.ail` as pure projection/navigation.
Minimize changes to `play.ail`: share respond/act/commit/finish and the host unchanged,
add a presentation mode and view/page/history state, and branch rendering/reading.
If keeping old run records simpler, add a separate internal UI record rather than
exporting new fields in PlayState. No cost, permission, seed-roll, receipt, freshness,
schema, task or completion changes. View/page/help operations consume no seed, AI
allowance, sequence, domain command or journal write. Avoid carrying accidental help
text as a new conversation. Pending host response/start/relief action remains the
active decision when switching views; `b` returns to that decision, not to a host
main phase that discards it. Navigation must not mutate PlayState at all.

New `[bin] crew-journey` and `crew-journey-offline` use the same GLM5.3Flash / stub
setup as existing entries and the same response library. Existing crew-play and
recording controls continue. Do not change user policy files or cache. Document
start commands and two actual experiment flows (equipment first; observations
first then relief/rest), including why waiting never replenishes consumed supplies.

Crew view: actual fatigue, readiness, observations, directed captain trust, OCEAN,
values and occupancy. Explain current agreement/status from actual host records;
do not claim peer disagreement contagion already exists. Work view: offered/working/
completed/stopped tasks, actual duration/progress and costs, supplies. Guide view:
first contact context, action workflow, known limited completion-only effects,
offline/library provenance and controls. Log view: published messages only; journal
path and remaining AI allowance live in inspect/guide, not the primary plot.

## Verification log and reuse

| Premise | Evidence, 2026-10-09 |
|---|---|
| Existing output can colour/clear/flush | Installed teaching prompt v0.16.6 terminal example; `docs std/io` exports print, flush. Execute a minimal IO probe before implementing. |
| Current public input is line based | Read installed `docs std/io` and core `std/io.ail`: readLine; no public readKey or size query there. This is a std/io surface observation, not a claim about every core implementation. |
| Registry has no terminal package candidate | `ailang pkg search terminal` and `... tui`: each succeeded with no packages, via approved network execution. Initial sandbox DNS failure is not negative evidence. |
| Existing rules/resources | Read scenario config: 6 materials, science reserve/consume4, maintenance reserve3/consume2, rest cost0, fixed recipe durations; host reused. |
| Existing controls | Read test-play.sh: exact help payload comparisons, stock/cache provenance, recoverable rejection replay, publication failure. Re-run after integration. |
| No new geometry/cast canon | Read human-life-bridge-commons and generation-cast-plan; roles retained, names remain open. |

Quorum triggers: none for this implementable slice. No freeze item, machinery override,
cost/KPI change, banked schema change or vendor premise. The broader journey backlog
below will require its own design and review when mechanics are proposed. Normative
design references: stapledons-design `vision/core-pillars.md`,
`features/next/human-life-bridge-commons.md`, `features/next/shared-social-dynamics-and-events.md`.

## Acceptance criteria

1. `terminal-ui-demo` and both journey commands install through `[bin]` and run
   from an unrelated cwd. No foreign-language terminal runtime or Process effect.
2. At 80x28 and 60x24, composed pages fit requested cell widths and heights,
   including a 4096-character message, long word, ANSI/control input and CJK case.
   Body remainder can be read through pages; decisions/footer remain available.
3. ANSI mode replaces frames without terminal mode/cursor changes. Plain output
   has zero ESC bytes. EOF/quit and fatal publication failure leave normal text.
4. A newcomer sees a briefing, explicit policy decision and causal offer/start/time
   workflow without a seed questionnaire. Preparation0/8..8/8 reflects host ticks;
   review has factual state and no score, deadline failure or fabricated alien contact.
5. View and page navigation at bridge, pending start, unavailable reply and relief
   changes no domain/seed/sequence/AI usage and does not discard the active decision.
6. Installed offline flows with view/page visits have the same journal payloads
   as identical choices in the old player (normalizing only existing start mode if
   the entry uses a distinct mode string; preferably preserve live/offline mode).
   Replay agrees on evaluator/strict VM. AI calls are zero in all offline checks.
7. Selected cached AI words retain correct provenance; cached authored origin stays
   narrator text. A shortage is explained and play continues. Publication failure
   exposes no uncommitted state/dialogue. Waiting view appears before provider work.
8. Existing scoped controls pass; new package native tests run evaluator and strict
   VM, source tests separately; strict package quality reports evidence and skips
   honestly. Independent evaluator judges UI/AC against actual transcripts/rendered
   frames, not only inventory counts. README, AGENT and changelogs reflect limits.

## Journey workshop continuation

After this interface is usable, extend the same AILANG host with authored scenario
configuration, multi-leg state, condition-triggered incident decks, explicit evidence
delivery to peers, remembered promises and contact/revisit obligations. Desired story
loop: departure briefing -> transit work/social incidents -> approach -> mediated
contact -> consequences -> next leg -> factual legacy. AI provides validated expression
and proposals on cache misses; trusted rules own legal effects and causality. Reuse
library variants, authored probabilities and explicit seeds so replay stays useful.

Full-journey fast-forward should pause at actionable incidents, publish each boundary,
and yield a causal chronology for story review. It must not silently advance through
crew decisions. Scenario/export formats and new KPI/cost effects need separate reviewed
design. Current interface delivers the first preparation chapter and can continue
indefinitely; it does not claim those later mechanics are already playable.
