# sunholo/social_dynamics

Experimental 0.2.0. Public exports are pure. Package IO ceiling is solely for
private `_smoke.ail`; no provider, wall clock, disk, game or hidden RNG access.

Start with `engine.init(config, actors, resources)`. Supply trusted deterministic
`Policies` with the config's stable authority/appraisal IDs. Use
`proposals.apply(config, policies, state, authenticatedPrincipal, trustedSource,
proposal)`, `relationships.deliver(..., Host, delivery)` and
`engine.advance(..., targetTick, boundaryBudget)`. Generated text is not principal
or source authentication. Only four offer/request operations are AI-permitted;
assignment/relief/consent decisions require an explicit authored/actor source.

Errors leave the incoming state unchanged. Exact accepted retries are no-ops,
including after expiry/revision change. Altered ID reuse fails. Generated inputs
cannot create raw effects/resources. Authority is configured, not universal.
`appraisalContext` returns only observer attributes/values/outgoing relationships
and evidence they know. Appraisal effects can modify only that observer's indicators
and outgoing relationships. Authorship grants evidence to its author without a
reaction; only host-validated delivery grants another observer knowledge.

Freeze the full Config and policy implementations for the session. The state keeps
its canonical config snapshot; same-ID config changes fail. Policy ID equality
cannot detect a host dishonestly replacing a function implementation. This is a
trusted host seam, not a callback sandbox. Exported low-level helpers (effects,
task/condition transitions) are for the trusted engine, not generated input.

All numbers are bounded +/-1,000,000,000; times/costs/capacities are nonnegative.
Strict IndicatorDelta never clamps. BoundedIndicatorDelta explicitly saturates a checked result at configured bounds; it refuses invalid current indicator state, unknown references and numeric overflow. Adding this ADT arm requires exhaustive consumers to update. Material available+reserved+consumed equals initial+inbound-outbound.
Accept reserves once; discrete project completion consumes configured amount and
returns the rest; stop returns unused reservation. Work allocations are concurrent
rate limits. `tasks.progress` derives checked allocation*elapsed ticks. This is
project accounting, not a substitute for ship physics or conserved ship mass.

One clock per session. Order is due tick, task-before-condition phase, then ID.
Durations >=1, recovery at next tick, cooldown then fresh entry-duration timer.
Reevaluate conditions after init, apply, delivery and every committed boundary.
Use separate sessions for external clocks; the host supplies causally received
inputs and maps their times. Partition equivalence applies only without inputs
between partitions. Pending accepts only continue/host abort; Blocked retains
prior committed boundaries and reports the failure. Never claim target reached.

Every collection is capped with no eviction. Examples use actors128, tasks64,
commitments64, reliefs64, evidence512, knowledge2048, accepted4096, operations16,
effects16, text4096 and wire65536. Config limits are positive <=1,000,000.
Indicator definitions, per-actor attributes/values/indicators, resource accounts,
rules and recipe costs/effects use the effects cap; recipes use tasks cap;
relationships use knowledge cap. Completed task IDs and accepted bodies remain.
Exhausted immutable retention requires a new session; save/reload migration and
century-long unbounded campaigns are outside this experimental release.

Wire `social_proposal/1` rejects unknown/repeated fields, fractions, unknown variants,
duplicate ID sets and trailing garbage. Canonical encoders sort ID collections,
preserve operation/event/effect order, and escape via std/json. State is a diagnostic
recording, not a validated deserialization API. Record initial config/policy IDs,
actors/resources and host input order for replay; external archive retains full log.

Run `make -f examples/social-dynamics/Makefile validate AILANG=/absolute/ailang`
from the repository root. See README and validation evidence. Run package tests and
source inline tests separately; report actual skips and runtime-only contracts.
Never publish without separate explicit authorisation.

Public module paths:

```ailang
import pkg/sunholo/social_dynamics/model (Config, State, Policies, Proposal)
import pkg/sunholo/social_dynamics/engine (init, advance, continueAdvance, abortAdvance)
import pkg/sunholo/social_dynamics/proposals (apply)
import pkg/sunholo/social_dynamics/relationships (deliver, appraisalContext)
import pkg/sunholo/social_dynamics/indicators (knows)
import pkg/sunholo/social_dynamics/tasks (progress)
import pkg/sunholo/social_dynamics/conditions (reevaluate)
import pkg/sunholo/social_dynamics/wire (decodeProposal, encodeState, encodeEvents)
```

Implementation clarification: partition equivalence covers successfully completed advances without intervening inputs. Blocked runs preserve the last committed boundary or idle advance; their retained tick can differ if a prior partition committed an idle time before the failure. They must preserve the same successful effects/event order and failing item, not falsely report the target reached. Generated outcome evidence uses reserved IDs `event-<sequence>`; initial/authored evidence may not use that prefix. Task/condition outcome evidence grants no automatic actor knowledge.

## Personality responses (0.3.0)

`personality` is a pure sidecar: initialize a complete five-trait baseline, accept
Host receipts for FirstContact/Loss/DeepTime/Betrayal, then advance against the
simulation clock. Major receipts set targets without an immediate change; at most
one point per trait per turn moves toward targets within baseline ±20 and 0..100.
Support/Conflict/Neutral interactions only influence an existing 20-turn response.
Targets are authored experimental rules, not a scientific claim or moral reward.
The calling host must verify actual observer knowledge, freeze perceived source,
and retain the sidecar in journals; supplying a Receipt alone is not authentication.
History retains at most128 receipts with no eviction; duplicates are exact and
idempotent, changed bodies or rewind fail. Keep current attributes in later
appraisal/AI context. No captain inference or personal-value drift is included.
