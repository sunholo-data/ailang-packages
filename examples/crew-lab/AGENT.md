# sunholo/crew_lab

Experimental host example, version0.3.0. Saved `main` and `viewer` use IO only.
The guided `play` adapter uses IO,Env,FS,AI; `store` uses FS,AI. `actor_policy`,
`scenario`, `session`, `codec`, `reactions`, `play_flow` and `presenter` remain pure.
No Net, RNG or clock effect is requested.

Reuse the social kernel and pure decisions0.4.0 API. Do not change core permission
rules or trust model-provided principals, sources, raw effects or authority.
The host-owned `crew-choice-v1` maps a closed legal choice to the responding NPC's
own ActorInput. Raw AI acceptance/resolution remains forbidden. Captain starts
and relief resolutions are separate authored commands.

The response boundary validates exact fields, duplicate keys, variant, model/id,
usage, full legal probability keys, finite confidence/probabilities/roll and total.
Confidence below0.6 defers. Normalize tolerated near-one totals in stable label
order; retain both raw and normalized probabilities and the complete response.
Never infer social effects from model floats or narrative substrings.

Requests bind config/policy, actor, task-agreement, received actor context and exact
tick/revision. Pending scheduler guards come first. Accepted identical body/roll
retries are no-ops; altered or cancelled identity reuse fails. Cancellation is
explicit and retained, never hidden eviction. All command staging includes domain
operations, immediate receipts and host bank state atomically. Blocked scheduler
output retains earlier committed boundaries; it does not claim the target tick.

`codec.CrewOutcome` is a closed fixture ADT; exact encoded codes map to directed personal
trust effects. Offer details reach only their worker immediately. Other observers
require explicit evidence delivery. OCEAN-like values are context, not a validated
human psychology model, and there is no combined goodness/mission score.

Read README and saved recordings before changing protocol. Keep completion-only
work/refund limitations explicit. No live JEV, publication, game or demo migration
is authorised by running this example. Path dependencies require the repository
tree; no claim of registry availability follows from a Git merge.

Validation: `make -f examples/crew-lab/Makefile validate AILANG=/absolute/ailang`
from repository root. Native tests execute on evaluator and strict bytecode;
inline scenario tests execute separately. Replay and pure VM recording compare
five traces. `[bin]` installation is tested in a temporary directory from an
unrelated cwd. Report skipped solver contracts separately from verified ones.

Public module paths: `sunholo/crew_lab/actor_policy`, `sunholo/crew_lab/scenario`,
`sunholo/crew_lab/session`, `sunholo/crew_lab/codec`, `sunholo/crew_lab/terminal`,
`sunholo/crew_lab/reactions`, `sunholo/crew_lab/store`, `sunholo/crew_lab/play_flow`,
`sunholo/crew_lab/play`, `sunholo/crew_lab/presenter`. Session is trusted host state;
application commands are the boundary, not caller-manufactured Session records.

`sunholo/crew_lab/terminal` translates friendly terminal commands into the same
strict JSON host protocol. Manual one-hot replies identify synthetic:manual and
never bypass host validation. `crew-view` adds ASCII gauges and recoverable friendly
errors; starting with JSON retains recorded fail-fast handling.

Guided captain controls use `crew-play` and `crew-play-offline`. Reaction weights
are authored from actor-local received context (including all five OCEAN traits);
AI supplies bounded dialogue variants, never effects or permission. Two explicit
seeded rolls choose the label and text, and both plus the full bundle are journalled.
Live cache misses use the pinned OpenRouter GLM model with the policy call limit (0..8).
Failures remain pending; retries and explicit authored continuation are captain
choices. Offline tests must use stubs/fixtures and make zero provider calls.

Stage each host Session and seed change purely, publish the bounded atomic journal,
then expose accepted state or dialogue. On publication failure stop with prior
state/seed intact; blocked scheduler outputs still retain earlier successful host
boundaries. Do not claim fsync durability, resume, hidden repair or cross-run crew
memory. Native UI controls and test-play.sh cover journal failure and replay.

Standalone onboarding and ASCII panels belong in presenter. Read recipes and Task
started/due ticks from the existing host; do not invent progress or replenish
consumed supplies. Display directed relationships, never the inert actor trust
scalar. Stock wording is a labelled narrator summary; exact selected bundle/text
remains recorded. Cached/generated quoted dialogue must equal selected text.

