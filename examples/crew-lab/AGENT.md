# sunholo/crew_lab

Experimental offline host example, version0.1.0. Effects ceiling IO; `main` reads
finite stdin and prints causal JSON. `actor_policy`, `scenario`, `session` and
`codec` exports are pure. No Net, Env, AI, FS, RNG or clock effect is requested.

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
`sunholo/crew_lab/session`, `sunholo/crew_lab/codec`. Session is trusted host state;
application commands are the boundary, not caller-manufactured Session records.
