# Changelog

## Unreleased

Local only; never published.

- **Stand down at the check-in (crew_core 0.6.0, 2026-10-16).**
  - `crew-sim --skip ... --stand-down on|off` (default on). With stand-downs
    on, the `crew_skip/1` line counts `relief.*`, `stand_downs.*` and the live
    `evidence`; with `off` it is 0.5.1's line byte for byte.
  - Claims can measure `stand_downs.asked/granted/denied`, `evidence` and
    `escalations.stand_down`. New `auto/stand-down-decade.claims.json`: 8 of 8.
  - The tally counts the new Acts per crew member.
  - `hands_on.json` gains `{"kind":"stand_down"}` (OQ3).
  - New recording `recordings/stand-down.ndjson` (check_in, answer, a grant on
    running work, a denial, carry_on, advance), under parity and replay.
  - `review/*.claims.txt` regenerate byte for byte. See `REVIEW.md`.
- **Check-ins from the work's start (crew_core 0.5.1, 2026-10-16).**
  - The random captain's check-in follows the package's new rule (every other
    day of the work, from the day after it starts), so the three captains
    share one rule.
  - `scenarios/stapledon/review/*.claims.txt` re-recorded; no verdict
    changed. See `REVIEW.md`.
- **Resource units from data (crew_core 0.5.0, 2026-10-15).**
  - `bubble.ail` is gone. Stapledon's eight bubble resources are now
    `scenarios/stapledon/resources.json` (crew_units/1), which the game syncs
    like the scenarios.
  - `crew-sim --bubble [--units FILE]` lints a scenario against that table
    through crew_core's `units`.
- **The game's profile (crew_core 0.4.1, 2026-10-14).**
  - `crew-sim --profile v2|v3` (v3 is the default with `--auto` or `--skip`)
    and `--concerns escalate|APPROACH`.
  - v3 gate claims: 0 host errors over a year.
  - All 0.4.0 auto claims rerun on v3; the findings are in `REVIEW.md`.
- **`hands_on` preset (2026-10-14).** The Stapledon pack gains
  `hands_on.json`, for the game's `hands_on` auto-run:
  - breakdown at stress 70, trust floor 40, `uncovered` and cohort pressure
    25;
  - claims in counting mode: 10 of 11 hold.

  Findings are in `REVIEW.md`:
  - the line at 70 re-arms about 130 times a year (hysteresis proposed);
  - at cadence 1 with archiving, crew_core asks about lapsed offers (an
    old bug, also in `critical_only` and crew_core 0.3.0).
- **Universal resources.** The Stapledon pack uses only the eight bubble
  resources (`mass`, `water`, `power`, `heat`, `garden`, `fabrication`,
  `compute`, `signal`; stapledons-design `bubble-resources.md`). Stocks are
  used up; capacities are only reserved. All claims are unchanged: 33 of 36
  hold.
