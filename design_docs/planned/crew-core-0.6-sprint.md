# Sprint S-CREW-CORE-0.6: the Archive as a crew actor (archive-npc A1)

**Why:** the game's archive-npc design (stapledons-godot `design_docs/planned/r2/archive-npc.md`, A1), implementing stapledons-design `features/future/archive-crew-trust.md`. The canon makes the Archive a full NPC with individual trust relationships, but the crew simulation doesn't know it exists. The game asked the crew lab for a special actor kind in crew_core.

**Mark's rulings (attended 2026-10-15):**
- **OQ3:** trust in the Archive only. Captain–Archive coupling is built behind a switch that is **off** by default.
- **OQ4:** integrity changes **only from events**. Decay with ship time is built behind a switch that is **off** by default.

**Authorization:** Mark, attended 2026-10-15: "yes use same scale for trust for all. and bear in mind the numbers arent player facing, but influence descriptions. and do your recommendation for archive events". Recorded in stapledons-design's decision log (#25).
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.8).
**Registry reuse:** none (inside crew_core and the lab).
**Depends on:** crew_core 0.5.0 (#146).

## Design in crew_core terms

- **The actor.** A scenario may name one `archive`: `{id, name, integrity, confidence, ocean?}`.
  - It is an actor in the engine, with indicators `integrity` and `confidence` (0..100). It has no stress, fatigue or morale.
  - It is never one of the `workers`. The host refuses offers, asks and relief requests to it, and the auto-captain never picks it.
- **Relationships.** Both directions with each worker: `trust` and `regard`, starting at 50 unless the scenario says otherwise.
- **Events: a new host command `archive_event`.** `{kind, witnesses, revision, tick}`, where kind is one of:

  | Kind | Effect |
  |---|---|
  | `answer_confirmed` | witnesses' trust in it up |
  | `answer_contradicted` | witnesses' trust in it down |
  | `crisis_help` | witnesses' trust in it up |
  | `crisis_failure` | witnesses' trust in it down |
  | `confusion_witnessed` | witnesses' trust in it down |
  | `captain_backs` | the coupling below |
  | `repair` | integrity up |
  | `degraded` | integrity down |

  - The host journals each event, it replays, and each witness hears it as evidence (`ar-<id>`).
  - The game decides when these happen: the voice misremembering becomes `confusion_witnessed`, and the analyst's integrity pass becomes `repair`. AI words never raise an event.
- **Trust deltas.** The design table's ranges (on −100..100), halved onto crew_core's 0..100 scale and turned into one number per witness by their traits, as `codec.traitDelta` does for crew outcomes. For example, `answer_contradicted` is −5 to −12: low agreeableness and high neuroticism sit at the harsh end. Deterministic, with no rolls.
- **The Archive's trust in each crew member** moves with their behaviour toward it: backing it, or confirming or contradicting its answers. The design's "information filtering" stays game-side, read from these numbers.
- **The switches** sit in the response policy:
  - `archive.coupling` (default off): when on, `captain_backs` moves each witness's trust in the captain by their trust in the Archive. Loyalists rise; skeptics fall.
  - `archive.decay` (default 0 per year): when non-zero, integrity falls at each year turn.
- **Readouts.** `archiveOf(session)` returns integrity, confidence, and trust and regard by crew member, for the game's Archive card ("Ligaya trusts it; Andrei doubts it").
  - **The numbers are never player-facing** (Mark). They choose descriptions, so the readout also gives each value's **band**: `trustBand(v)` is devoted (90+), trusting (70–89), neutral (31–69), skeptical (11–30) or hostile (0–10), and integrity has its own bands (healthy 80+, degraded 50–79, compromised 20–49, critical under 20). The game words from the bands.
- **Refusals** (the integration agent's request): an `archive_event` with an unknown kind, an unknown witness, a stale revision, or no Archive in the scenario comes back in the host's `blocked:<code>:<detail>` form.

## Milestones

| ID | What | Gate |
|---|---|---|
| X1 | The scenario's `archive` actor: decoder, engine actor, relationships, refused as a worker | tests on both engines; a scenario without `archive` gives byte-identical sessions, so the six parity recordings replay unchanged |
| X2 | `archive_event`: journalled, replayed, evidence to witnesses, trust deltas by traits, integrity from `repair`/`degraded` only | tests for each kind; a seeded mutation (wrong delta sign) is caught; interpreter == strict VM |
| X3 | Switches `archive.coupling` (off) and `archive.decay` (0) in the policy | tests: with defaults, `captain_backs` leaves captain trust unchanged and integrity is constant over a year with no events; with them on, both move |
| X4 | Lab: last-messages-home gains the Archive; claims on v3 | claims: trust moves by the table; integrity is constant without events (OQ4); captain trust is unmoved by backing (OQ3); the 0.4.1 gate still has 0 errors |
| X5 | 0.6.0: changelog, AGENT.md, independent evaluation (score of 70 or more), PR, publish, sha to the integration agent | CI green; publish |

## Questions for Mark (answered 2026-10-15)

1. **The trust scale.** The design table is written on −100..100, while crew_core's trust is 0..100 with 50 neutral. Plan: halve the ranges onto 0..100 (for example, "prediction wrong −10 to −25" becomes −5 to −12) and map the levels the same way (Devoted 90+, Trusting 70–89, Neutral 31–69, Skeptical 11–30, Hostile 0–10). Recommended, since crew and Archive trust then share one scale. **Answer: yes, one scale for all trust; the numbers aren't player-facing but influence descriptions.**
2. **Who raises events.** The game raises them from what happens, and crew_core only applies them. Recommended: it keeps AI words out of decisions, and the game already owns the Archive voice. **Answer: yes.**

## Not in scope

- The presence art (A3) and the Crew console card (A2): game-side.
- Generational trust (founders, ship-born): waits on cohorts with featured crew births.
