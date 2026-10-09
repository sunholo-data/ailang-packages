# Reusing the Deliberating Nouls decision demo

Inspected 2026-10-09: `ailang-demos/decisions` and
`sunholo/decisions@0.4.0`, already present on packages/main. The demo is a
browser artificial-life playground with an AILANG simulation. This social lab
can run independently on the CLI. No live provider calls were made for this
comparison, and no demo or game integration is delivered by this release.

## What to reuse

- `souls.ail`: decision points triggered by needs, changed perception and
  cadence; personality-dependent confidence gates and sampling of available
  choices. Ask a crew member whether to accept, decline, raise a concern or
  request relief when circumstances change, rather than on every render frame.
- `bank.ail`: retain the whole typed Decision, observation snapshot, questions,
  distribution, confidence, random roll and selected action. Replaying a saved
  answer is reproducible; making the same live request again is not.
- `host.ail` and `oracle.ail`: prepare/complete separation keeps network waiting
  outside world updates. Validate the result against current actor, task,
  revision and clock before admitting an operation. Snapshot staleness requires
  an explicit host policy; a model's answer alone cannot grant authority.
- The demo's Now / Self / Story / Evidence inspector: show current indicators,
  personality, known evidence, alternatives and actual consequences. Keep model
  predictions separate from observed outcomes.
- Recorded synthetic answers and offline browser/CLI tests: iterate without
  keys, paid calls or large game builds.

## Ownership and mapping

`sunholo/decisions` supplies typed judgments, probability distributions and
confidence routing. `sunholo/social_dynamics` owns accepted task transitions,
resource reservations, commitments, directed relationships, received evidence
and consequences. Personality and OCEAN are host-configured actor attributes,
not a universal morality or success score. Thresholds depend on the actor and
stakes; an uncertain choice can defer rather than force an action.

Use a separate effectful adapter depending on both packages. Give Jev only the
actor's perceived context and legal options. Map a sufficiently confident saved
choice to one validated operation. Authorisation comes from the host's bound
principal and source, never generated metadata. AI output may offer tasks,
concerns, relief requests or commitments; acceptance requires the explicit actor
decision path. Text generation can propose narrative or bounded offers, while
Jev chooses among legal alternatives. Neither writes raw indicator deltas.

The Nouls already own needs, movement, identity and social preferences. Adding
this package must avoid maintaining a second independently changing copy of the
same state. Start with tasks, promises and received outcomes; retain the demo's
movement and physiology. Keep one scheduler clock and deliver outcome evidence
only to actors who receive it.

## Next bounded experiment

Extend the CLI lab first: a captain offers two competing projects; two crew
members with different attributes decide whether to accept, decline or request
relief using saved synthetic Jev Decisions. Record perception, legal choices,
gate, roll, operation and resulting causal trace. Test replay, uncertainty,
stale responses, task contention and personal consent before enabling live calls.

Then add an opt-in Nouls scenario with shared repair work and personal promises,
showing reservations, fatigue and received relationship consequences in its
existing inspector. Its current runtime is v0.40.2; the social package requires
v0.52.0. Upgrade and validate that demo's own WASM runtime and native/browser
tests in isolation before connecting them. Other demos retain their runtimes.

References: [demo README](https://github.com/sunholo-data/ailang-demos/blob/main/decisions/README.md),
[typed decisions guide](https://github.com/sunholo-data/ailang-packages/blob/main/packages/decisions/AGENT.md),
[social library guide](../../packages/social-dynamics/AGENT.md).
