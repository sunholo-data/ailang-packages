# AGENT.md — sunholo/deontic

## When to use

Use this package when modeling **contract-shaped state machines**:
obligations with deadlines and money attached, breach/notice/cure flows,
waivers, force-majeure windows, amendments, termination. Typical fits:
legal/commercial contract reasoning, SLA tracking, milestone billing,
procurement workflows.

Do NOT use it for: general workflow engines (no money/deadline semantics
needed), or anything requiring wall-clock time — days are abstract integers
supplied by the caller (this keeps the engine pure and replayable).

## Quick start

```ailang
import pkg/sunholo/deontic/types (Event, Deliver, Pay, Notice, Waive, Terminate,
                                  ForceMajeure, AmendPrice, Policy, State, initState)
import pkg/sunholo/deontic/engine (runEvents, report, applyEvent, isCured)

let pol = { penPerDay: 200, penCap: 4000, payWithin: 10,
            cureDays: 15, ratePct: 1, ratePeriod: 10 };
let st = runEvents(pol, initState([("M1", 10, 10000)]), events);
let lines = report(pol, st, ["M1"])   -- [string], print under YOUR caps
```

## Exported surface

| Module | Export | Signature | Notes |
|---|---|---|---|
| types | `Event` | ADT: `Deliver(day, id)`, `Pay(day, id)`, `AmendPrice(day, id, price)`, `ForceMajeure(day, d1, d2)`, `Notice(day, breachId)`, `Waive(day, breachId)`, `Terminate(day, by)` | breach ids: `"<id>-delivery"` / `"<id>-payment"` |
| types | `Term` | `NoTerm \| TermAt(day, by, grounds)` | |
| types | `Policy`, `State` | record aliases | plain data |
| types | `initState` | `([(id, deadline, price)]) -> State` | |
| types | `aGet`/`aSet`/`hasStr` | assoc-list helpers | |
| engine | `runEvents` | `(Policy, State, [Event]) -> State` | pure fold; events must be in day order |
| engine | `applyEvent` | `(Policy, State, Event) -> State` | single step |
| engine | `isCured` | `(Policy, State, breachId, noticeDay) -> bool` | |
| engine | `report` | `(Policy, State, [id]) -> [string]` | full settlement report |
| settle | `capAt`, `floorPeriods`, `interestFor`, `penaltyFor`, `daysLateAt`, `netOf` | Z3-VERIFIED arithmetic | run `ailang verify` yourself |

## Rules the engine pins (read before extending)

See README "Semantics (pinned)". The two that trip people:
1. Report lines show ACCRUED penalty/interest; waiver only removes amounts
   from the owed sums.
2. Cure windows are INCLUSIVE (`<= notice day + cureDays`); termination
   requires strict expiry (`day > notice day + cureDays`).

## Gotchas for agents

- All package exports are `pure`. Printing is the CONSUMER's job under its
  own capabilities.
- Do not put local function calls inside record-update fields
  (`{ s | f: localFn(...) }`) in this package — hoist to a `let` first
  (ailang #327 workaround, already applied throughout).
- Imports go immediately after the module declaration (ailang #325).
- `ailang test` currently SKIPS package-relative test modules; verify via
  `wave5_demo.ail` diff instead (see README Ground truth).
