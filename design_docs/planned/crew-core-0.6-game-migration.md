# crew_core 0.6.0: migration notes for the game (S7 hand-off)

**For:** the stapledons-godot integration agent (R2-INTERLUDE follow-up).
**From:** sprint S-CREW-CORE-0.6 (design `crew-core-0.6-stand-down.md` §6).
**Package:** `sunholo/crew_core` 0.6.0, release kind `feature`.
**Merge sha:** pending. PR #150 is not merged and 0.6.0 is not published yet.
Fill this in at the hand-off.

Nothing in the game changes until it pins 0.6.0. These are the game-side
changes, in order.

1. **Pin.** Set `sunholo/crew_core = "0.6.0"` in `sim/ailang.toml`, then run
   `ailang install` and `ailang lock` (lockfile `generated_at` churns; ignore
   it when diffing).
2. **Digest (`sim/cruise_digest.ail`).**
   - Count Acts `stand_down_asked` (detail `sd-<id>`) and
     `stand_down_decision` (label `granted` or `denied`) into new
     `crew.counts` fields `standDownsAsked`, `standDownsGranted`,
     `standDownsDenied` (a protocol minor bump).
   - `momentKind("stand_down") = "relief"`.
   - `emotionOf("stand_down", _) = "sad"`, as `request_relief`.
   - The Aboard sentence may add stand-downs to relief ("one asked to step
     back"). That choice is the game's.
3. **Template lines (`sim/protocol_crew.ail` `templateLine`).** Add
   `stand_down` (for example "I need to stand down for a while.") and
   `carry_on` (for example "I can keep going."). No digits (D-21).
4. **`ui/crew_page.gd`.** Add `stand_down` to `STRAINED_LABELS` if the
   fallback list still lives there.
5. **Orders literals.** `Orders` gains `standDown: string` (`"on"` by
   default in `consentOrders()` and `ordersOrders()`). Any full `Orders`
   record literal needs the field; `{ base | ... }` updates absorb it. The
   standing-orders JSON accepts an optional `"stand_down": "on" | "off"`.
6. **Re-record fixtures at a cadence of 2 or more**: `make crew-parity`, the
   `crew_hold_test` expectations at cadence 30, and the digest fixtures.
   Daily-cadence fixtures do not change (OQ1: duty check-ins only at a
   cadence of 2 or more).
7. **AI replies (D-7, `crew_reply`).** A duty request's legal labels are
   `carry_on`, `stand_down` and `defer`; the reply screen must accept them.
8. **Waiting page.** Under auto-run a stand-down is decided in the same call,
   so it never waits. Under `hands_on` the synced `hands_on.json` now
   carries `{"kind":"stand_down"}` (OQ3): advanceAuto stops with escalation
   `stand_down` (actor the crew member, task `sd-<id>`, detail `<id>`) before
   deciding. The hold card shows it like a relief hold, and the player's
   answer is `{"command":"resolve_stand_down","id":<detail>,"release":true|false}`
   in the same tick. `critical_only` (`escalation.json`) has no such rule and
   decides by the standing order.
9. **Unchanged:** `AutoState`, `Act`, `Escalated`, the escalation schema, the
   appraisal policy id `received-outcome-v1`, and every existing command,
   record and outcome code.

**What to expect** (crew lab, last-messages-home, a 10-year monthly skip,
seeds 1–2): 28 and 29 stand-downs under consent, all granted; 17 and 14 under
orders, all denied; 0 errors.