Published host rejection is recoverable through play_flow.recover: navigation may
change but Session, seed, IDs and journal sequence are retained. Partial scheduler
boundaries remain. Publication/retention failures stop play. Offered review is pure
navigation to Start/Leave; help changes no domain, seed, sequence or budget.
Legacy recording/run.sh remains fail-fast; recoveryRecording replays extracted
journal host commands through every rejection and accepted blocked output.

Modern pure AILANG presentation: `sunholo/crew_lab/journey_flow` and
`sunholo/crew_lab/journey_presenter`, depending on `sunholo/terminal_ui/ui`.
crew-journey and crew-journey-offline use the same play/respond/commit host adapter.
Their `journey.ail` CLI wrappers are internal, outside the reusable module export
inventory. Public `play.launchJourney` requires a supported live/offline mode;
installed controls establish effectful behavior, without a unit-return proof claim.
TERM nonempty/not dumb and absent NO_COLOR chooses trusted ANSI; explicit flags
--plain/--ansi override. This is not TTY detection: redirected output uses --plain.
Default80x24; COLUMNS/LINES or --columns/--rows clamp40..160/16..60. Input is line
keys+Enter, no Process/foreign terminal host, raw mode, hidden cursor or alt buffer.
Screen includes an empty prompt row; print text without appended newline before
Choose >. Plain reading adds a separating newline after input for pipe readability.
Views/pages preserve PlayState, allowance and journal; b returns to active decision.
History stores last64 published messages in session only; never a replacement save.
Preparation8-turn marker is UI projection, no deadline/arrival/alien simulation.
Recipe costs/host configuration, authority, response schema, model and library unchanged.
Native controls must test evaluator AND strict VM; installed test-journey compares
all journal payloads against legacy paths and replays recovery recordings both ways.
Core raw-key/size request: inbox_1791568104057_d08245d1; the native watch now
uses terminal_ui's native adapter on standalone AILANG0.54. Old journey
commands retain their original line-input behavior.


Modern default crew-journey uses explicit watch-v2 start, captain plus five specialists,
three approved named resources and bounded recipe effects. Preserve strict legacy
start/config/recordings; --legacy --debug remains the comparison UI. Config.version
stays1. Resource compute is reserved concurrent capacity/consume0; modules/cartridges
reserve1/consume1. Completion-only effects and full stop refunds remain explicit.
Normal modern surfaces show descriptive psychology and exact AI quotations; --debug
is the only development score switch. Authored stock is an app-owned narrator
projection of frozen local state, while original selected bundle/text remains exact
in the journal. Normal Guide never announces concealed variables.
Use separate response-policy-watch-v2.json, callLimit6 default/cap8; never overwrite
legacy response-policy.json or existing user edits. Modern signatures hash exact
configuration identity and include local frozen perception, project/purpose, model,
policy and prompt version. Prompt omits full config/effects and policy text. Reject
known score/trait disclosures on every cached variant and generated variant before
cache publication. The guard scans all metric occurrences and permits qualitative
state alongside physical quantities; this is a bounded pattern check, not a semantic
proof. Invalid generated/cached text leaves the host request pending. Offline controls
have0 provider calls; deterministic fixture attempts are reported separately.
Validate installed walkthrough and both-engine journal recovery with watch-test.
Pure modules narrative, watch_presenter and watch_scenario contain modern projections.
Native presentation controls use initialized trusted fixtures; installed controls
exercise complete host-start/publication flows. The current evaluator has an imported
native-test std/json getString callback resolver issue in minimal imported controls; do not skip native controls, use pure fixture boundaries and real CLI tests.

Modern proposal preview derives its worker, agreement, purpose, duration and costs
from trusted host state. Start now assigns/reserves without advancing time; Decide
later and0 return to main with the offer/answer intact. Label b Decision during
submenus: it returns from reading views to that active decision, not to main.
Keep Start/Decide later meanings in the persistent minimum-size footer; rest has
no resource reservations. These are presentation changes, not new host transitions.

