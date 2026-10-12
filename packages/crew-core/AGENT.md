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
