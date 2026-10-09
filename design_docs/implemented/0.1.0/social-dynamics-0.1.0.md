# sunholo/social_dynamics 0.1.0: causal social simulations

| Stapledon pillar | Score | Reason |
|---|---:|---|
| Choices Are Final | +2 | Explicit decisions and their consequences remain in recorded history. |
| The Game Doesn't Judge | +2 | Domain-defined indicators; no moral score or ideal state vector. |
| Time Has Emotional Weight | +2 | Named clocks, commitments and duration-based conditions. |
| The Ship Is Home | +2 | Directed relationships and task conflicts create human-scale consequences. |
| Grounded Strangeness | +1 | Actor knowledge and causal contact boundaries remain explicit. |
| We Are Not Built For This | +2 | Capacity and autonomy constrain cooperation. |

**Status:** Implemented and locally validated 2026-10-09; independent final evaluation pending. Mark approved; independent design round2 PASS.
**Priority:** P1. **Version:** new experimental package 0.1.0, not published.
**Implements:** Mark's direction: task-driven conditions, captain trust/authority,
crew-to-crew reactions, dynamic AI-created events, shared micro/macro causal mechanics,
and different ways to play without one correct strategy. He explicitly requests reusable
AILANG package support. Source designs are in the isolated design clone at
`/private/tmp/stapledon-human-design-20261009/features/next/`:
`human-life-bridge-commons.md` and `shared-social-dynamics-and-events.md`.
**Depends on:** AILANG v0.52.0; standard library only. No Godot, game sim, AI provider,
physics package or transport dependency. **Estimate:** 2,500 implementation/test/example
LOC plus documentation; 8 working days including review buffer, provisional velocity.

## Problem and verified existing surfaces

The game has pure AI request bookkeeping (`sim/ai.ail`) and a separate service
(`ai/wire.ail`), but the former enumerates text/voice/portrait/avatar and purposes
line/news/archive/probe. A social-effect proposal is a new boundary; do not smuggle it
into accepted dialogue. Existing relationship, society and orchestrator designs describe
intent but supply no reusable package implementation in the inspected package tree.

Registry searches performed on 2026-10-09: social → LinkedIn API client; event →
billing packages and AG-UI; simulation → relativity/celestial; personality → none.
`pkg info/docs sunholo/agui` inspected: it encodes agent transport lifecycle, not
task resources, conditions, actor knowledge or social consequences. Do not depend
on it to model domain events. Local `packages/decisions/AGENT.md` describes a network binding for System One
decision models, not social evolution; the pure kernel does not require model calls.

Source bases: packages `2b3c9b2`, game `5bc4aff`. Both original checkouts contain
other work; use isolated clones. No game files change in this sprint.

## Goals and non-goals

Deliver a pure reusable kernel with domain-supplied indicators, resources, directed
relationships, task recipes, reaction policies and condition rules; validate structured
generated proposals atomically; demonstrate two different domains without source changes.

Initial examples: bridge/Commons work versus a promised external collaboration;
and a non-space community project. All tuning values are example configuration,
not package defaults, scientific claims or final Stapledon mechanics.

Live AI calls, provider routing, portraits, the ship UI, game protocol changes,
biological generation, civilisation evolution, mutiny, a galaxy reputation score,
publication and deployment are outside this sprint. Dynamic content is represented by
recorded structured proposals; the provider adapter comes after the core boundary is proven.

## Package and API proposal

Directory `packages/social-dynamics`, module prefix `sunholo/social_dynamics`.
Public modules: `model`, `indicators`, `relationships`, `tasks`, `conditions`,
`proposals`, `engine`, `wire`. Types crossing the package boundary use `export type`.
Pure exports use explicit pure signatures and meaningful contracts; intra-package
imports use `./`. Minimal library effects are empty; if `_smoke.ail` uses printing,
the manifest ceiling is IO solely for that private boot entry, as in existing packages.

Manifest: experimental 0.1.0, Apache-2.0, `[release] kind = "feature"`, repository
tree URL for `packages/social-dynamics`, metadata and exact dependencies (none).
README, AGENT.md and CHANGELOG 0.1.0 are required. No package publication is authorized.

### Model

- Bounded string IDs identify actors, groups, indicators, resource accounts, tasks,
  rules, sessions and proposals. IDs are unique within each category.
- Domain `Config` gives each indicator unit, integer bounds and policies; there is
  no built-in happiness, captain, species, currency or optimum. Integer model values
  and integer clock ticks avoid undefined tolerances in replay comparisons.
