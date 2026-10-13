# Changelog

## 0.2.0

Crew strain (design `design_docs/planned/crew-strain.md`). Requires
`social_dynamics` 0.4.0.

- **Crew argue over lost capacity.** A ship event can take more than is
  available while running work holds the rest. The holders then take stances
  from their traits: hold score = (100 − A) + E/2 + C/2, plus 15 when
  overextended.
  - The least assertive are halted first (`social_dynamics` `halt`).
  - A halted crew member gains stress 5 + N/10.
  - One who held their ground loses regard for the colleagues who kept
    working. One who yielded gains +1 regard from them.
  - The argument is crew evidence `sf-<event>-<n>`.
  - Scenarios with events give crew a `regard` relationship (0..100, from 50).
- **Trust by personality.** New outcomes `complied_start` (a yes under
  orders) and `strained_start` (a yes while overextended). `traitDelta`
  scales every outcome's trust change by OCEAN traits and stress. Examples:
  - a strained yes: diplomat −1, engineer −2, skeptic −4;
  - an overridden refusal: −4 at A100 down to −12 at A0.
- **Strain in the response policy.** An optional `strain` block
  (`{indicator, threshold, shift}`) moves weight from accept and continue to
  decline and request_relief while the crew member is overextended, scaled by
  neuroticism. Policies without it are unchanged.
- The `sf-` id prefix is reserved for flows.
- **Behaviour change for orders runs.** Crew with OCEAN traits now get
  personal trust deltas, so orders sessions recorded on 0.1.0 replay to
  different trust values:
  - a "yes" under orders is `complied_start`, worth 2 − voice;
  - an overridden refusal costs −4 to −12, not a flat −8;
  - a denied relief costs −(2 + N/25), not −4.

  Consent sessions are unchanged. `session_test` pins the new values.

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
