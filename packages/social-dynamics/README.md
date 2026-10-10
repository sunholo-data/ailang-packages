# Social dynamics experiments

A reusable pure AILANG kernel for emergent social situations. Host configuration
defines indicators, resource accounts, recipes, conditions and authority/appraisal
policies. There is no global moral score or prescribed ideal state.

The first experiments explore a captain choosing maintenance/rest, alien research
collaboration, or a smaller negotiated promise. A community repair/gathering example
uses the same public API without requiring ships, captains or OCEAN attributes.
These are tunable examples, not final game balance or human psychology claims.

From the monorepo root, with AILANG v0.52.0:

```sh
make -f examples/social-dynamics/Makefile deps AILANG=/absolute/path/to/ailang
make -f examples/social-dynamics/Makefile experiment SCENARIO=ship POLICY=care AILANG=/absolute/path/to/ailang
make -f examples/social-dynamics/Makefile experiment SCENARIO=ship POLICY=collaboration AILANG=/absolute/path/to/ailang
make -f examples/social-dynamics/Makefile experiment SCENARIO=ship POLICY=renegotiate AILANG=/absolute/path/to/ailang
make -f examples/social-dynamics/Makefile experiment SCENARIO=community POLICY=repair AILANG=/absolute/path/to/ailang
make -f examples/social-dynamics/Makefile experiment INPUT=/absolute/session.ndjson AILANG=/absolute/path/to/ailang
```

No Godot build, GPU, game assets, registry publication or live model call. The runner
uses only IO. Make prints distinct domain outcomes and saves the complete canonical
state/event trace to `.ailang/state/social-experiments/latest.ndjson`. Use
`examples/social-dynamics/run.sh interpreter recording.ndjson` for raw output or
`ENGINE=vm` for strict bytecode. Dependencies are local; regenerate locks after moving.

Edit the example Config/policies and start a new run to experiment with rules. Edit
recordings to change offers, assignments, promises and received evidence. Dynamic AI
can later provide the same supported proposal grammar; this sprint runs recorded
proposals only. AI cannot grant itself authority, broadcast hidden knowledge, invent
resources or choose arbitrary trust rewards.

Read [AGENT.md](AGENT.md) for API contracts and explicit retention limits, and the
[runner guide](../../examples/social-dynamics/README.md) for commands and input format.
The package is experimental and unpublished. Game integration, live generation,
visibility of captain KPIs and final refusal/authority rules remain subsequent work.

Opt-in `BoundedIndicatorDelta(actor, indicator, delta)` performs checked addition and saturates to configured indicator bounds. Strict `IndicatorDelta` retains rejection outside bounds. Unknown references, invalid current indicator state and numeric overflow remain errors, and appraisals can affect only their observer. The new effect encodes as `bounded_indicator_delta`; existing tags remain unchanged.

### Gradual personality experiment

Import `personality` alongside `model`. `initialize(actor, fiveOCEANValues, tick)`
returns baseline/current response state. `beginMajor(p, {receipt, kind:FirstContact})`
sets an individual target without changing traits. `advance(p, tick+1)` moves each
trait by at most one point; `receiveInteraction` can modify a currently active
response but ordinary dialogue never starts drift. Use validated received evidence,
not generated prose, to construct receipts. The independent crew-watch lab provides
a complete example with explicit scenario reports and development inspection.