- Directed `Relationship(from,to)` holds domain-defined dimensions. Default policies
  live in examples. Human OCEAN can be supplied as actor attributes to a reaction policy;
  the core has no universal psychology formula and does not impose OCEAN on aliens.
- Actor knowledge is explicit evidence IDs, not omniscient global state. Policies
  receive only the permitted appraisal context. State remains available to validation.
- A domain-defined authority/capacity policy evaluates a proposed assignment as
  `Allowed`, `Conditional(requirements)` or `Refused(reason)`; no automatic mutiny rule.
- All collections have configured hard limits; example safety caps are actors 128,
  active tasks 64, proposal operations 16 and observations 64. Exceeding a cap is an
  explicit refusal, not truncated state or a partially applied transaction.

### Tasks and resources

Task recipes are supplied by the host and reference participants, a named session time,
duration/work requirements, prerequisites, resource reservations and typed effects.
Cost, progress and completion effects are separate. Reserve once at acceptance;
consume/release according to the recipe; task retry or completion cannot duplicate cost
or reward. Negative inventory, missing actors and unauthorized assignment are refused.

Resource transfers and commitments conserve quantities. Consumption is an explicit
domain operation and records its sink; the package cannot create inventory from an
AI-provided delta. The game's closed-mass and energy accounting remains the host's
physical ledger, never a made-up package formula. The first examples model only a
recoverable project-material account and work capacity, not ship mass or propulsion.

### Time, conditions and reactions

v0.1 uses **one authoritative scheduler clock per Session**, with integer ticks and
host-defined units. The ship example uses ship minutes; a separate external session
can use its own units. Host-delivered messages explicitly connect sessions after the
host maps their causal receipt times. The package never compares local ticks from two
sessions and never calculates relativity or signal propagation.

`advance` targets this session clock only. Reject rewind. Order crossed boundaries by
`(dueTick, phase, objectId)`: task completions, condition transitions, then queued
observation deliveries; each item commits against the preceding committed state.
Re-evaluate rules after a boundary transaction; schedule any resulting condition
boundary no earlier than the next tick. All task/condition durations are at least one
tick. A delivered observation produces at most one finite appraisal batch, not recursive
same-time appraisal. A reaction cannot mint another observation or schedule a task.

Partition invariance is promised only for advances on this one clock with no intervening
inputs or config changes. Interleaving counterpart inputs differently is a different
causal history, even if final clock values match. Pin config ID/revision and target in
a continuation; while pending, accept only its matching continuation or a host abort.
A per-call work budget pauses between boundary transactions and never skips consequences.
Final state and emitted sequence match a larger-budget run of the same ordered inputs.

Condition rules specify threshold direction, entry duration, separate recovery band
and cooldown. Polling alone cannot refire an active condition. No desired-range policy
is inferred for a dimension that is monotone beneficial.

Knowledge is granted by validated initial state, accepted authorship of new content
(all its cited causes must already be known), or host-delivered observations. Authorship
does not trigger an appraisal; received observations do. The host is responsible for sender/receipt
causality; input includes `notBeforeTick`, and early delivery refuses unchanged. This is
a local receipt gate, not proof of astrophysical causality. An observer appraisal gets
own attributes/current indicators, relevant outgoing relationships and already-known
public evidence; never other actors' private evidence. The policy is trusted deterministic
host code, not a sandbox for malicious callbacks. Every returned effect is nevertheless
validated: only that observer's outgoing relationships and self-owned indicators can
change, within bounded deltas and declared dimension limits. Invalid batch rejects the
whole observation transaction. Duplicate `(observer,evidence)` grants do nothing.

### Generated proposals and recording

Schema `social_proposal/1`: proposal ID, base revision, cause/evidence refs, participants,
session clock expiry and bounded operations, with an acting principal bound by the host. Supported operation grammar initially:
offer a task from a configured recipe, raise a concern with existing evidence,
request relief from an existing task, propose a named commitment.

AI creates participants' situations, text and combinations of supported actions; it
does not supply arbitrary code, raw trust rewards, new resources or hidden-history edits.
The host provides recipes and policy configuration. Actor permissions and authority
are independent of whether input came from a model, authored content or the player.

Validate schema, size, references, context revision, evidence visibility, expiry,
permissions and affordability against current state, then apply the entire proposal
atomically. Invalid and stale input returns a typed error with unchanged state.
IDs provide at-most-once application: identical replay is a no-op; same ID with a
different canonical body is refused. Rejected input consumes no resources or event IDs.

