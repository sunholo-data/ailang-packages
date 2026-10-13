# Sprint S-CREW-BUBBLE-RESOURCES

**Status:** ✅ Completed 2026-10-13. R1–R4 pass. Independent evaluation round 1: 80/100 (Sonnet), and all seven findings were fixed. `make validate` passes keyless. Pack claims: 41 of 46 hold, with the findings in `REVIEW.md`.

**Design:** [crew-bubble-resources.md](crew-bubble-resources.md)
**Stacked on:** #133 (spike/crew-memory) → #132 → #131.
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.5).
**Registry reuse:** none. No registry package models resource flows; `social_dynamics` 0.3.0 is reused as is.

## Milestones

| ID | What | LOC (est.) | Depends | Gate |
|---|---|---|---|---|
| ✅ R1 | crew_core: resource `kind`, `events`, `yields`, decode and validation, transfer applier keeping the invariant, journal records; byte-identical replay fixture for old scenarios | 350 | — | `make core-tests` |
| ✅ R2 | crew-lab: `crew_sim` resource measures (`min`, `zero_ticks`, `stockouts`, `in`, `out`); claims metrics `resources.<id>.*`; `bubble.ail` (`allocate`, `lintPack`) with tests | 250 | R1 | `make tests claims-test` |
| ✅ R3 | Pack: claims first, then events, yields and kinds in four scenarios, `lintPack` in `scenario-pack-test`; 20-seed results in `REVIEW.md` | 200 | R2 | `make scenario-pack-test`; `crew-sim --check` |
| ✅ R4 | Close: CHANGELOGs, AGENT notes, sprint JSON, independent evaluation (a different agent), PR | 50 | R3 | `make validate` (keyless), `pkg quality --strict` |

## Module checklist (AILANG syntax gate)

| Module | Contracts | Effects | Inline tests |
|---|---|---|---|
| crew_core `scenario.ail` (events, kinds, yields) | include: decoders `ensures` bounded counts | pure `! {}` | include |
| crew_core `session.ail` (`applyEvent`, `applyYields`) | include: `ensures` invariant holds | pure | include |
| crew-lab `bubble.ail` | include: `allocate` `ensures` non-negative and `lintPack` totality | pure | include |
| crew-lab `crew_sim.ail` measures | include | pure | include |

## Risks

- **Event evidence needs the knowledge limit** (8,192, raised last sprint). Bounded by 32 events.
- **Replays and recordings of the default ship** must stay byte-identical. R1's fixture guards this.
- **CI time** is already about 47 of 60 minutes. Keep the new tests cheap: seeds 1..3 in CI, 20 seeds only locally.
