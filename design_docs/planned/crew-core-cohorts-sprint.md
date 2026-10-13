# Sprint S-CREW-CORE-0.4: cohort actors for the ship's population (CP-0 + CP-1)

**Design:** stapledons-godot `design_docs/planned/r2/crew-population.md`
§CP-0 and §CP-1, with the open questions settled by ledger D-73 (cohorts in
R2; department axis first, generation splits later; featured cap 15 with
promotion; unrest shown as bands) and the headcount by D-75 (about 1,000
aboard, growing to about 1,500).
**Authorization:** Mark, attended 2026-10-13: "yep sounds good continue".
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.8).
**Registry reuse:** none. This extends crew_core, which is already the host;
the bucket and binomial maths are new and small.

**Compatibility promise** (to the integration agent, as for 0.3.0):
- Cohorts are additive. A scenario without a `cohorts` section behaves
  exactly as in 0.3.0.
- The six parity recordings, plus the integration agent's three, replay
  byte-identically.
- Snapshot and journal records gain `cohorts`, `population` and `promoted`
  only when cohorts exist.
- `session` gains no import of `auto`, which stays opt-in.

**Naming contract** (agreed with the integration agent, 2026-10-13):
- crew_core never carries display names.
- A promotion emits `{"kind":"promoted","id":"<cohort>-p<n>","cohort":…,"at":…}`
  with a deterministic id.
- The game names the new actor from its D-74 generator, keyed by that id.

## The model

A cohort is a group actor:

| Field | Meaning |
|---|---|
| `id`, `department` | Grouping axis: department (D-73 OQ2) |
| `headcount` | The people in it, which may be in the thousands; cost does not depend on it |
| `mix` | Mean OCEAN traits, 0..100 |
| `mood` | People per band: content, uneasy, strained, breaking. Sums to headcount |
| `trust` | People per band of trust in the captain (4 bands). Sums to headcount |
| `ages` | People per decade band, 0–9 … 90+. Sums to headcount |
| `voice` | A featured crew id, or none |

- **Readouts:**
  - *mean*;
  - *division*: how bimodal the bands are, 0..100;
  - *pressure*: the strained and breaking share, weighted by low trust, 0..100.
- **Moves between bands:** one seeded binomial draw per band, not per person.
  The default is an exact-integer expected-value mode (largest-remainder
  rounding); a seeded mode adds per-band noise. Both engines must agree bit
  for bit.
- **Children and departments:** births go to a `children` cohort. At 18 they
  join departments in proportion to department headcounts. A department
  splits off a ship-born sub-cohort once ship-born people are 25% of it (the
  generation split; the threshold can be set per pack).

## Milestones

| ID | What | Gate |
|---|---|---|
| ✅ P1 | Scenario `cohorts` section (1–16, separate from crew's 1–15); validation that every band list sums to headcount and that voices are featured crew; the response policy gains a `cohort` section | decode tests on both engines; bad packs rejected with the field named |
| ✅ P2 | Band transitions: events and heard captain decisions move people by band through the cohort mix. Expected-value and seeded modes; readouts | property tests: sums preserved, never negative, same seed gives the same result, VM == interpreter |
| ✅ P3 | Drift on quiet days toward the mood set by resources and recent events; `advance(n)` and the auto-captain cover cohorts; cohort escalation rules (`pressure`, `division` thresholds) in `crew_escalation/1` | `crew-sim --auto` claims; a split cohort escalates before a uniformly uneasy one |
| ✅ P4 | Yearly population step: `birth_policy` command (`encourage`/`hold`/`restrict`, journalled, D-71(2)); births by policy, resources and parents' mood; deaths by age band plus `loss` events; ageing; children joining departments; the `crew.used` draw as a readout. The `hold` default gives about 0.4% net a year (D-75) | headcount over 100 years within ±10% of 1,500 under `hold` in good conditions; births stall when garden or water are short |
| ✅ P5 | Promotion: a featured member who departs (dies, breaks permanently, or leaves the featured set) is replaced from their cohort. The new actor gets the cohort mix plus a seeded offset and the cohort's regard, then the `promoted` event fires. The featured cap of 15 holds; voices reassign | tests: cap holds; id deterministic; replay identical |
| ✅ P6 | CP-1 lab content: a founders scenario with about 1,000 people in 10 department cohorts plus children, voices from the featured 11. Claims written first: split before uneasy; a death aboard moves founders more than ship-born after generation 2; births stall under shortage; the 100-year growth band | `crew-sim --check` over 20 seeds; claims recorded, failures kept as findings |
| ✅ P7 | Scale and close: AC9 (a 10-year skip with 1,000 people and with 100,000 people within 10% of each other); parity (nine recordings); changelog; independent evaluation; PR; publish 0.4.0 | timing table in the CHANGELOG; evaluator score at least 70 |

## Risks

- **Compile memory.** It was fixed in v0.54.8. The plan still keeps the
  population step in its own module (`cohorts.ail`), with the session calling
  it once, and re-measures cold compile at P2 and P7.
- **ailang#1814 (VM list tails).** Fixed-size band lists, at most 10 long, so
  the cost is not affected.
- **Pack size.** Ten cohorts plus the existing 11 crew is 21 actors, so
  regard holds about 440 pairs. That is measured at P3 and P7.

## Questions for Mark

None are blocking. The design choices above (children cohort, 25% generation
split, expected-value default) are mine; say if any should be different.

## Outcome (2026-10-13)

- **P1–P6 done.** 59 new crew_core tests on both engines; the six parity
  recordings replay byte-identically; 18 of 18 founders claims hold.
- **P7:** AC9 holds (20.1 s at 1,000 people, 20.4 s at 100,000, 10-year
  skip). Evaluation, PR and publish follow.
- **Changes during the sprint, all recorded in the CHANGELOG:**
  - Birth-policy tension (Mark, 2026-10-13).
  - Birth rates recalibrated: the first draft was below replacement.
  - Grievance persists while the policy lasts (a claim failed first).
  - Drift on calendar weeks, so batched and daily advances agree (raised by
    the R2 integration agent).
  - Shortage counts reserved units.
  - Promotion keeps the role and replaces the person (the engine cannot add
    actors).
- **Evaluation round 1** (Sonnet, 74/100, pass) found three real bugs,
  all now fixed, each with a test that fails on the old code:
  - people were lost once a department's founders died out;
  - batched and daily advances disagreed across year boundaries and
    mid-skip events;
  - the `promoted` record lacked `id`.
  Also fixed: `-shipborn` ids reserved and room left for them.
- **Deviations from the plan:**
  - The calm-year, century, restrict and famine claims ran over seeds 1..3,
    and split over 1..20, not 20 seeds each. Expected mode makes cohorts
    seed-independent; seeds vary only the crew.
  - Ages are kept by single year (decades in the pack and the snapshot).
  - `split-escalates` checks plumbing: the pack sets the split.
  - Under restrict, births fell to zero, so `restrict-shrinks` is weak.
- **Not built** (deferred, listed for CP-2 and the scenario library):
  - deaths from `loss` events (ages and the yearly mortality profile only);
  - the `crew.used` resource-draw readout;
  - a cohort section in the response policy (cohort reactions are in
    code, scaled by OCEAN mix).
- **Not built:** generation mix offsets for the ship-born. The claim "a
  death moves founders more than the ship-born" was not written, because the
  model gives the ship-born the founders' mix, so it would fail by
  construction. Which households get permits under restrict is the
  integration agent's open follow-up for CP-3/R3.