Accepted inputs and resulting events have canonical, versioned encodings and sequence
numbers. Replay the same initial state/config and inputs without AI calls. Domain history
retention must be explicit: v0.1 uses bounded evidence IDs and stores the full emitted log
in the example harness, outside core state; overflow refuses new evidence rather than
silently forgetting who knows what. No hidden RNG: selection is host input in this version.

The pure library performs no provider calls, disk I/O, wall-clock reads or global access.
The effectful example harness reads recordings and prints trace output. A later game adapter
will supply true proper/external times and physics-validated message delivery, not the kernel.

## First two examples

**Ship:** maintenance and observations compete for the same work time; a recurring
alien research commitment creates obligations. One policy prioritises maintenance/rest,
another collaboration, a third renegotiates. Different outcomes and directed reactions
are asserted; there is no overall winner. External responses are recorded counterpart
actions delivered no earlier than a host-supplied receipt time, not a full civilisation sim.

**Community:** residents commit work and material to a shared repair versus a public
event. Reuse the same package without any captain, ship or OCEAN requirement. Each example
supplies config, policies, actors, recipes and recorded generated proposals.

## Fast standalone experiments

Mark explicitly requests rapid iteration without game builds. The example runner is
a first-class deliverable, not a one-off test fixture. A small NDJSON session accepts
configuration/initial state, decisions, absolute clock advances and recorded generated
proposals, then emits canonical state changes and causal event traces. No Godot import,
GPU, game asset fetch or package publication is needed for local runs.

Provide named scenario variants and inspectable config/input recordings. Running the
same initial state with changed policies or player inputs creates comparable traces;
changing config starts a new recorded experiment and never rewrites an existing run.
The runner prints causal records and separate domain-defined outcomes, without a
composite score or ranking. Record measured timings once implemented; do not promise
a speed before measuring. An interactive console/UI and live model adapter can follow.

Proposed commands: `make -f examples/social-dynamics/Makefile experiment SCENARIO=ship
POLICY=care AILANG=$A`, the same with `POLICY=collaboration` or `renegotiate`, and
`experiment SCENARIO=community POLICY=repair`. Names are example choices, not imposed
play styles. `experiment INPUT=/absolute/path/session.ndjson` replays custom authored
or generated proposals through the same validation boundary. Missing input, invalid
config, malformed JSON and unrecognized options must fail clearly.

## Command-checkable acceptance criteria

All commands are proposed interfaces; none is claimed to pass before implementation.
`A` is the pinned absolute AILANG v0.52.0 path, `P=packages/social-dynamics`.

| ID | Criterion | Command |
|---|---|---|
| AC1 | Public interfaces compile; library has zero-effect exports; package manifest/quality evidence complete | `$A check --package $P`; `(cd $P && $A pkg quality --strict .)` |
| AC2 | Directed relationships, actor knowledge and differing policy reactions; unknown/unauthorized refs refused | `(cd $P && $A test relationships_test.ail)` |
| AC3 | Reservations/consumption/release conserved; partial invalid proposal leaves state unchanged; retries don't double-spend | `(cd $P && $A test tasks_test.ail && $A test proposals_test.ail)` |
| AC4 | Threshold duration, recovery, cooldown and event deduplication verified | `(cd $P && $A test conditions_test.ail)` |
| AC5 | Single-clock rewind refusal, simultaneous boundaries and permitted partition/continuation invariance | `(cd $P && $A test engine_test.ail)` |
| AC6 | Versioned codecs round-trip; stale revisions, oversized input and altered duplicate IDs rejected | `(cd $P && $A test wire_test.ail && $A test proposals_test.ail)` |
| AC7 | Three ship choices have distinct explainable traces, no universal score; second domain imports identical API | `make -f examples/social-dynamics/Makefile scenarios AILANG=$A` |
| AC8 | VM/interpreter traces byte-identical; recordings replay with no AI/Net capability | `make -f examples/social-dynamics/Makefile parity replay AILANG=$A` |
| AC9 | Actual native/inline tests, meaningful contracts, quality and dry-run packaging evidence recorded separately | `make -f examples/social-dynamics/Makefile validate AILANG=$A` |

## Milestones, risks and delivery

S1 model/indicators/relationships (500 LOC), S2 tasks/conditions/time (700),
S3 proposal validation/codec (650), S4 two examples/parity/package evidence (650).
Total 2,500 LOC; test-first; independently evaluated before landing.

