# AGENT.md — sunholo/deontic

## When to use

Use this package when modeling **contract-shaped state machines**:
obligations with deadlines and money attached, breach/notice/cure flows,
waivers, suspension for non-payment, force-majeure and attributed-delay
windows, amendments, termination. Typical fits: legal/commercial contract
reasoning, SLA tracking, milestone billing, procurement workflows,
professional-services engagements.

Do NOT use it for: general workflow engines (no money/deadline semantics
needed), or anything requiring wall-clock time — days are abstract integers
supplied by the caller (this keeps the engine pure and replayable).

## Quick start

```ailang
import pkg/sunholo/deontic/types (Event, Deliver, Pay, Notice, Waive, Terminate,
                                  ForceMajeure, AmendPrice, Suspend, Resume, AsOf,
                                  AttributedDelay, Policy, State, initState)
import pkg/sunholo/deontic/engine (runEvents, report, applyEvent, isCured)

-- period interest (legacy, and the wave-5 model)
let pol = { penPerDay: 200, penCap: 4000, payWithin: 10,
            cureDays: 15, ratePct: 1, ratePeriod: 10, ratePerAnnumBp: 0 };

-- statutory per-diem interest, 10.35% p.a. — ratePct/ratePeriod unused
let svc = { penPerDay: 0, penCap: 0, payWithin: 14,
            cureDays: 14, ratePct: 0, ratePeriod: 0, ratePerAnnumBp: 1035 };

let st = runEvents(pol, initState([("M1", 10, 10000)]), events);
let lines = report(pol, st, ["M1"])   -- [string], print under YOUR caps
```

**Pick the contract shape first.** `ppa_demo.ail` is a supply contract: delay
damages, termination cancels what was never delivered. `services_demo.ail` is
a professional-services engagement: no delivery penalty, statutory per-diem
interest, suspension rather than damages, and fees that survive termination.
Copying the wrong one is the commonest way to get a wrong answer.

## Exported surface

| Module | Export | Signature | Notes |
|---|---|---|---|
| types | `Event` | ADT: `Deliver(day, id)`, `Pay(day, id)`, `AmendPrice(day, id, price)`, `ForceMajeure(day, d1, d2)`, `Notice(day, breachId)`, `Waive(day, breachId)`, `Terminate(day, by)`, `Suspend(day, by)`, `Resume(day)`, `AsOf(day)`, `AttributedDelay(day, d1, d2, cause)` | breach ids: `"<id>-delivery"` / `"<id>-payment"` |
| types | `Term` | `NoTerm \| TermAt(day, by, grounds)` | |
| types | `SuspWindow` | `SuspW({from, to, by, grounds})` | `to == -1` while running |
| types | `Attribution` | `Attr({from, to, span, cause})` | |
| types | `Policy`, `State` | record aliases | plain data |
| types | `initState` | `([(id, deadline, price)]) -> State` | |
| types | `aGet`/`aSet`/`hasStr` | assoc-list helpers | |
| engine | `runEvents` | `(Policy, State, [Event]) -> State` | pure fold; events must be in day order |
| engine | `applyEvent` | `(Policy, State, Event) -> State` | single step |
| engine | `isCured` | `(Policy, State, breachId, noticeDay) -> bool` | |
| engine | `report` | `(Policy, State, [id]) -> [string]` | full settlement report |
| engine | `interestDue` | `(Policy, price, daysLate) -> int` | picks the policy's interest model |
| engine | `openSuspFrom` | `([SuspWindow]) -> int` | day an open suspension began, else -1 |
| settle | `capAt`, `floorPeriods`, `interestFor`, `interestPerDiem`, `penaltyFor`, `daysLateAt`, `netOf` | Z3-VERIFIED arithmetic | run `ailang verify` yourself |

## Rules the engine pins (read before extending)

See README "Semantics (pinned)". The ones that trip people:
1. Report lines show ACCRUED penalty/interest; waiver only removes amounts
   from the owed sums — and waiver NEVER forgives principal.
2. Cure windows are INCLUSIVE (`<= notice day + cureDays`); termination and
   suspension both require strict expiry (`day > notice day + cureDays`).
3. **Termination does not cancel delivered-but-unpaid obligations.** The
   price stays owed and interest keeps running. (Changed in 0.2.0; 0.1.x
   cancelled them and reported such contracts as settled.)
4. Interest on money still OUTSTANDING needs `AsOf(day)`. Without one the
   principal is still owed but interest reads `not computed (no AsOf)`
   rather than `0` — do not read the absence of a number as zero.
5. `Suspend` and `Terminate` share a validity test but not an outcome:
   suspension is reversible and holds undelivered deadlines, termination
   cancels them.

## Gotchas for agents

- All package exports are `pure`. Printing is the CONSUMER's job under its
  own capabilities.
- Do not put local function calls inside record-update fields
  (`{ s | f: localFn(...) }`) in this package — hoist to a `let` first
  (ailang #327 workaround, already applied throughout).
- Imports go immediately after the module declaration (ailang #325).
- `ailang test .` runs the package tests (22 pass). An older note here said
  it skipped package-relative modules; that is no longer true. `_smoke.ail`
  remains the publish gate and asserts both the wave-5 ground truth and the
  termination regression.
