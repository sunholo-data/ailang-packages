# A human-readable five-specialist watch

| Game pillar | Alignment | Constraint |
|---|---:|---|
| Choices Are Final | +2 | Published assignments, time and consequences remain in the journal. |
| The Game Doesn't Judge | +2 | No best policy, composite goodness score or graded ending. |
| Time Has Emotional Weight | +1 | Work holds people and capacity for actual host turns. |
| The Ship Is Home | +2 | Five specialists express competing interests before contact. |
| Grounded Strangeness | +1 | Archive analyses Spire readings; no cargo crosses the bubble. |
| We Are Not Built For This | +2 | Stress, morale and fatigue affect reactions; rest and refusal matter. |

**Status:** Reviewed: two independent PASS verdicts on revision1 plus controller PASS.
**Target:** experimental crew-lab successor. **Priority:** P0.
**Estimate:** four focused milestones, about 2,000 changed lines including controls,
2–3 development days with review buffer; not a delivery promise.
**Planner-Lane:** codex-ok.

## Authorization and problem

Mark requested five crew, specific resources, OCEAN-informed personalities and
qualitative player descriptions with numeric state available during development.
He approved reusable Archive compute slots plus finite replacement parts and medical
supplies in the attended interview on 2026-10-10. The initial policy menu remains
unintelligible to him: its short Consent/Orders labels precede their explanation.
His instruction to continue authorizes this bounded lab implementation. Numerical
tuning below is experimental scenario data, not canonical ship economics.

## Related work and duplicate gate

Read implemented `crew-journey-terminal.md`: it explicitly preserved the two-worker
scenario, materials costs and raw metrics. This successor changes those mechanics
and corrects onboarding that the user rejected after acceptance. It reuses that UI
package and host; it does not repeat their implementation. The scaffold search
ranked that document and the unrelated decisions use-case map highly; the latter
covers decision APIs and commerce examples, not this scenario. Their contents were
reviewed. Distinct requested scope is recorded here rather than creating another
terminal library.

Normative references: stapledons-design `vision/core-pillars.md`,
`features/future/crew-psychology.md` (scientist, engineer, medic, pilot, diplomat),
`features/future/spire-mystery.md` (Archive processing capacity), and the owned design
branch `features/next/human-life-bridge-commons.md` / `shared-social-dynamics-and-events.md`.
Bridge and already designed Commons remain the background. No new room geometry.

## Experience and first choice

The first visible page must say: you are captain; your crew is preparing for a
possible first contact; preparing people and equipment competes for time and
Archive capacity. Explain the first action flow and the policy choices before
accepting input, including at 40x16. Keep choice semantics in persistent chrome
rather than later pages. Help works before starting, with an example; help and
paging consume no host command, seed, journal or AI attempt.

Use plain choices: “Ask for agreement” means work cannot start until the person
agrees; “Use captain's authority” permits starting despite an objection, with
trust consequences and existing cooperation/capacity/resource checks. Neither
choice guarantees success. This is the watch's command style, not a moral grade.
Explain what choosing a style changes and that it lasts for this run.

Introduce five specialists alongside the player captain, six actors total. Roles
remain labels, no invented canonical names. Each has useful work, personal concerns,
a rest assignment, and a directed trust relationship to the captain. Main controls
lead to small menus for choosing work or rest rather than ten unexplained recipes.
Describe a project before offering it: purpose, worker, duration, required slots or
supplies. Offering hears a reaction; starting actually reserves resources; advancing
one turn moves work; completion returns reusable capacity and consumes supplies.
Failures explain what is unavailable and how to continue on the same decision.

Normal Bridge, Crew, Work, Log, Guide, conversation and recap show descriptive
psychological state and visible behavior, no gauges/scores/OCEAN labels or disclosure
that variables are hidden. Physical inventory counts, task progress and time remain
numeric. Examples: “looks tired”, “on edge”, “in good spirits”, “guarded with you”.
These are projections of actual state, not diagnoses or inferred new facts. AI receives
the numeric local perception and renders short speech consistent with it. Static
observation phrases are a reliable fallback and never claim an AI call occurred.
`--debug` explicitly enables developer-only raw metrics, OCEAN and sampling evidence;
it is off by default and may not be activated by an ordinary player key accidentally.

