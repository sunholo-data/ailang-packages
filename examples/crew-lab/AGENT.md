# sunholo/crew_lab

Experimental host example, version0.1.0. Saved `main` and `viewer` use IO only.
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
Core raw-key/size request: inbox_1791568104057_d08245d1; not implemented here.
