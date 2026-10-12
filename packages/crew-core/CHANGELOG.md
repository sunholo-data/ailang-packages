# Changelog

## 0.1.0

First release, split out of the local crew-lab example (S-CREW-CORE-SPLIT).
`scenario` decodes and validates `crew_scenario/1` JSON: the captain and crew,
OCEAN traits, priorities, starting indicators, offered work with costs and
bounded effects, rest, the overextension rule, trust in the captain and named
supplies. `config(scenario, policy)` derives the social_dynamics configuration;
`scenarioHash` is the sha256 of the canonical encoding, so layout changes do not
alter it. Errors name the field. The public API is pure.