## Versioned scenario and resources

Keep legacy start `{command:start,policy:consent|orders}`, configs, actors, recordings,
response-policy file and cache signatures unchanged. Add an explicit modern start
variant (a closed scenario name such as `watch-v2`). Reject unknown variants/extra
fields. `crew-journey` defaults to this scenario; legacy player remains legacy.
Identity checks must recompute the expected config using both exact known variant
and policy, compare full encoded config, state ID/body/session and enforce recipe
ownership in that variant. Policy string stays consent/orders: no suffix that
would bypass the existing equality-based consent guard. Generic social kernel
reserve/consume/complete/relief semantics are reused without overrides.

Initial experimental stocks: 3 Archive compute slots, 3 replacement modules,
4 diagnostic cartridges. Slots are concurrent analysis capacity in the Archive,
not a claim that Spire itself is a computer. Reserve them while working, consume
zero; completion or granted stop releases them. Physical supplies reserve one,
consume one on completion; granted stop refunds the reservation under existing
completion-only lab semantics. Waiting never replenishes spent supplies.

| Worker | Work | Turns | Reservation | Completion |
|---|---|---:|---|---|
| Scientist | Analyse Spire readings | 4 | 2 compute slots | observations +25, fatigue +20, stress +10, morale +5 |
| Engineer | Service signal equipment | 3 | 1 slot, 1 module | readiness +20, fatigue +15, stress +5 |
| Medic | Prepare diagnostic supplies | 2 | 1 cartridge | readiness +15, fatigue +10, stress +5, morale +5 |
| Pilot | Plan approach observations | 2 | 2 slots | readiness +15, fatigue +15, stress +10 |
| Diplomat | Rehearse first-contact signals | 3 | 1 slot | readiness +15, fatigue +10, stress +10, morale +5 |
| Each specialist | Rest | 2 | None | fatigue -20, stress -15, morale +5 |

Psychological indicators use 0..100 bounds. Existing IndicatorDelta is strict:
out-of-range completion returns InvalidPolicyEffect and leaves work occupied.
Do not rely on validation to saturate. Add an explicit opt-in
BoundedIndicatorDelta(actor,indicator,delta) to the generic social Effect ADT.
It checks actor/indicator/reference/shape and existing state validity, uses the
checked addition, then clamps to the configured indicator minimum/maximum.
NumericOverflow remains an error, not disguised as a clipped result. The legacy
IndicatorDelta and RelationshipDelta branches and encoded tags remain unchanged.
Modern recipe effects use only this bounded indicator constructor, so repeated rest
at zero or useful work at maximum can finish and release the worker/resources.
Record actual resulting values, never claim the full nominal delta happened at a
bound. Supplies still consume even if a benefit is capped: describe that before start.

Extend shape/reference validation, relationships.ownEffect with the same observer-only
ownership check, and wire.effectJson with a distinct bounded_indicator_delta tag.
No new raw-effect command is accepted. Bump the experimental social_dynamics package
to 0.2.0 with release kind breaking because adding an ADT arm affects exhaustive
consumers; update known typed consumers and path-dependency locks. Config.version
remains wire schema1, while modern scenario IDs explicitly say watch-v2. Old encoded
configs/events and legacy outputs must remain byte-identical. Native controls cover
low/high/exact bounds, negative and nonzero indicator bounds, invalid current state,
missing references, numeric overflow, atomic rollback and forged cross-actor appraisal.
Installed repeated work/rest controls prove completion and release at both limits.

Add
stress and morale to fatigue/readiness/observations; directed trust is the relationship,
not the inert actor trust scalar. Work/rest effects occur at completion only; time
alone does not simulate deterioration. OCEAN attributes remain stable this slice,
using existing archetypes as experimental starting points. Initial states differ
by role and are recorded in source; no personality drift or clinical interpretation.

Authored modern reaction weights use all OCEAN axes plus fatigue, stress, morale,
values and directed trust, with closed legal labels and existing weighted seeded
selection. Stress can increase concern/decline/relief, morale can affect willingness
and continuation; boundary tests must demonstrate actual directional differences.
A condition rule per specialist reports sustained overextension with the existing
scheduler hysteresis/duration/cooldown semantics. No new unsolicited peer knowledge
or event propagation is claimed. The captain's authority still depends on the
existing directed cooperation floor. No universal mission KPI is introduced.

