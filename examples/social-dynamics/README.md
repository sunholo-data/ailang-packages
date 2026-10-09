# Standalone social experiment runner

Run from the repository root with the Makefile commands in the package README.
Requirements: AILANG v0.52.0, Bash, make and jq. No game or AI capability is used.
`deps` regenerates both local locks. `scenarios`, `parity`, `replay` and `validate`
exercise five recorded paths. `experiment` supports `SCENARIO`, `POLICY`, `INPUT`,
`ENGINE=interpreter|vm` and `AILANG`; invalid choices and malformed input fail.

Input is finite NDJSON, 1..10000 nonblank lines, each <=65536 bytes. First line:

```json
{"command":"start","scenario":"ship","policy":"care"}
```

Ship policies: care, collaboration, renegotiate. Community: repair, festival.
Subsequent commands:

- `proposal`: `principal` host-bound identity, independent `source` (ai/authored/actor), and nested strict `social_proposal/1`.
  The CLI is an offline host: the outer source binds origin independently of inner proposal metadata.
  An untrusted network/model adapter must authenticate principal/source separately.
- `advance`: absolute integer `tick` and positive `budget` measured in boundary
  transactions. Repeat the same target to continue a pending chunk.
- `deliver`: `id`, `observer`, `evidence`, `causes`, `not_before`, `source`.
  This command is a host-authorised received observation, not a model operation.
- `abort`: host discards pending target, retains already committed boundaries.

Each accepted line emits `{state,events}`. Canonical records include causes, event
sequence, directed relationships, resources, conditions, knowledge and accepted-body
ledger. Duplicate deliveries emit the identical state and empty events. Errors emit
an error object and exit1. A blocked scheduler returns committed state/events plus
failure metadata and exits1; partial progress must remain visible in its trace.
State encoding is for inspection/replay evidence, not a save deserialization API.

Example tuning is in `config.ail`; recorded inputs in `recordings/`. `ship-collaboration`
completes more observations and incurs fatigue/readiness costs; care recovers and
repairs; renegotiation changes promise terms and yields lower expected support.
Support here is a configured counterpart trust reaction to received promise content;
this is not a whole civilisation simulator or a judgement of which choice is best.
Only one scheduler clock is used per run. Initial request evidence represents already
received information; `not_before` demonstrates later host receipt. Relativistic delay
mapping belongs to a future game adapter.

IO main has no fixed effect-count budget because it reads variable-length recordings;
shell preflight bounds input count/size. Pure logic is checked separately. Compiler
contracts needing ADT/list/HOF reasoning can remain runtime assertions; evidence
reports distinguish these from Z3 proofs and note native generator skips.

Pinned-v0.52.0 VM detail: std/io.readLine is evaluator-only. The strict VM path uses the same pure `session.recording` entry with structured arguments and zero capabilities. The interpreter stdin wrapper and VM pure replay produce byte-identical NDJSON; no VM fallback is enabled.
