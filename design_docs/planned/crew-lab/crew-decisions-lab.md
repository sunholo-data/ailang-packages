# Captain and crew: saved JEV decisions in the CLI lab

| Game pillar | Score | Reason |
|---|---:|---|
| Choices Are Final | +2 | Accepted assignments and received consequences remain recorded. |
| The Game Doesn't Judge | +2 | Distinct material/social trajectories, no combined goodness score. |
| Time Has Emotional Weight | +1 | Work, exhaustion and recovery evolve on one explicit ship clock. |
| The Ship Is Home | +2 | Captain, scientist and engineer negotiate useful work. |
| Grounded Strangeness | 0 | No alien generation in this slice. |
| We Are Not Built For This | +2 | Refusal, uncertainty and fatigue constrain cooperation. |

**Status:** Design quorum PASS (two independent reviews, revised once). Implementation in progress. **Target:** independent experimental
`sunholo/crew_lab@0.1.0` example. The social kernel remains 0.1.0.
**Priority:** P1. **Planner-Lane:** codex-ok.
**Authorisation:** Mark selected captain and crew in the CLI lab and instructed
“continue”. Scope follows the previously presented JEV integration notes: saved
synthetic decisions, competing projects, personal consent, replay and trust.
No game edits, live calls, registry publication or changes to other demos.
**Estimate:** 1,200 source/test/example LOC, four working days including review;
planning estimate, not a forecast of this attended session's duration.

## Problem and reuse

The existing social lab replays authored operations and demonstrates task costs,
thresholds and trust reactions. It does not assemble actor perception, ask a typed
JEV choice or retain the model alternatives that produced an NPC response.
`ailang-demos/decisions` already demonstrates confidence gating and banked sampling.
Reuse `sunholo/decisions@0.4.0` pure `buildRequest`, `parseAnswers`, `answer`, `gate`.
Reuse social_dynamics init/apply/deliver/advance and its exported model/wire.
New code is an independent example host and actor policy, not a second kernel.
No core exported signatures or origin permissions change.

## First scenario and experimental policies

Captain, scientist and engineer; two crew-specific projects (observations and
maintenance) competing for conserved project materials and work capacity. Rest
and relief provide alternatives. Configure bounded fatigue/readiness/observations
and directed trust in the captain. OCEAN-like attributes and personal values are
context, not an inflexible personality archetype or civilisation-wide score.

An offered task includes a personal work agreement between the captain and the
worker, represented by an existing Commitment. Both must explicitly accept it to
be active. Agreement acceptance is separate from the captain starting work.
Two illustrative authority policies may be compared:

- `consent`: captain may start only an active, unexpired agreement for that task.
- `orders`: captain may start a refused task while that worker's directed trust
  remains above the configured cooperation floor. The refusal/order becomes
  received evidence with a configured personal trust cost, not instant mutiny.

These policies and numerical effects are experimental fixtures, not game canon.
The refusal-policy interview is optional; after a reasonable reply window, use
both as explicitly labelled experimental comparisons unless Mark steers otherwise.
Refusal never becomes personal consent, including under `orders`.
Every task has one worker in this slice, keeping consent ownership unambiguous.

The host stores a typed immutable `TaskAgreement {task, agreement, captain,
worker, recipe}` for each offer, with unique task and agreement IDs. Validate its
exact matching task participants/recipe and agreement parties, activity and
`due > current tick` before a consent-policy start. Another agreement between the
same parties cannot authorise this task. No terms-text, causes or ID-prefix
inference. Offer creation, captain agreement acceptance and immediate receipt to
the worker are one atomic host command. The kernel authority callback stays fixed:
captain identity and cooperation floor. The additional consent/binding guard is
in the trusted host before apply; do not replace the callback under a stable ID.

## Actor decision boundary

A trusted host owns the actor policy `crew-choice-v1`, its principal binding and
legal action mapping. A model returns a closed choice distribution, never an
Operation, principal, source, authority rule or raw effect. For a known offer,
choices are accept agreement, decline, raise concern and defer. While working,
choices are continue, request relief and defer. Only the actor's own agreement
may be accepted; only their current task may receive a relief request.

