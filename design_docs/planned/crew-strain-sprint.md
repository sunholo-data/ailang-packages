# Sprint S-CREW-STRAIN

**Design:** [crew-strain.md](crew-strain.md). Approved by Mark on 2026-10-13
("yep great continue"), with the halting rule "crew argue it out" and trust
that depends on OCEAN traits.
**Stacked on:** #134.
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.5).
**Registry reuse:** contribute. `social_dynamics` 0.4.0 gains host `halt`; it
is published.

| ID | What | Gate |
|---|---|---|
| ✅ S1 | `social_dynamics` 0.4.0: `tasks.halt` and the `TaskHalted` event; tests; published | package tests on both engines; `pkg quality --strict`; `ailang publish` |
| ✅ S2 | crew_core: crew argue over lost capacity (hold score, halts, stress, regard), `regard` relationships for scenarios with events, `sf-` reserved | `strain_test.ail` (4 tests) on both engines; `make core-tests` |
| ✅ S3 | crew_core: trust by personality (`complied_start`, `strained_start`, `traitDelta`) and the optional policy `strain` block | `codec_test` table; `policy.ail` strain tests |
| ✅ S4 | crew-lab: orders captain stops resting people unprompted; peak, overextended, halted, regard and shortfall measures; claim metrics; pack `policy.json`; claims written first; 20-seed results in REVIEW.md | `make tests replay parity claims-test scenario-pack-test`; `crew-sim --check` |
| ✅ S5 | Close: changelogs, notes, independent evaluation, PR; publish `crew_core` after merge | `make validate` (keyless) |

## Module checklist

| Module | Contracts | Effects | Inline tests |
|---|---|---|---|
| `social_dynamics` `tasks.halt` | include: `ensures` that the tick and the task count are unchanged | pure | include (`tasks_test`) |
| crew_core `codec.traitDelta` | include: `ensures` −12..4 | pure | include (`codec_test`) |
| crew_core `policy` strain | include: decoding validated by `policyOK` | pure | include |
| crew_core `session` arguments | private helpers | pure | include (`strain_test`) |