- **crew_core 0.3.0 in the lab (S-CREW-CORE-0.3).**
  - crew-sim's consent and orders captains run crew_core's auto-captain,
    with byte-identical output.
  - New flags:
    - `--archive N`;
    - `--auto escalation.json` (counts `escalations.<rule>`, available to
      claims);
    - `--skip N --cadence C` (times the game's skip).
  - `recording_cli` prints `crew_core.recording` for parity checks.
  - The pack gains `escalation.json` and year-long auto claims (6 of 6
    hold).
  - The ergosphere scenario gets a third heat user (D-70 OQ6).
- **Crew strain (S-CREW-STRAIN).**
  - crew-sim's orders captain no longer rests people on its own initiative.
  - New per-crew measures: `peak_stress`, `peak_fatigue`,
    `overextended_turns`, `halted` and `regard_min`. New run-level measures:
    `shortfalls` and `halts`. Claims can name all of them.
  - The Stapledon pack has `policy.json` (strain on), and the stress claims
    use peak stress.
  - Over 20 seeds, 44 of 50 claims hold; the findings are in `REVIEW.md`.
- **Resources that flow (S-CREW-BUBBLE-RESOURCES).**
  - `crew_sim/1` reports `resources.<id>` (`min`, `zero_ticks`, `stockouts`,
    `in`, `out`), and claims can name these.
  - `bubble.ail` holds the eight bubble resources, `allocate` (ship ledger to
    crew units) and `lintPack`.
  - `crew-sim --bubble` lints a scenario, and `scenario-pack-test` runs it.
  - Four pack scenarios gained ship events and yields. 41 of 46 claims hold;
    the findings are in `REVIEW.md`.
- **Crew memory spike.**
  - `memory.ail` (pure, exported) provides recall, the variety check
    (`echoes`), `margin` and the Archive's near-miss `pick`.
  - `recall_spike.ail` measures local embeddings (EmbeddingGemma 2 on Ollama)
    on the pack's sampled words. Report:
    `spikes/recall-spike-2026-10-13.txt`.
  - Design: `design_docs/planned/crew-memory.md`.

## 0.7.0

Local only; never published. A verification loop for tuning:

- `crew-sim --check claims.json`: expectations as `crew_claims/1` (one captain, one
  measure, a statistic over the seeds, or the share of seeds meeting a condition),
  validated against the scenario; PASS/FAIL per claim with the observed value, exit 1
  on any failure. `data/watch-claims.json` records the default ship (10 claims).
- Long runs: `crew_core` drops answers to expired requests when its bank fills, and
  its scenario limits rose, so `crew-sim --turns 60` runs are clean.
- `crew-sample`: crew wording across varied moments, fetched as the watch would,
  within `--max-calls`; `--report` for reading; `crew-sample-offline` for authored words without a provider key.
- The watch policy allows up to 64 AI attempts (default 12 for new homes).

New checks: `make ... claims-test`, `sample-test`.

## 0.6.0

Local only; never published. Live crew words arrive in the background: a crew
member's decision shows at once (it never depended on the model), an authored line
stands in, and their own words are fetched by a separate `crew-reply-worker` process
while the captain keeps playing. Status row `Replies: N preparing, M new (r)`; `r`
opens a Replies view. Arrivals never move the menu, cursor, page or editor text.
The watch itself never calls a provider and needs no AI key: only `crew-reply-worker`
does. Up to three workers at once, at most 16 queued; quit stops them, releases any
dialogue-cache lock they held and journals each as one possible attempt; a missing
worker leaves the authored line. Each attempt is reserved from the run allowance and refunded
when no call was made. Journals gain transport-only `wording` records; domain records
are identical to a run with saved words.

Prefetch (`--prefetch 0..5`, default 2): on the bridge, the words for offering idle
crew their work are fetched ahead, predicted exactly from the pure session, so the
offer shows them immediately. Prefetch keeps three attempts in reserve and is never
shown as a reply; an offer made mid-prefetch adopts that job.

New modules: reply_jobs (pure inbox), reply_codec (job/result files), reply_runner
(process adapter), reply_worker (bin). New checks: `make ... reply-test` and
`async-test` (nine installed scenarios with provider-free fixture and stub workers).

## 0.5.0

Local only; never published. The captain/crew host moves to the new published
package `sunholo/crew_core`; this example keeps the watch, AI dialogue wording,
journals and tools. The ship is data: `data/watch-scenario.json`
(`crew_scenario/1`), and `crew-watch` / `crew-watch-offline` accept
`--scenario FILE` and `--policy FILE`, validated before the watch opens. Journals
record the scenario hash, policy hash and canonical scenario.

New `crew-sim`: batch runs without AI under a consent, orders or random captain,
one JSON line per seed, `--summary` medians and spreads, never ranked. Same inputs
give byte-identical output on both engines; 20 seeds x 12 turns take about 12 s.

`crew-host` (formerly `crew-lab`) is the NDJSON host; its recordings now use the
watch scenario. Retired: `crew-lab`, `crew-view`, `crew-play*` and `crew-journey*`
with their modules, scripts and the legacy two-crew scenario; their menu
recordings are kept under `recordings/retired/`. The line-mode watch menu now
names running work (it showed "Unknown project").

Known limits: the host keeps at most 64 answered questions per session (about
12-15 turns with five crew); live AI wording is still synchronous.

## 0.4.1

Reduce new live watch requests to two short wordings of the reaction already
chosen by the authored personality policy. Send nested actor-local context;
retain exact policy/configuration in a separate versioned cache identity.
Both random draws, consequences, existing complete cache hits and offline
continuations retain their previous behavior. Validate both saved and generated
short replies: two matching labels, equal weights, at most240 characters each,
and no exposed development metrics. Rejected generation retains the pending
request and supports authored continuation.

One paired GLM-5.3-Flash sample fell from83.7 seconds/6,502 output tokens/12
alternatives to10.9 seconds/967 output tokens/two alternatives. This is a sample,
not a latency guarantee. Streaming and background inbox delivery remain separate
work; this version still waits synchronously for a new reply.

## 0.4.0

Add captain conversations to the native watch: actionable crew concerns, known
context, three editable starting replies and free text, followed by review of
exact words and a declared approach. A worker reconsiders the same offered task;
speaking does not start work, spend supplies or advance time. New watch-v3 hosts
include conversation and personality sidecars; old journey/play traces retain
their existing wire format. Public Session gains sidecars (breaking API change).

Add explicit lab voyage reports to experiment with slow, major-event OCEAN
responses and interaction influence. Numeric traits stay in development views.
AI remains synchronous; the independent reply-inbox sprint is still gated.

## 0.3.2

Expand the native action menu with terminal height, retain the complete last
window and show its visible choice range. Tall screens show all six bridge
actions and all five specialists. Compact screens retain detail space and
scrolling; domain commands, resources, AI and cached dialogue are unchanged.

## 0.3.1

Fix native staircase rendering using terminal_ui0.2.1's explicit raw-mode row
separators. Strengthen the actual PTY harness with a visible-cell cursor oracle,
no-scroll assertions and a 220×70 terminal beyond the capped 160×60 layout.
Simulation, library, journal and line/plain behavior remain unchanged.

## 0.3.0

Adds pure AILANG `crew-watch` and `crew-watch-offline` with native arrows/Enter,
a newcomer briefing, safe proposal/quit defaults, responsive ship/crew panels,
named resource previews and actual elapsed project bars. Reading and resizing
leave host state, sampling and journals unchanged. Known shortages stay on the
same proposal; compute contention recovers after existing work completes. Native
terminal scope restores raw mode, cursor and alternate screen on quit, interruption
and host-publication failure. Line/plain distinguish idle blank input from EOF.
Requires standalone AILANG0.54; Godot runtime and earlier durable commands remain
separate. Existing journal/store/AI boundaries and exact library words are reused;
AI remains synchronous. Adds isolated installed/PTY/replay controls and practical
science/authority/relief walkthroughs. No publication or async worker implementation.

## 0.2.0

Adds understandable first-choice context and pre-start help, plus a versioned
five-specialist watch that is now crew-journey's default. Archive compute capacity
is reusable; replacement modules and diagnostic cartridges are finite. Fatigue,
stress, morale, role values and all OCEAN axes influence responses; normal play uses
qualitative descriptions and exact AI words, while --debug exposes development state.
The separate watch policy defaults to6 bounded AI attempts and preserves legacy user
policy/cache files. Modern signatures include exact config identity; score-disclosure
guards reject generated and cached text before use. Adds installed walkthrough,
resource contention/completion, cache isolation and both-engine replay controls.
Legacy recordings, crew-play and strict effects remain compatible; --legacy --debug
retains the earlier journey comparison. No registry publication or game integration.

The pending proposal now distinguishes an agreed offer from started work, explains
the assigned worker, purpose, duration and resource consequences, and labels the
choices Start now / Decide later. The old0 shortcut is explicitly the same as
deciding later; b returns to the current decision. These hints remain visible on
the minimum-size screen and rest does not claim to reserve supplies.

## 0.1.0

Adds an independent captain-and-crew CLI experiment using saved synthetic typed
decisions, explicit confidence gates and sampling rolls, actor-local perception,
personal work agreements, captain assignment and relief, bounded request retention
and directed trust consequences on receipt. Five contrasting recordings demonstrate
completion, refused orders, care, denied relief and competing materials.

The original library and host transitions remain pure; saved stdin/output use IO. Includes
strict response/command controls, native tests, saved replay, pure strict-VM parity,
temporary `[bin]` installation tests and package quality commands. Requires the
pinned AILANG0.52.0 runtime for the documented checks. Strict VM replay uses the
pure recording entry because stdin `readLine` is evaluator-only on that runtime.
The saved fixture paths use no provider calls. No game integration or registry publication.
Completion-only project effects and full reservation refunds on stop remain
explicit limitations; no partial-work economics or moral winner is introduced.

Received trust deltas are illustrative fixed fixture rules; traits and values enter
request context, with trait-dependent appraisal deferred. Initial fixture-only proof evidence reported
5/28 verified,22skipped and one unsupported function-record encoding; runtime
contracts remain active. No isolated publish smoke is claimed for the unpublished
path dependency. A scoped CI job runs the crew and original social lab checks.

Adds `[bin] crew-view` and `make view` for readable per-step interior state, sharing
the same pure host and saved decisions with the full JSON CLI.

Terminal iteration adds portable ASCII indicator gauges, help/status/quit and
friendly captain command aliases. Manual replies are labelled synthetic fixtures
and reuse the same validation and host authority. Friendly errors preserve the
incoming session; JSON recordings keep fail-fast behaviour.

Adds `crew-play` and `crew-play-offline`: numbered captain choices, automatic crew
reactions, explicit start/leave decisions and refreshed exact indicator gauges.
Authored reaction rules use all five OCEAN traits and received context; bounded
GLM dialogue bundles grow a persistent exact-context library on live misses.
Offline mode uses cache or generic authored variants with zero provider calls.
Visible pending failures permit explicit retry, authored continuation or cancellation.
Two seeded rolls, complete selected bundles, policy weights and usage are recorded
with every actual host command before state/seed/dialogue publication. New native
UI controls and installed offline tests cover science, care, denial, materials
competition, extracted strict-VM replay and atomic journal-write rollback.
The original fixed host trust appraisal and completion-only work effects remain.

Published guided-play host rejections now return to the bridge without undoing
committed work or consuming an extra RNG step. Offered review opens Start/Leave
without re-answering an already accepted agreement. Recovery journal replay
continues across rejected commands; legacy recording entry stays fail-fast.

Adds a standalone bridge briefing, authority/seed explanations, compact ASCII
panels, contextual h/help, actual worker/time/reservation/consumption details,
bounded host tick progress, recorded consequence deltas and a factual quit recap.
Directed relationship trust is shown instead of the inert actor indicator.
Stock reactions are labelled narrator summaries; selected AI quotations and full
journal provenance remain exact. Help/navigation uses no AI or host transition.

Cached authored bundles now remain labelled saved stock narrator reactions.
Cached/generated AI dialogue remains quoted exactly; Fetch and journal source
metadata are unchanged. Native and installed cached-origin controls cover both.

### Captain journey terminal
New pure AILANG crew-journey/live and offline entries use reusable bounded ANSI/plain
screens, independent reading views and paged exact dialogue; line keys+Enter.
Before the first hello is an8-turn preparation marker, not a contact or deadline.
Costs, seed draws, provider, library/journal and legacy player remain unchanged.
Published messages and actual completion indicator deltas are visible; view/page
navigation retains pending choices. Installed baseline payload/replay controls.