The host-owned NPC policy may map a valid choice to ActorInput for that NPC.
This is explicit delegated self-decision, not a generated proposal changing its
origin. Raw AI proposals remain AI and still cannot AcceptTask, ResolveRelief or
AcceptCommitment. Captain assignment/relief resolution remains authored input.
Tests must distinguish these two routes and refuse cross-actor consent.

Confidence must clear a caller-owned finite 0..1 threshold before sampling a
response. Defer on uncertainty; do not force the argmax or add a silent fallback.
Use an explicit recorded finite roll in [0,1), not a hidden RNG. Sample in stable
label order from the validated distribution. At least one probability is positive;
keys are unique, exactly equal to the request's legal choices; probabilities are
finite 0..1 and total within 1e-9 of 1. Validate the chosen wire label, Answer variant,
confidence, required model/id and duplicate structural fields: parseAnswers alone
is not an input validation boundary (its decoder defaults missing numeric fields).
All fixture provenance is explicit `synthetic`; no calibrated-live claim or spend.
The complete response body and parsed Decision remain in the bank.
After validation, divide probabilities by their positive total in stable label
order. If rounding leaves an unselected tail, select the last positive label.
Never select a zero-probability label; use strict `roll < cumulative` comparisons.
Bank raw probabilities and normalized sampling probabilities separately.

## Prepare/complete, observations and staleness

`ask` captures a request ID, actor, subject, tick, revision, full config identity,
actor policy ID, threshold, legal choices, questions and exact actor perception.
Context uses appraisalContext: own attributes/values/indicators, outgoing
relationships and received evidence only. Never pass another actor's private
indicators, global unseen evidence or hidden host state. Project details must be
received as offer evidence before asking. Offer delivery is a documented immediate
host receipt to the addressed worker, not a broadcast trust update.

`answer` binds to a stored request. No request body from a response replaces it.
Reject changed config/policy/revision, expired request, unknown actor/subject,
pending scheduler or illegal transition before committing. A response judged at
an old revision requires a fresh ask; no silent rebasing. Bound bank/request
collections (64 completed, 16 pending), wire <=65536 bytes and command count10000.
Exact accepted request retries with identical body/roll are no-ops; altered reuse
fails. Even defer/continue have a bank entry; they do not fabricate domain events.
Check duplicate identity before staleness so a saved accepted retry stays safe.
Every request also binds the exact captured tick; idle clock changes invalidate
it even without a revision change. Its `expires` is `min(tick + 1, agreement.due)`
with checked addition; never ask at numericLimit. Validity requires current tick
equal to captured tick and current tick strictly less than expires. Commitments
remain invalid at `tick == due`. Pending guards precede duplicate retry handling.

`cancel_request(id)` is an explicit host command: atomically remove one pending
request and bank a cancellation with its request snapshot. It frees pending
capacity even after staleness. Completed/cancelled IDs are retained and cannot be
reused; they count against the 64-entry completed retention limit. This is not
automatic eviction. At retention exhaustion start a new session. Test sixteen
pending requests, a domain mutation, rejected stale answer, cancellation and fresh
ask recovery. Rejected commands never secretly reap requests.

A command stages host bookkeeping, domain operations and immediate receipts
atomically; any failure leaves incoming host and domain state unchanged. Advancing
uses the existing bounded scheduler. A blocked advance keeps earlier committed
boundaries and reports failure; it never claims the target was reached. Pending
advance accepts only continuation or abort. No hidden wall time or clock mapping.

## Consequences and reporting

Recipes own fatigue, readiness, observations and material accounting. Reactions
come from explicit received evidence and observer-local policy, not model floats.
Captain decisions produce a bounded structured report with a mechanically
recognisable outcome code (granted relief, denied relief, agreed start, refused
order). Do not infer effects from arbitrary narrative text. Receiver-specific
appraisal in this first fixture uses fixed illustrative outcome deltas, directed
trust and received captain/task provenance; no omniscient crew-wide bonus. OCEAN,
values and needs enter the saved request context; trait-weighted appraisal is
deferred and these synthetic answers do not prove a model used the attributes.
An uninformed colleague remains unchanged until explicit delivery.
Outcome codes use one closed ADT and exact encoder/decoder, validated against the
associated task/agreement and captain authorship; never substring-match arbitrary
narrative. Metadata stays host-owned and staged with the transaction.