Risks: premature generality (two small domains, bounded operations); arbitrary psychology
(host policies, labelled example tuning); dominant strategy (contrasting traces, no balance
claim); invalid generated content (atomic validation); timing drift (partition tests);
state growth (explicit limits); dependency pollution (no game/provider dependency).

Deliver library and examples only after sprint approval. Plan, JSON, evidence and docs
are reviewable now. Package release requires separate explicit publication authorization.

## Open decisions and review gates

Proposed freeze for this first sprint: experimental `sunholo/social_dynamics`, pure domain
kernel, no live provider/UI integration, no publication, default policies in examples.
This does not resolve game KPI visibility, captain's final authority/refusal rules,
event generation autonomy or final balance. Those decisions remain in the design interview.

Attended design-quorum triggers: 1 (API/schema freeze) and 3 (new indicator/resource
semantics and recorded schema). Independent reviewers must examine this draft before
it proceeds to an approval-ready sprint. General AILANG compiler axioms are out of scope:
this changes no parser, compiler, runtime or shared protocol; Stapledon pillar scoring
and package contracts are the applicable design criteria.

## Verification log

V1: game AI kinds/purposes read at `5bc4aff:sim/ai.ail`; social proposals require a new boundary.
V2: reusable package search and AG-UI docs inspected as described above; registry audit recorded.
V3: package AGENTS and local package skill read; pinned binary reports v0.52.0/bf2436a.
V4: `ailang docs package-authoring` read; teaching prompt loaded, active prompt version v0.16.6.
V5: current game do-not-touch ownership read from charter; this sprint changes package files only.
V6: API and commands above are proposals, not unverified claims about working source.

## Normative v0.1 boundary contracts (review revision 1)

These contracts resolve the independent review objections. They govern over any
earlier high-level shorthand. They describe proposed interfaces, not compiled code.

### Public boundary types and calls

`Config` contains config ID/version, session ID/time-unit label, ID/value/collection
limits, indicator definitions, resource accounts, task recipes, condition rules and
policy IDs. `Policies` supplies trusted pure authority/appraisal functions whose stable
IDs are part of the recorded config. Changing policy implementation requires a new
config version and a new run; replay must supply the same policy implementation.

`State` contains config identity, session tick, committed revision, event sequence,
actors/attributes/indicators, directed relationship dimensions, resource accounts,
pending/active/completed tasks, pending/active commitments, condition lifecycle,
evidence and observer knowledge, accepted proposal `(id, canonicalBody)` ledger,
scheduled items and optional continuation. Lists are serialized in ascending ID order;
events retain sequence order. All clock arithmetic and configured values use bounded
integers; overflow returns an error rather than wrapping or silently clamping costs.

Proposed exported pure calls:

| Call | Result and invariants |
|---|---|
| `init(Config, actors, resources) -> Result[State, Error]` | validates full config, uniqueness, referenced IDs and initial ranges |
| `appraisalContext(State, observerId, evidenceId) -> Result[Appraisal, Error]` | refuses unknown/unseen evidence; returns the filtered projection described above |
| `apply(Config, Policies, State, Principal, Source, Proposal) -> Result[Step, Error]` | all-or-nothing state and event batch; exact duplicates return `Duplicate` and unchanged State |
| `deliver(Config, Policies, State, Delivery) -> Result[Step, Error]` | host-authorized input only; not-before gate, knowledge grant and reaction are one transaction |
| `advance(Config, Policies, State, targetTick, budget) -> AdvanceResult` | commits bounded scheduled transactions; returns Done, Pending(token), or Blocked |
| `continueAdvance(Config, Policies, State, token, budget) -> AdvanceResult` | token/config/target/cursor must match; same sequence as equivalent unsplit advance |
| `abortAdvance(State, Principal, token) -> Result[State, Error]` | host-only boundary; discards unprocessed target, retains prior committed boundaries and current tick |
| `encodeProposal(Proposal) -> string`, `decodeProposal(string) -> Result[Proposal, Error]` | strict version/schema and deterministic canonical representation |
| `encodeState(State) -> string`, `encodeEvents([Event]) -> string` | deterministic recorded trace; no random or hidden data |

`Step={state, disposition:Applied|Duplicate, events}`. A refusal is `Err` and preserves
the entire incoming state. `AdvanceResult` carries state and events in all variants;
Blocked includes failing item ID, due tick and typed error. Successful prior boundary
transactions remain committed, the failed transaction changes nothing, and session tick
stays at the last committed tick. Target future time is never falsely reported reached.

