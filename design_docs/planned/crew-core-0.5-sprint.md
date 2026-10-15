# Sprint S-CREW-CORE-0.5: resource units as data in crew_core (and the Archive actor, after OQ3/OQ4)

**Why:** Mark's repo-use review (2026-10-15, "yep please clear this up").
- **The problem.** The game's `sim/crew_resources.ail` is a port of the lab's `bubble.ail`, made because crew_lab is never published. Since then the copy has grown: `bubbleOf`, `lintAgainstShip`, `usedOf`. Two copies of one rule set will drift.
- **The constraint.** The eight resources themselves are Stapledon canon (D-69, stapledons-design `bubble-resources.md` §6). A general-purpose package must not hard-code them.

**The split:**

| What | Where |
|---|---|
| The logic | crew_core (published) |
| The table | scenario data: `scenarios/stapledon/resources.json`, synced into the game the way the scenarios already are (`data/crew/SYNC`, sha256) |
| `shipUnits` (reads the game's ship ledger) | stays in the game |

**Authorization:** Mark, attended 2026-10-15: "yes approved and do the merges". The game side was checked by the integration agent (no objections).
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.8).
**Registry reuse:** contribute (crew_core gains the module the game and the lab both import).

## Milestones

| ID | What | Gate |
|---|---|---|
| ✅ U1 | **`crew_core/units`**. The types are `UnitDef {id, kind, unit, physical, per}` and `Amount {id, value}`. `decodeUnits(Json) -> Result[[UnitDef], string]` checks for unique ids, a kind of stock or capacity, and `per >= 1`. The functions take the table as their first argument: `unitOf`, `allocate`, `lintPack`, `lintAgainstShip` and `usedOf`, with the semantics of the game's current port (whole units rounded down, unknown ids and negative amounts give nothing, the same lint messages). Pure, with contracts and inline tests | `units_test.ail` on both engines. The game's fixture cases (its `crew_events_test` resource tests) are reproduced byte for byte with the Stapledon table. `pkg quality --strict` shows no gates |
| ✅ U2 | **The Stapledon table as data.** `scenarios/stapledon/resources.json` holds the eight rows, taken unchanged from the game's port. The lab's `bubble.ail` becomes a thin reader on crew_core/units, and the pack lint and the crew-sim resource measures use it | every lab claim file is unchanged (same pass counts and same numbers); `crew-sim --check` on the auto claims |
| U3 | **Release 0.5.0** (kind feature): changelog, the README section "Resource units", parity recordings unchanged. Independent evaluation by a different model (score of 70 or more), then PR and publish | CI green; publish |
| U4 | **Hand-off to the integration agent (game side, its sprint):** pin 0.5.0, sync `resources.json` into `data/crew/` with a SYNC line, reduce `sim/crew_resources.ail` to `shipUnits` plus calls into crew_core/units, keep `make crew-parity` | message with the merge sha |

**Then crew_core 0.6, the Archive actor (archive-npc A1).** Planned separately once Mark answers OQ3 and OQ4. Both the captain coupling and integrity decay over time will be switches, so either answer only changes a default:
- an actor kind `archive` with `integrity` and `confidence`, which never takes work or asks for relief;
- trust and regard both ways with each crew member, moved by the archive-crew-trust table: confirmed or contradicted answers, help or failure in a crisis, witnessed confusion, the captain backing it;
- claims on v3.

## Game-side checks (from the integration agent, 2026-10-15)

- **The table.** The eight ids, kinds, units, physical units and `per` values are unchanged. `resources.json` is generated from the game's current table and compared to it byte for byte.
- **Signatures.** In crew_core the functions take the table first, for example `allocate(table, ship)` and `lintPack(table, sc)`. The game keeps its current call sites by wrapping them, `allocate(ship) = units.allocate(stapledon(), ship)`, so no caller changes.
- **Reason strings.** The `blocked:<code>:<detail>` reasons come from the host and are not touched. The lint messages ("<id>: not one of the eight bubble resources", "<id>: must be a <kind>", "<id>: N units but the ship can spare M") are kept verbatim, and U1 tests assert them.

## Questions for Mark (answered 2026-10-15)

1. **The split above:** logic in crew_core, the eight resources as synced data, `shipUnits` in the game. (Recommended: the table is canon, so it belongs with the scenarios, not in a general-purpose package.)
2. **For 0.6** (archive-npc OQ3 and OQ4):
   - Should the captain–Archive coupling ship in the first release, or trust only?
   - Should integrity decay with ship time (the integration agent's proposal), or only from events?
   - **Answers (Mark):** 1, approved. OQ3: trust in the Archive only (coupling switch off by default). OQ4: integrity changes only from events (decay switch off by default).

## Not in scope

- The Archive actor (0.6, above).
- Option (b) and (c) skip-speed work, on hold until ailang#1827 lands (Mark, 2026-10-15).
