# Sprint S-CREW-CORE-0.3: crew_core 0.3.0 for Stapledon R2-CREW (CI-0)

**Brief:** ailang-packages#137, written by the R2-CREW integration agent.
**Design:** stapledons-godot `design_docs/planned/r2/crew-integration.md` §CI-0 (approved, D-70; auto-run additions approved in D-72).
**Authorization:** Mark, 2026-10-13: "great continue".
**AILANG prompt version loaded:** v0.16.7 (runtime v0.54.5).
**Registry reuse:** none. This extends crew_core itself.

**Compatibility promise** (to the integration agent):
- The existing commands, journal record shapes and outcome codes are unchanged.
- The new features are additive.
- Archiving is off unless `keep` is set.
- crew_core 0.2.0 recordings (consent, orders, scheduled ship event) replay byte-identically.

| ID | What | Gate |
|---|---|---|
| ✅ K1 | `policy` command (consent/orders mid-session, journalled, from the next request on; config identity unchanged), and the run-time `ship_event` command through the existing flow code | crew_core tests on both engines; 0.2.0 parity fixture |
| ✅ K2 | Profile run growth; archiving (`keep`): fold old finished tasks, resolved reliefs and their evidence and knowledge into per-crew counters; one `archived` record | lab claims unchanged; `crew-sim --turns 500` growing linearly |
| ✅ K3 | Auto-captain in crew_core: `crew_standing_orders/1` and `crew_escalation/1`; `advance(n)` running turns under orders until the first escalation (`escalated` record); fast path when nothing is open | crew_core tests; `crew-sim --auto` with escalation claims per year |
| ⚠️ K4 | Speed: a 10-year interlude (3,650 turns) inside the target, measured in the lab | `crew-sim --auto --turns 3650` timing |
| ✅ K5 | Ergosphere: a third heat user (D-70 OQ6); claims rerun and recorded | `crew-sim --check` 20 seeds |
| ✅ K6 | Close: changelogs, parity check, independent evaluation, PR; merge sha posted on #137 | lab `make validate` keyless |

## Outcome (2026-10-13)

- **K1–K3 and K5 are done.** The six 0.2.0 parity recordings replay
  byte-identically, and crew-sim's output is unchanged under the
  auto-captain.
- **K4 is partial.** Cadence brings a 10-year skip to 1.9 s with yearly
  check-ins. Weekly or monthly check-ins take about 60 s, because each
  decision costs 28–100 ms, much of it VM list-tail copying (ailang#1814).
  The 2 s target for denser check-ins waits on #1814.
- **Compile memory (ailang#1812).** A second call site into the flow group
  cost +14 GB; the workaround routes run-time events through advance. `auto`
  costs about +4 GB cold and stays opt-in.