Runtime validation limits on v0.52.0: fmt reports a nil-expression node for the
existing journey_presenter_test module, and bounded15-second format attempts for
play, narrative and watch_presenter time out. Record these gaps; never describe
those files as formatter-clean. Package check, native tests and actual installed
screen controls remain required. Journals retain the existing8MiB total/1MiB record
limits and stop before publication when full; they do not yet support long journey
checkpoint compaction. The explicit clampIndicator pure contract is Z3 verified;
complex actor/state effects are established by native controls, not a whole-kernel
formal proof. Source-inline contracts lacking complex generators are recorded as
skipped separately from zero-skip native suites.


Native watch adapters: native_watch_ui, native_watch_presenter and native_watch_args
are pure. native_watch is an internal CLI, outside the reusable export inventory.
play.Run/Applied and openWatch/applyWatch/closeWatch are trusted host adapter APIs;
caller-manufactured records are not an application permission boundary. They reuse
existing start/commit/respond/journal/library operations. applyWatch suppresses the
old waiting renderer only; native_watch displays its honest synchronous waiting
frame. Generated/cache quotes are selected and journalled before display.

Exactly one input branch owns each read: Native uses adapter.readInput inside
adapter.run; Line/Plain uses readLineOpt and published lineEvent. Generic lineEvent
maps bothq and0 to Cancelled; the app intentionally preserves literal0 as Back in
its displayed proposal, and mapsq to its own quit confirmation. Native Interrupted
ends immediately; Escape remains contextual Back/quit confirmation. No background
worker, Process/Clock/Stream or foreign product host is introduced. PTY Python is a
hermetic acceptance fixture only: its session guardian keeps Darwin's terminal
observable after the AILANG child exits, and reads a separate cleanup pipe.

UI state is separate from Session and owns only view, cursor, details page, actual
bounded viewport and ASCII preference. Idle reads cause no redraw, counter change,
FS access or journal update. Tiny viewports accept resize/quit only. Reading menus
hide inactive actions. Quit is modal and preserves previous cursor/page; Start
proposals always initialize on Decide later. Resource/consent/occupancy previews
are descriptions, and host guards remain authoritative. On failed Start retain
stage's original phase/target; never call legacy recover to redirect to Bridge.

Native dimensions cap rendering at160x60 and preserve actual smaller sizes. Compose
preformatted structural rows directly into Screen; prose-only wrap may collapse
spaces. Screen.lines contain no escapes; trusted focus styling belongs in text.
Plain/line reserve a blank prompt row. All physiological/personality descriptions
are qualitative outside --debug; bars represent physical project turns only.
Eight-turn preparation review is never an arrival countdown or winning grade.

Run native-ui-test (both pure engines and separately reported source-inline
generators), native-watch-test (installed offline flows/navigation payload parity/
replay/cached exact words) and native-watch-pty-test (raw input, real sizes and
restoration) through Makefile.validate. Effectful scoped adapter requires interpreter:
strict VM lacks bounded @limit execution. Do not broaden any IO budget to mask it.
Named pure controls run strict VM with zero fallback; distinguish skipped generator
and Z3 encodings from established controls/proofs. Journal8MiB retention and bounded
runtime formatters still limit long-watch scaling; no unbounded journey guarantee.

Native action menus expand with measured height (3..12 rows); compact80x24 keeps
detail space, from27rows the six bridge actions remain visible at every focus.
The footer shows visible choice range. Up/Down chooses; PgUp/PgDn pages details.
Resource-aware offer/withdrawal gameplay is separately planned, not implemented.

## Conversation watch (0.4.0)

Native watch defaults to `watch-v3` host sidecars; `--legacy`, journey and play
keep v2/older recordings. Session.chat and .personalities are additive API fields
but excluded from old wire snapshots. `conversations` owns issue catalogue, exact
speech and three seeded starting replies; session validates issue/task/clock/revision,
confirmed stance, delivered evidence and same-proposal reconsideration atomically.
The native text editor and review are pure UI state and never consume RNG/journal
IDs/resources. Letters including q/b/h are text while editing. Review defaults to
Keep editing; only explicit Send publishes speech. Context reads/resize preserve it.
`personality_host` verifies received evidence before creating kernel receipts,
projects gradually changed traits into actor attributes on actual committed turns,
and serializes baselines/targets/history in new host snapshots. A lab_major fixture
is explicit developer-supplied voyage evidence, not simulated alien contact.
Scores belong to --debug; ordinary player views use descriptive conditions.
Python remains restricted to acceptance oracles/harnesses, never product code.