Current kernel recipes apply effects on completion; stopping work releases its
reservation without consuming materials or charging partial fatigue. Progress
reports allocation times elapsed ticks, not partially accrued recipe effects.
This limitation remains explicit in the experiment and tests; partial-work
economics would require a separately designed kernel change.

The causal output retains domain state/events plus request, saved alternatives,
confidence, gate result, roll, selected response, mapped actor operation and
actual received consequences. Prediction and observed result are distinct.
Trust affects available cooperation but is not a mission victory score. Include
both useful work at personal cost and care at opportunity cost, with no winner.

## CLI and example files

`examples/crew-lab` is an independent package with path social-dynamics dependency
and exact decisions0.4.0 registry pin. Effects ceiling IO; only pure decisions
functions are called. `[bin] crew-lab` reads finite NDJSON, emits causal NDJSON.
Commands: start(policy), offer(worker,recipe,id), ask(actor,task,id),
answer(request,body,roll), start_task(task), resolve_relief(id,release),
advance(tick,budget), deliver(observer,evidence,id), abort. Strict keys/types/limits.
Also `cancel_request(id)` for stale/pending-request recovery.
Library error ADT plus host error ADT; no untyped null success or swallowed failure.
An interactive session can pipe commands; saved inputs are the repeatable tests.
The shell launcher preflights blanks/size/count. The stdin entry treats a blank
as EOF on pinned runtime; document it. Pure recording entry gives strict-VM parity.

- `examples/crew-lab/ailang.toml`: independent exports, IO ceiling, bin, exact dependencies.
- `examples/crew-lab/actor_policy.ail`: pure context, legal choices, validated saved answer and sampling.
- `examples/crew-lab/scenario.ail`: experimental config, recipes, authority and observer appraisal.
- `examples/crew-lab/session.ail`: pure host state, strict commands and atomic transitions/bank.
- `examples/crew-lab/main.ail`: finite stdin/output wrapper only.
- `examples/crew-lab/*_test.ail`: native actor, codec and consequence controls.
- `examples/crew-lab/recordings/*.ndjson`: contrasting complete runs and failure fixtures.
- `examples/crew-lab/Makefile`: deps/check/tests/scenarios/replay/parity/CLI-install/quality/validate.
- `examples/crew-lab/README.md`: immediate experiment commands and trace interpretation.
- `examples/crew-lab/AGENT.md`: trust boundary, protocol and explicit limitations.
- `examples/crew-lab/CHANGELOG.md`: feature description, runtime and validation limits.

## Acceptance commands (to be implemented, not passing claims)

A = absolute pinned v0.52.0 binary, bf2436a; teaching prompt version0.16.6 loaded.

| ID | Required behaviour | Command |
|---|---|---|
| AC1 | Actor perception excludes unseen/private information; unknown offer refused | `ailang test --package examples/crew-lab` (named context controls) |
| AC2 | Validate response variants, fields, probabilities, threshold and roll; confidence defers; deterministic sampling | same (named response/sampling controls) |
| AC3 | Self consent only; raw AI cannot accept; start authority differs between policies without fabricating consent | same (named consent/authority controls) |
| AC4 | Atomic failures, changed/stale requests, exact retries, capacity and pending guards | same (named host boundary controls) |
| AC5 | Work costs, refused order, granted/denied relief and delayed observer reactions have distinct causal traces | `make -f examples/crew-lab/Makefile scenarios AILANG=$A` |
| AC6 | Five contrasting recordings replay and evaluator/pure strict VM are byte-identical; invalid process input exits1 | `make -f examples/crew-lab/Makefile replay parity cli-test AILANG=$A` |
| AC7 | Runtime compilation, tests, inline examples, contracts/proof limits and strict quality honestly reported | `make -f examples/crew-lab/Makefile validate AILANG=$A` |
| AC8 | Existing social lab remains green with 5 recordings unchanged and kernel signatures unchanged | existing social-lab validate plus Git diff limited to new example/docs |