## Response library and isolation

Use a separate modern policy filename (for example response-policy-watch-v2.json)
with its own default rules, preserving any existing user file byte-for-byte. Modern
response signatures carry a new prompt version and exact scenario/config identity,
local frozen perception, legal labels, model and exact policy text. Legacy signatures
remain byte-identical. Changed state or policy cannot hit a legacy response bundle.

Modern prompt names the role and intended project from the scenario's trusted
catalog and asks for expressive speech: never numerical psychological scores,
OCEAN trait names, or declarations about concealed mechanics. Give it only actor-local
received evidence and relevant project context; do not add other crew's private
state or unknown inventory assertions. Config identity may be hashed/included in
signature but must not dump the entire config/effects as omniscient narrative input.
Do not treat AI text as legal effects, authority, resource creation or evidence.

Apply a bounded deterministic guard to modern AI/cache text before acceptance/cache
publication: reject explicit trait names, metric-score patterns and hidden-variable
claims. Document that this is a known-pattern guard, not a semantic proof. Permit
ordinary qualitative words (“fatigue”, “tired”, “anxious”) and physical quantities.
Rejected generation spends only its actual call and leaves the host request pending;
retry or an explicitly authored continuation stays available. Never rewrite an
already journalled quote. Authored offline starters must be context-aware summaries,
not quoted fake AI speech. Exact bundle/text/provenance and both selection rolls
remain recorded for replay and developer inspection.

## Verification log and conflict surface

| Premise | Source read/check on 2026-10-10 |
|---|---|
| Kernel reserve/consume are separate | tasks.ail reserve moves available to reserved; release returns reserve-consume; complete passes true, granted stop passes false. |
| Existing deltas reject rather than clamp | indicators.ail applyOne returns InvalidPolicyEffect when inRange fails; tasks.finish applies effects before publishing. indicators_test explicitly asserts effects cannot clamp into valid bounds. |
| Effect extension touches known exhaustive matches | rg IndicatorDelta/RelationshipDelta: model, indicators shape/reference/apply, relationships.ownEffect, wire.effectJson, crew journey_presenter.effects. No raw-effect decode command in wire/proposals; new constructor is trusted typed config/appraisal only. |
| Legacy identity is strict and recipe ownership is hardcoded | session.ail identity, binding, offer; recomputes scenario.config(policy), compares full state configBody. |
| Consent guard uses exact policy string | session.ail startTask checks policy == consent and agreed state. |
| All five OCEAN axes already reach reactions | scenario attributes, session.perception, reactions.defaultRules and weights. |
| Library generation is text-only and budgeted | store.generate uses AI@limit1 + decodeGenerated; resolve cache/offline/lock; existing play commit journals before exposed speech. |
| Old onboarding hides explanation in body pages | play.choosePolicy footer says Consent/Orders, only n/v/1/2/0 accepted; journey_presenter.opening supplies long body. |
| Terminal rendering already reusable | journey_flow/presenter imports sunholo/terminal_ui; dimensions 40..160 x16..60, safe plain/ANSI, line keys. |
| Reuse registry checked | successful searches social/terminal/content/decisions; social and terminal packages are experimental in-repo, decisions0.4.0 registered. Reuse local kernel/library/UI and pinned decisions. |

No compiler/parser/runtime modifications. Compatibility surface: Effect ADT (extend
with new opt-in constructor; versioned breaking release), legacy delta branches
(preserve), observer-owned appraisal restriction (reuse), wire effect tag (extend;
old tags/configs unchanged), legacy strict start
and configs (preserve), new closed start variant (extend), host freshness/authority
and receipt guards (reuse), journal envelope schema (preserve, new variant explicitly
in start payload), old cache/policy (preserve), modern signature/policy (version).

