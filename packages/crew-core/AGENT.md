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

Limits: the captain's id must be `captain`; at most 16 pending and 64 answered
requests per session; conversation prompts are keyed by role in code.
