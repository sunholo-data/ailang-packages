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

The public API is pure and deterministic. Known limits: the captain's id must be
`captain`; a session keeps at most 64 answered requests; conversation prompts are
still keyed by role in code.