**Quorum trigger 3:** cost/KPI semantics and signature versioning. Independent
reject-by-default review is required before planning/execution. External-provider
quorum was rejected by automatic approval review because document sharing to those
destinations lacked explicit authorization. Safer alternative: two independent
frontier reviewers inside this Codex session. Both rejected round0 on delta bounds;
this revision adds the explicit bounded constructor and boundary controls. Preserve
their machine artifacts and re-review once; any remaining blocker stops execution.
Revision1 re-review completed: both PASS with no remaining design blockers; evidence
in watch-evidence/design-a-r1.json and design-b-r1.json. Controller concurs: explicit
bounded effect resolves completion failure without weakening legacy guards. Actual
implementation acceptance remains pending.
No new unverified vendor premise; provider and model remain the existing setup.

## Acceptance criteria and commands

1. `make -f examples/crew-lab/Makefile watch-test`: actual installed first page at
80x24 and40x16 explains captain/context/actions/policy, h help works before start,
reading views/pages has zero domain/seed/sequence/AI changes.
2. Native watch controls on interpreter and strict bytecode: six actors, five owned
work/rest recipes, three named stocks, unknown variants/config mutations rejected,
legacy controls unchanged; consent cannot be bypassed by variant.
3. Native completed-work and relief tests: slots release, supplies spend once,
repeat work exhausts actual stock, capacity/shortage rejection retains state; normal
UI explains reservations/shortage and completion-only refunds honestly. Repeated
rest/work at indicator limits completes without stranding reservations; legacy strict
overflow tests, new bounded-effect references/ownership/overflow/rollback controls pass.
4. Native reaction controls prove stress/morale/OCEAN affect selected weights; sustained
condition rules tested with scheduler, no invented peer receipt or composite grade.
5. Installed normal flows through every view and recap show qualitative state and
no numeric psychology/OCEAN; --debug shows real values and all five actors.
6. Prompt/signature/cache tests: v1 exact stability, v2 separation, local context,
score-disclosure fixtures rejected, physical quantities accepted, invalid generation
not cached, explicit retry/stock, zero provider calls in offline tests.
7. Modern journal recovery recording replays byte-identically both engines, retaining
raw exact quotes/provenance; old recording/CLI/play/library/terminal controls pass.
8. README/AGENT/changelog and playable walkthrough updated; scoped validation and
CI pass; independent evaluator checks actual frames/causal flows, not only totals.

Test commands: existing `make ... validate`, new watch-test target, social kernel
native suites, and `ailang pkg quality --strict examples/crew-lab`; document actual
solver verified/skipped/encoding errors separately. No new language-support claims.

## High-impact decisions, latitude and risks

Human decisions: pure AILANG, five specialists, descriptive psychology with development
inspection, reusable Archive capacity + finite supplies, first-contact preparation.
Agent choices: labels, numerical tuning as recorded experimental data, internal helpers,
fixture layout and phased menus. All costs require version identity, never retroactive
legacy tuning. Resource holds and truthfulness about completion-only consumption are
load-bearing. Risks: hidden numeric leakage through consequence/log/recap (audit all
surfaces); old user cache/policy overwrite (hash-preservation tests); profile consent
bypass (adversarial identity tests); cramped chrome (real minimum-size frames).

## Axiom compliance

| Axiom | Score | Reason |
|---|---:|---|
| A1 Determinism | +1 | Existing seeded selection and recorded publication preserved. |
| A2 Replayability | +1 | Explicit profile identity, old records preserved. |
| A3 Effect Legibility | +1 | Pure UI/config plus existing bounded IO/FS/AI adapter. |
| A4 Explicit Authority | +1 | Host guards and actor-local receipt remain mandatory. |
| A5 Bounded Verification | +1 | Native boundary/resource/identity controls. |
| A6 Safe Concurrency | 0 | Existing cache locks retained. |
| A7 Machines First | +1 | Raw causal journal remains structured; human UI is projection. |
| A8 Minimal Syntax | 0 | No language syntax changes. |
| A9 Cost Visibility | +1 | Distinguishes reusable holds from spent supplies. |
| A10 Composability | +1 | Reuses generic social, library, decisions and terminal packages. |
| A11 Structured Failure | +1 | Rejections preserve pending requests and published state. |
| A12 System Boundary | +1 | AI writes expression, host owns consequences. |

Net +10, no hard violations. Deferred: real multi-leg travel, alien negotiations,
peer disagreement propagation, new geometry, personality drift and universal KPI
schemas. This lab slice prepares that experimentation; it does not claim those
systems are playable yet.
