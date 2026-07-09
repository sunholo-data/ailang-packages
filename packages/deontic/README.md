# sunholo/deontic

A **verified deontic reasoning engine**: model contract-shaped domains —
obligations with deadlines and prices, notice-and-cure windows, waivers,
force majeure, amendments, termination cascades — as a **pure fold over an
event list**, with the money paths **mathematically proved by Z3**.

Extracted and generalized from the AILANG frontier-benchmark campaign
(wave 5, `legal_obligation_engine`), whose output is cross-validated
byte-for-byte against an independent Python implementation.

## Why this exists (the four moats)

1. **Illegal states are unrepresentable.** Events, termination outcomes and
   breach resolutions are closed ADTs. A missed case is a loud error at
   compile/match time — not a silently wrong settlement.
2. **The settlement math is proved, not tested.** Every function in
   `settle.ail` carries `requires`/`ensures` clauses and is verified by Z3
   for ALL inputs:
   ```
   $ ailang verify --relax-modules settle.ail
     Solver: Z3 version 4.15.4 - 64 bit
     ✓ VERIFIED capAt          ✓ VERIFIED floorPeriods
     ✓ VERIFIED interestFor    ✓ VERIFIED penaltyFor
     ✓ VERIFIED daysLateAt     ✓ VERIFIED netOf
     6 functions: 6 verified
   ```
3. **Replayable by construction.** `runEvents` is pure: same contract +
   same events = same outcome, every time, auditable line by line.
4. **Least authority.** The package exports only `pure` functions and its
   manifest ceiling is `IO`-only (used by the demo gate). Shrink
   `[effects].max` to `[]` and even the demo's `println` is rejected at the
   manifest level — the engine cannot quietly acquire effects.

## Quick start

```bash
ailang add --git https://github.com/sunholo-data/ailang-packages --subdir packages/deontic --tag main
ailang lock
```

```ailang
import pkg/sunholo/deontic/types (Event, Deliver, Pay, Notice, Terminate, Policy, initState)
import pkg/sunholo/deontic/engine (runEvents, report)

export func main() -> () ! {IO} {
  let pol = { penPerDay: 200, penCap: 4000, payWithin: 10,
              cureDays: 15, ratePct: 1, ratePeriod: 10 };
  let st = runEvents(pol,
    initState([("M1", 10, 10000)]),
    [Deliver(12, "M1"), Pay(30, "M1")]);
  printAll(report(pol, st, ["M1"]))
}
```

## Semantics (pinned)

- **Delivery penalty**: `penPerDay` per day late, capped at `penCap`;
  accrues to the delivery day, or to `termination day − 1` for obligations
  cancelled by termination.
- **Payment**: due `delivery day + payWithin`; interest is `ratePct`% of
  the effective price per FULL `ratePeriod` days late — floor division,
  simple, non-compounding, integer arithmetic throughout.
- **Notice** opens a cure window ending `notice day + cureDays` INCLUSIVE.
  Payment breaches cure by paying principal in the window (accrued interest
  still owed); delivery breaches cure by delivering.
- **Waiver**: a waived breach can never ground termination and its
  penalty/interest is EXCLUDED from the owed sums. Report lines always show
  ACCRUED values; waiver affects only `vendor_owes`/`client_owes`.
- **Force majeure** `[d1, d2]` extends UNDELIVERED delivery deadlines lying
  inside the window (inclusive) by `d2 − d1 + 1`. Payment dues unaffected.
- **Amendment** replaces an obligation's price as if the contract had
  always said so (amounts already paid stay credited).
- **Termination** is valid only against a noticed, uncured, unwaived breach
  whose window has expired (`day > notice day + cureDays`); grounds are the
  first qualifying notice in arrival order. Invalid attempts change
  nothing. On termination, undelivered obligations cancel (no price owed,
  penalty frozen); delivered-but-unpaid obligations cancel for payment.

## Ground truth

`wave5_demo.ail` replays the benchmark timeline through this generalized
engine; its 16-line output is byte-identical to the cross-validated
`legal_obligation_engine` expected output in the ailang repo:

```bash
AILANG_RELAX_MODULES=1 ailang run --caps IO wave5_demo.ail
```

`engine_test.ail` carries the same assertions as inline tests. NOTE: the
current `ailang test` runner skips tests in modules with package-relative
imports (pre-existing; other packages' tests skip identically), so the demo
diff is the enforced gate for now.

## Real-world example: Power Purchase Agreements

`ppa_demo.ail` models a solar PPA — COD milestone with capacity payment,
quarterly contracted-energy deliveries, curtailment as force majeure,
indexation as amendment, termination for prolonged default — with NO engine
changes, just data:

```
Q1 effective: deadline=275 price=120000     <- curtailment window extended it
Q2 effective: deadline=350 price=126000     <- indexation amendment
Q2 delivery: CANCELLED late_days=49 penalty=24500
termination: day=400 by=Buyer grounds=Q2-delivery
net: Vendor pays Client 24500
```

## Integrating: API service vs WASM

The engine's purity changes the usual calculus:

- **WASM (client-side analysis).** The documented AILANG WASM pain points are
  effect-handler bridges and version drift — a pure fold needs NO effect
  bridges, so this package is an unusually good WASM citizen: ship the AILANG
  wasm runtime + these modules, feed events from your app, render the report.
  Wins: contracts never leave the browser (PPA confidentiality), and what-if
  analysis (drag a deadline / toggle a waiver, re-run the fold) is
  interactive at zero marginal cost. Validate with a spike before committing
  (version drift between the wasm runtime and .ail sources is the known trap).
- **API service (docparse pattern).** Proven ops path, and REQUIRED anyway
  for the step WASM can't do: AI extraction of events/terms from contract
  prose (`std/ai` with explicit capabilities, server-side keys).
- **Recommended hybrid:** extraction server-side (prose -> typed events via a
  small API), reasoning client-side (WASM what-if on the extracted events).
  If the WASM spike bites, run BOTH server-side behind the docparse-style
  API first — the module boundary between extraction and reasoning is the
  same either way, so the split is a deployment decision, not a design one.

## Extension points

- **Custom policies**: `Policy` is plain data — per-contract knobs.
- **New event kinds**: extend the `Event` ADT and `applyEvent`; the
  exhaustiveness pressure of `match` tells you every place to update.
- **Beyond vendor/client**: v0.1.0 fixes the two-party delivery/payment
  role split; multi-party generalization is the natural 0.2.0 if a real
  consumer (e.g. Aitana workflows) needs it.

## Known limitations

- Two parties, two obligation kinds (delivery, payment) per obligation id.
- `ailang test` package-mode skipping (see Ground truth).
- Engine code hoists local calls out of record-update fields to dodge
  ailang issue #327 (`undefined variable` mis-resolution) — cosmetic only.