`Event={schema:"social_event/1",seq,revision,tick,kind,causeIds,payload}`. Closed kinds:
TaskOffered(offerId), TaskAccepted(taskId), ConcernRaised(concernId),
ReliefRequested(requestId), ReliefResolved(requestId,accepted),
CommitmentOffered(commitmentId), CommitmentAccepted(commitmentId,partyId,active),
TaskCompleted(taskId), ConditionEntered(ruleId), ConditionRecovered(ruleId),
ObservationDelivered(evidenceId,observerId), ReactionApplied(observerId,evidenceId,
boundedEffects). Payload fields are typed IDs, booleans and bounded integer effect
records; text is only in the associated recorded proposal/evidence, not executable.
Scheduled boundary evidence references are immutable and become known only through delivery.

Error ADT cases: InvalidConfig, InvalidSchema, UnsupportedVersion, UnknownId,
Unauthorized, UnseenEvidence, StaleRevision, Expired, AlteredDuplicate,
InsufficientResource, CapacityExceeded, InvalidPolicyEffect, InvalidTransition,
ClockRewind, InvalidBudget, NumericOverflow, PendingAdvance, InvalidContinuation.
Cases include bounded offending ID/detail; stable wire error names use snake_case.

### Operation grammar and authority

`Principal=Actor(id)|Host`; this value is supplied by the authenticated host boundary,
not trusted from generated text. `Source=AI|Authored|ActorInput` is likewise supplied
by the host, determines permitted operation classes, and must match the recorded origin.
Proposal includes `principalId` which must match the supplied principal.
Each generated operation requires the principal to know the cited cause/evidence.

| Operation | Payload | Transition |
|---|---|---|
| OfferTask | offerId, recipeId, participantIds, causeIds | creates a pending offer; no inventory reservation or work starts |
| RaiseConcern | concernId, evidenceIds, addresseeIds, text | records a concern known to its author; no automatic trust adjustment or knowledge broadcast |
| RequestRelief | requestId, taskId, causeIds | active participant records request; work and reservations unchanged |
| OfferCommitment | commitmentId, partyIds, terms, dueTick, causeIds | records a pending proposal; no implied recipient consent |
| AcceptTask | offerId | authorized actor/host commits configured assignment policy; Allowed starts task/reservation, Conditional checks all requirements then acts as Allowed or refuses, Refused changes nothing |
| ResolveRelief | requestId, releaseRemaining:bool | authorized supervisor/host accepts or declines relief; acceptance stops task and returns unused reservation; no implicit replacement worker |
| AcceptCommitment | commitmentId | each party accepts only for itself; active once all party acceptances recorded; obligations stored, no automatic reward |

Only the first four are permitted in AI-origin proposals in this sprint. The last
three are explicit host/player/counterpart decisions, not authority invented by the
model. `origin=ai|authored|actor` is recorded metadata, not authentication; the caller
binds allowed operation classes. A generated project can be new situational content
and a new combination of actors/terms, but must name an existing effect recipe.

`Delivery={deliveryId, observerId, evidenceId, causeIds, notBeforeTick, sourceId}`
is host-authorized; it is the only grant of received observation knowledge after init.
Accepted principal-authored concern/offer/commitment content becomes evidence known to
that principal only, without an appraisal. All cited causes must already be known;
authorship cannot reveal hidden evidence. Evidence/knowledge capacity is checked inside
the same staged proposal: failure rolls back content, knowledge, events, revision and
dedup entry together. Task participation alone grants no observations.
Delivering evidence already known to that observer (including its author) returns a
no-op with no appraisal, events, revision or extra ledger entry. Validate host authority,
source/reference shape and receipt gate first. Unknown-author/other-observer and
author-self-delivery fixtures must show one authorship grant, no self-reaction, and
exactly one reaction after another observer receives it. Repeated delivery is a no-op.
It can expose concern/project evidence to others. An AI operation cannot call deliver.
The initial actor knowledge set is validated against initial evidence.

### Transaction, resource and failure semantics

Validation order: context/config/principal shape; accepted-ID lookup; exact canonical
duplicate returns Duplicate even after revision/expiry changes; altered ID reuse refuses;
then capacity, current revision, expiry/permissions/evidence and staged operations.
Each operation validates against the private state produced by preceding operations,
including cumulative reservations. Only a wholly valid transaction commits one new
revision, contiguous event sequences and one dedup entry. No partial event emission.

