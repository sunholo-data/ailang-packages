# sunholo/crew_core

Experimental 0.1.0. Public exports are pure; the IO ceiling is solely for the
private `_smoke.ail`. No file, clock, provider or hidden RNG access.

The caller reads scenario JSON and passes the text in. That keeps runs
replayable: a journal records `scenarioHash(s)`, and a changed file is a
different scenario. Do not load scenarios from package assets
(`std/package.assetPath` resolves the newest installed version, not the
locked one; ailang#1772).

```ailang
import pkg/sunholo/crew_core/scenario (decodeScenario, config, scenarioHash)
match decodeScenario(body) {
  Err(e) => -- e names the field, e.g. "work_cook: unknown resource sugar"
  Ok(s) => match config(s, "consent") { ... }   -- "consent" or "orders"
}
```

`crew_scenario/1` fields: `schema`, `id`, `indicators` (ids, must include
`trust`), `indicator_defaults` (every actor gets these in this order),
`captain {id, values, start}`, `crew [{id, role, ocean{openness,
conscientiousness, extraversion, agreeableness, neuroticism}, values, start,
work [{id, name, purpose, duration, costs [{resource, reserve, consume}],
effects {indicator: change}}]}]`, `rest {purpose, duration, effects}`,
`overextended {indicator, threshold, recovery, duration, cooldown}`,
`trust_in_captain`, `resources [{id, name, initial}]`. Extra fields are
rejected. Traits and indicators are 0..100; effects -100..100. Each crew
member gets a `rest_<id>` recipe; work ids must not collide with it.

Optional flows (absent fields keep the old behaviour, byte for byte):
- **Resource `kind`:** `"stock"` (the default) or `"capacity"`. Work may
  reserve a capacity but never consume it.
- **Work `yields`:** `[{resource, amount}]`, up to 4. Transferred in when the
  work completes; stopped work yields nothing.
- **Top-level `events`:** up to 32 of `{id, at, text, transfers [{resource,
  delta}], major?}`.
  - After an advance reaches tick `at`, the host moves the units.
  - A negative delta takes only available units, never reserved ones, and the
    body records requested and applied units.
  - Each event is raised as captain evidence `ev-<id>` and heard by every crew
    member. `major` (loss, deep_time, first_contact, betrayal) also reaches
    personalities in watch-v3.
  - Yields are raised as `yd-<task>` and heard by the task's participants.
  - Ordering: after a completed advance, all due yields fire first (tasks in
    state order), then due events (scenario order).
  - Caller ids may not start with `ev-`, `yd-`, `sf-`, `hear-` or `ship-`;
    those prefixes are reserved for flows.
  - **Arguments.** When an event takes more than is available and running
    work holds the rest, the holders argue (hold score from traits; the least
    assertive are halted first; see CHANGELOG 0.2.0).
  - Scenarios with events add a crew-to-crew `regard` relationship and a
    `regard` indicator to the engine config.

Trust: `codec.traitDelta(outcome, ocean)` turns each reported outcome into a
trust change based on the observer's traits. Under orders, a "yes" is
`complied_start`, or `strained_start` when the crew member is overextended.
The response policy may carry `strain {indicator, threshold, shift}`.
  - Each flow fires once. Accounts stay balanced (`flows.balanced`):
    available + reserved + consumed == initial + transferredIn − transferredOut.

## Resource units (`units`, 0.5.0)

A game's scenarios draw on resources from a table the game owns, given as
data (`crew_units/1`): `{"schema":"crew_units/1","name":"bubble","units":[{id,
kind, unit, physical, per}]}`. Each crew unit is `per` of the `physical`
quantity. `decodeUnits(json)` checks it (unique ids, stock or capacity, per of
at least 1). Every function takes the table first:
- `allocate(table, ship)`: a physical ledger to whole crew units, rounded
  down; unknown ids and negative amounts give nothing.
- `lintPack(table, scenario)`: "<id>: not one of the <count> <name>
  resources" or "<id>: must be a <kind>".
- `lintAgainstShip(table, scenario, ship)`: lintPack, plus "<id>: N units but
  the ship can spare M".
- `usedOf(table, consumed)`: crew units back to physical amounts.

crew_core never builds a table in. Stapledon's eight bubble resources live
with its scenarios (crew lab `scenarios/stapledon/resources.json`).

## Driving a session

```ailang
import pkg/sunholo/crew_core/example (firstContact)
import pkg/sunholo/crew_core/session (start, offer, ask, complete, startTask, input, untraced)
import pkg/sunholo/crew_core/policy (decodePolicy, watchPolicyBody, authoredAnswer)

-- start: host profile "watch-v3" adds personality and conversation sidecars.
match firstContact() { Ok(sc) => start(sc, "{\"command\":\"start\",\"policy\":\"consent\",\"scenario\":\"watch-v3\"}"), ... }
-- offer(s, "scientist", "work_scientist", "science") -> the task is Offered
-- ask(s, "scientist", "science", "r1")              -> s.pending holds Request r1
-- authoredAnswer(policy, r1, seed)                   -> {label, body, roll, seed}
-- complete(s, "r1", answer.body, answer.roll)        -> agreement or concern recorded
-- startTask(s, "science")                            -> holds supplies; consent needs agreement
-- input(s, "{\"command\":\"advance\",\"tick\":4,\"budget\":64}")
```

Every call returns `Result[Output, HostError]`; `Output.trace` is the JSON line a
journal stores (empty for `untraced(s)` sessions, which batch runs use). Failures
leave the session unchanged. `input(s, line)` accepts the same NDJSON commands as
crew-lab's `crew-host`, so an external host (a Godot simulation) can drive this
package over stdin/stdout. Asking produces a pending request: answer it later with
`complete`, which is how a background reply inbox fits without core changes.

Limits: the captain's id must be `captain`; at most 16 pending requests; the bank
keeps 64 answers and drops answers to expired requests when full (a retry of a
dropped answer reports `unknown request`); finished tasks are not archived (256 task
limit, runs slow as they grow); conversation prompts are keyed by role in code.

## Stand down (0.6.0)

At a check-in, a crew member under strain may ask to stand down, working or
not. In host terms this is a **duty check-in**, a check-in without a task:

- `{"command":"check_in","actor":W,"id":ID}`: the captain offers W's own rest
  recipe as task `sd-ID` under a duty agreement `duty-ID` due at the next
  tick, and asks W in the same call. The pending request has id `ID`, phase
  `duty`, legal `carry_on`, `stand_down`, `defer`, and expires at the next
  tick. Refused below the cooperation floor (trust under 20), for an unknown
  crew member, or while W already has an open duty check-in.
- Answer it as any request (`answer`). `carry_on` and `defer` change nothing;
  the subject lapses and archiving folds it. `stand_down` is W's concern
  `standdown-ID` to the captain. It opens no conversation issue.
- `{"command":"resolve_stand_down","id":ID,"release":true|false}`, the same
  tick: a grant has W accept the duty agreement, halts W's running work
  (reason `stood_down`, reservations released), starts the rest and reports
  `granted_stand_down` (+4 trust); a denial reports `denied_stand_down`
  (−(2 + N/25) trust, no stress).
- `session.checkIn` and `session.resolveStandDown` are the same calls as
  functions.

The response policy weighs phase `duty` with its `duty` rules. A policy with
none borrows its working weights: `carry_on` from `continue`, `stand_down`
from `request_relief` (and the strain shift applies to both).

The auto-captain (`advanceAuto`, step 2b) makes duty check-ins at a cadence of
2 or more when standing orders say `"stand_down":"on"` (the default; `"off"`
runs as 0.5.1). A crew member is checked in when strained (stress or fatigue
at the orders' tired line, or overextended), not resting, not asked about
relief this turn, without an open concern, at or over the cooperation floor,
and off cooldown: 30 days after a grant; 90, 180, then 360 after denials in
a row (kept in `AutoState.raised` as `stand_down/<worker>:<tick>:<denials>`).
The `relief` order decides. Acts: `reply` (label `stand_down`, `carry_on` or
`defer`), `stand_down_asked` and `stand_down_decision` (`granted` or
`denied`), detail `sd-<id>`. The opt-in escalation rule `stand_down` stops
before the decision and leaves it to the player (`resolve_stand_down` with
the escalation's detail as the id).
