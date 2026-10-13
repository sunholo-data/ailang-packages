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