For each inventory account: `available + reserved + consumed = initial + transferredIn
- transferredOut`; consumed has a named sink. Reservation moves available to reserved;
work moves recipe-defined amounts reserved to consumed; stopping/completing releases
unused reservation. Work capacity is a renewable **rate/allocation limit**, never
inventory: sum of concurrent task allocations cannot exceed capacity; elapsed task
progress follows rate × ticks with checked arithmetic. It does not manufacture material.
Completion fires once; retained completed IDs prevent reapplying it.

Pending offers/commitments, tasks, evidence/knowledge, scheduled items and accepted-ID
ledger all have separate finite caps (example accepted ledger: 4096). v0.1 has no eviction:
unique input at capacity refuses; exact duplicate still succeeds. Full history remains
available to the example runner; starting a new session is the explicit recovery for
retention exhaustion. This is suitable for bounded experiments, not yet a century-long
unbounded save. Document limits prominently in AGENT.md.

Scheduled boundary transaction uses the same staged validation. Capacity overflow or
invalid policy effect yields terminal Blocked at that item, never an endless silent retry.
Host may abort and submit valid configuration-preserving inputs that remove/cancel the
offending task where authorized; unrecoverable evidence/dedup exhaustion requires a new
session. Do not change frozen config mid-session. Each boundary produces bounded events;
reaction output has a hard configured cap and cannot recursively deliver observations.
Zero/negative durations, impossible schedules and same-time self-rescheduling refuse.

### Wire example and compatibility tests

Canonical proposal field order is fixed: schema, id, config_id, base_revision,
principal_id, origin, expires_tick, causes, operations. Object fields inside operations
have their documented order; arrays of operations preserve input order, ID sets sort
and reject duplicates. Output has no optional whitespace, UTF-8 strings use std/json
escaping, integers emit decimal without fractions. Decode rejects unknown fields,
wrong types, repeated keys, duplicate IDs, out-of-range integers and unknown variants.
Canonical identity is the bounded canonical body itself, avoiding a crypto dependency.

Illustrative authored proposal (the following compact line is the proposed golden):

```json
{"schema":"social_proposal/1","id":"p1","config_id":"ship_v1","base_revision":0,"principal_id":"scientist","origin":"authored","expires_tick":60,"causes":["request1"],"operations":[{"type":"offer_task","offer_id":"offer1","recipe_id":"observations","participants":["scientist"],"causes":["request1"]}]}
```

Boundary tests must use a **separate consumer package** importing exported types/calls,
not only same-package tests. Include this exact golden and representative encode/decode
goldens for each variant and error; decoder malformed/duplicate-field tests establish
the chosen strictness. Existing std/json APIs are not asserted to enforce it automatically;
the executor must implement/probe the strict boundary rather than assume it.

Extra required fixtures: collectively unaffordable task acceptances; a last failing
operation; conditional requirement missing/met; duplicate after revision/expiry;
hidden/early/repeated observation; forged other-observer effect; overflow at completion;
invalid appraisal; attempted same-time cycle; full dedup ledger; pending continuation
input refusal. Two-clock counterexample is documented as **different host input order**,
not falsely asserted equivalent. Equivalent same-session partitions must be byte-identical.

Example tradeoffs: care prioritises recovery/readiness but completes fewer observations;
collaboration delivers more observations at fatigue/maintenance cost; renegotiation may
reduce both workloads and expected external support. These are target fixture differences,
not predictions of human behaviour or a proof of balanced gameplay.

Implementation clarification: partition equivalence covers successfully completed advances without intervening inputs. Blocked runs preserve the last committed boundary or idle advance; their retained tick can differ if a prior partition committed an idle time before the failure. They must preserve the same successful effects/event order and failing item, not falsely report the target reached. Generated outcome evidence uses reserved IDs `event-<sequence>`; initial/authored evidence may not use that prefix. Task/condition outcome evidence grants no automatic actor knowledge.

Implemented State additionally stores `configBody` (canonical frozen Config) and Event stores `evidence: Option[string]`. Every public task/condition mutation checks frozen context and pending continuation. Scheduler task/condition outcomes stage finite evidence atomically; only explicit delivery grants actor knowledge. CLI proposal commands bind `source` independently of nested origin; Blocked output includes committed state/events and terminates with error. See [validation report](social-dynamics-validation.md).