Mutation controls: bypass confidence gate, accept other actor's agreement, ignore
stale revision, charge accepted retry twice, expose unseen evidence, broadcast
trust without receipt. Each compiles and is killed by a behavioural test.
No live-provider, WASM or Godot claim. Measure scenario process time separately
from test/quality startup. Independent evaluator must review final code/trace.

## Verification log and review scope

- V1: social proposals `generated` explicitly rejects acceptance/resolution for AI;
  tasks.accept delegates authority to host policy; commitment consent is party-local.
  Read model/proposals/tasks in packages/social-dynamics at5d01829.
- V2: appraisalContext filters own outgoing relationships and known evidence;
  deliver gates Host and observer-local effects. Read relationships.ail.
- V3: decisions parseAnswers maps only requested answers but defaults absent numeric
  fields. gate requires threshold0..1 and refuses Noul; ChoiceA has a distribution.
  Read decisions/decide.ail:70–110,220–287. Host validation is additional.
- V4: JEV demo bank/oracle/souls/host inspected; record distributions and rolls,
  prepare/complete separation. Demo runtime0.40.2 is not being upgraded here.
- V5: registry search decisions/social; decisions0.4.0 is latest, installed API
  matches local guide. social kernel is available on main, not yet registry-published.
- V6: prior lab source/session tests and five recordings inspected; its authored
  replay does not implement this request/answer host adapter. This document extends
  its JEV integration notes, not a duplicate kernel design.
- V7: engine.advance idle paths update tick without revision; requests check both.
  Commitment consent is invalid at due <= tick. Native controls must include
  clock-only staleness, agreement-expiry equality, same-party/wrong-task consent,
  near-one probability totals and zero endpoints, and pending queue recovery.
- V8: pinned-v0.52.0 probe importing decisions with an empty effects ceiling
  compiled and returned `accept` on evaluator and strict VM, with no capabilities.
  Replay of saved parseAnswers/answer/gate is supported on the pinned runtime.

Quorum triggers 3 (new bank schema/KPI experiment semantics) and 4 (decision package
wire contract). External response fixtures are explicitly synthetic; vendor live
behaviour/calibration is not a load-bearing premise. Review against inspected
package contracts. No language/parser/compiler override. Shared core permissions,
existing social runner and legacy recordings are reused, not altered.

## Axiom assessment

| Axiom | Score | Evidence |
|---|---:|---|
| A1 Determinism | +1 | Explicit roll, recorded response, one ordered clock. |
| A2 Replayability | +1 | Whole request/Decision/body and actual consequences banked. |
| A3 Effect Legibility | +1 | IO wrapper; no Net, Env, AI or hidden RNG calls. |
| A4 Explicit Authority | +1 | Host binds actor self-policy; captain powers remain separate. |
| A5 Bounded Verification | +1 | Capped host collections, explicit invalid controls. |
| A6 Safe Concurrency | +1 | Revision-bound async completion and pending guards. |
| A7 Machines First | +1 | Strict NDJSON and typed failures. |
| A8 Minimal Syntax | 0 | Existing language and package types only. |
| A9 Cost Visibility | +1 | Project material reservation/consumption, zero provider calls. |
| A10 Composability | +1 | Two existing packages, independent host. |
| A11 Structured Failure | +1 | Error ADTs and atomic rejection. |
| A12 System Boundary | +1 | Model judgments separated from host mechanics. |

Net+11, no hard violation (A1/A3/A4/A7). This is author assessment, not quorum result.

## References and deferred work

[Prior kernel design](../../implemented/0.1.0/social-dynamics-0.1.0.md),
[JEV integration notes](../../../examples/social-dynamics/JEV-INTEGRATION.md),
[decisions guide](../../../packages/decisions/AGENT.md),
[social guide](../../../packages/social-dynamics/AGENT.md).
Game design branch: sunholo-data/stapledons-design design/human-life-bridge-first-level,
features/next/human-life-bridge-commons.md and shared-social-dynamics-and-events.md.
Relativity: future host maps proper time and causal messages per physics spec;
this experiment does not implement external clocks. Defer live JEV, AI prose,
Nouls/WASM upgrade, bridge/Commons UI, mutiny, aliens and century-long retention.
