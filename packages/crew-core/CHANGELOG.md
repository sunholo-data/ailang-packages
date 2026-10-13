# Changelog

## 0.1.0

First release, split out of the local crew-lab example (S-CREW-CORE-SPLIT). A pure
captain/crew host for social and narrative games on `social_dynamics`:

- `scenario`: decode and validate `crew_scenario/1` JSON (captain and crew, OCEAN
  traits, priorities, starting indicators, offered work with held and spent
  supplies and bounded effects, rest, overextension, trust in the captain,
  supplies); `config(scenario, policy)`; `scenarioHash` (canonical sha256).
- `session`: the host. `start(scenario, line)`, `offer`, `ask`, `complete`,
  `startTask`, `resolve`, `cancel`, `captainReply`, `input` (NDJSON commands) and
  `recording`. Consent or orders, agreements, relief, conversations, gradual
  personality, atomic failures. `untraced(s)` skips per-call trace encoding for
  batch runs (same states, about 3x faster).
- `policy`: the authored response policy (`crew_response_policy/1`), reaction
  weights, `chooseReaction` and `authoredAnswer` (reaction plus answer body).
- `host_policy`, `actor_policy`, `personality_host`, `conversations`, `codec`.
- `example`: the five-specialist first-contact ship (generated from crew-lab's
  `data/watch-scenario.json`).

Long sessions: the answer bank keeps 64 answers for idempotent retries; when full,
answers to expired requests (which can never be retried) are dropped first, so a
session can run for many turns (60-turn crew-sim runs are clean). Scenario limits:
256 tasks, commitments and reliefs, 2048 evidence, 8192 knowledge. `callLimit` in
`crew_response_policy/1` is 0..64; the watch policy default is 12.

The public API is pure and deterministic. Known limits: the captain's id must be
`captain`; finished tasks are never archived, so runs slow down as they grow (one
seed: 12 turns about 1 s, 60 about 8 s, 120 about 40 s); conversation prompts are
still keyed by role in code.

Also in this first release:

- **Resource flows (S-CREW-BUBBLE-RESOURCES).** Optional fields in
  `crew_scenario/1`, so existing scenarios decode and replay unchanged:
  - resource `kind` (stock or capacity; a capacity is never consumed);
  - work `yields`;
  - top-level ship `events`, which move units at a tick and are heard by the
    whole crew.
- `scenario`: `Transfer`, `ShipEvent`, `Yield`, `resourceKind` and `yieldsOf`.
- `session`: applies due yields, then due events, after each completed advance.
- New module `flows`: balanced transfers (`transfer`, `transferAll`,
  `appliedDelta`, `balanced`). An outward transfer never takes reserved units.
  `social_dynamics` is unchanged; transfers use its existing
  `transferredIn` and `transferredOut` books.
