# sunholo/deontic

A **verified deontic reasoning engine**: model contract-shaped domains —
obligations with deadlines and prices, notice-and-cure windows, waivers,
suspension, force majeure, attributed delay, amendments, termination
cascades — as a **pure fold over an event list**, with the money paths
**mathematically proved by Z3**.

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
     ✓ VERIFIED capAt           ✓ VERIFIED floorPeriods
     ✓ VERIFIED interestFor     ✓ VERIFIED penaltyFor
     ✓ VERIFIED daysLateAt      ✓ VERIFIED netOf
     ✓ VERIFIED interestPerDiem
     7 functions: 7 verified
   ```
   `interestPerDiem` carries the floor property explicitly —
   `result * 3650000 <= price * bp * daysLate` — so it is proved never to
   over-charge, for every input, not for the cases someone tested.
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
              cureDays: 15, ratePct: 1, ratePeriod: 10,
              ratePerAnnumBp: 0 };   -- 0 = use the period model above
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
- **Payment**: due `delivery day + payWithin`. Two interest models, chosen
  explicitly by the policy:
  - `ratePerAnnumBp > 0` — **per-diem** simple interest at that annual rate
    in basis points (`1035` = 10.35%). This is the shape statutory interest
    actually has: both the Finnish Interest Act and Danish renteloven accrue
    daily from the due date.
  - `ratePerAnnumBp == 0` — the legacy model: `ratePct`% of the effective
    price per FULL `ratePeriod` days late. A step function. It pays nothing
    until a whole period has elapsed, so it always rounds toward the debtor
    by up to one full period. Kept because contracts really are drafted this
    way, and because it is the cross-validated wave-5 model.

  Integer arithmetic throughout, simple and non-compounding in both.
- **Notice** opens a cure window ending `notice day + cureDays` INCLUSIVE.
  Payment breaches cure by paying principal in the window (accrued interest
  still owed); delivery breaches cure by delivering.
- **Waiver**: a waived breach can never ground termination and its
  penalty/interest is EXCLUDED from the owed sums. Report lines always show
  ACCRUED values; waiver affects only `vendor_owes`/`client_owes`. **Waiver
  forgives the consequences of a breach, never the price** — an unpaid
  principal stays owed by a party whose lateness was waived.
- **Force majeure** `[d1, d2]` extends UNDELIVERED delivery deadlines lying
  inside the window (inclusive) by `d2 − d1 + 1`. Payment dues unaffected.
- **Attributed delay** `[d1, d2, cause]` does exactly what force majeure
  does to deadlines, and additionally records the cause in the report. "An
  act of God" and "the customer never sent the inputs it owed" move a
  deadline identically and mean completely different things about who is in
  breach; the engine should not silently conflate them.
- **Suspension**: `Suspend(day, by)` passes the **same validity test as
  termination** — a noticed, uncured, unwaived breach whose window has
  expired. It stops performance and keeps the contract alive; every
  UNDELIVERED deadline is held for the duration and moves on `Resume(day)`.
  A second `Suspend` while one is running changes nothing, as does a
  `Suspend` with no qualifying grounds.
- **Valuation**: money still outstanding accrues interest until somebody
  values it, and a pure fold has no clock — so the valuation date is an
  event, `AsOf(day)`. It defaults to the termination day, and where there is
  neither, the principal is still reported and owed while interest is
  reported as uncomputed rather than as zero.
- **Amendment** replaces an obligation's price as if the contract had
  always said so (amounts already paid stay credited).
- **Termination** is valid only against a noticed, uncured, unwaived breach
  whose window has expired (`day > notice day + cureDays`); grounds are the
  first qualifying notice in arrival order. Invalid attempts change
  nothing. On termination, **undelivered** obligations cancel (no price
  owed, penalty frozen). **Delivered-but-unpaid obligations do not cancel**
  — the price stays owed and interest keeps running to the valuation date.
  Termination stops the future, not the past.
- **Outstanding money is reported.** A delivered, unpaid obligation produces
  an `OUTSTANDING` line and its principal flows into `client_owes`, whether
  or not the contract was terminated. An undelivered obligation past its
  deadline reports `OVERDUE` once there is a valuation date.

## What changed in 0.2.0, and why

0.1.x was extracted from a **supply** contract benchmark and quietly encoded
that shape. Pointing it at professional-services agreements — the ordinary
case of delivering work and invoicing for it — found four things. All four are
fixed here; the first is the reason for the version bump.

**1 · Terminating for non-payment extinguished the debt.** Under 0.1.x, on
termination "delivered-but-unpaid obligations cancel for payment". So a vendor
who delivered, went unpaid, served notice, let the cure window expire and
terminated got this:

```
M1 payment:  CANCELLED
termination: day=87 by=Vendor grounds=M1-payment
client_owes=0
net: settled
```

The money the termination was *grounded on* vanished, and the engine called
the contract settled. Coherent for a forward supply relationship; wrong for
anything where work is earned as it is done. Delivered work is earned —
termination stops the future, not the past. The same run now reports the
principal outstanding, with interest running to the valuation date.

**2 · Outstanding money was invisible even without termination.** A delivered,
unpaid, unterminated obligation produced *no payment line at all* and
contributed nothing to the owed sums. An overdue invoice did not appear in the
report meant to settle it. Principal now flows into `client_owes` whenever
delivery has happened and payment has not, and `AsOf(day)` supplies the
valuation date interest needs.

**3 · Interest was a step function where the law is linear.** The only model
was "`ratePct`% per full `ratePeriod` days", so a payment 29 days late under a
30-day period attracted nothing at all. Statutory interest accrues daily.
`ratePerAnnumBp` adds per-diem accrual; the period model stays for contracts
actually drafted that way and remains the default.

**4 · Delay had no cause.** `ForceMajeure` extends deadlines and is
party-neutral, so a slip caused by the customer failing to supply an input it
owed was indistinguishable from a storm. `AttributedDelay` extends deadlines
identically and records whose delay it was.

**Backward compatibility.** `Policy` gains one field and `State` gains three,
so 0.1.x literals need updating — but the *semantics* are unchanged for every
timeline 0.1.x could express, which is why the wave-5 ground truth below is
still byte-identical. Setting `ratePerAnnumBp: 0` reproduces 0.1.x arithmetic
exactly.

## Ground truth

`wave5_demo.ail` replays the benchmark timeline through this generalized
engine; its 16-line output is byte-identical to the cross-validated
`legal_obligation_engine` expected output in the ailang repo:

```bash
AILANG_RELAX_MODULES=1 ailang run --caps IO wave5_demo.ail
```

`engine_test.ail` carries the same assertions as inline tests, plus eleven
more pinning the 0.2.0 semantics — that earned money survives termination,
that an overdue invoice is visible, that waiver forgives interest and not
principal, that suspension needs the grounds termination needs, and that
per-diem and period interest differ where they should.

```bash
AILANG_RELAX_MODULES=1 ailang test .     # 22 passed, 0 failed
```

*(Corrected in 0.2.0: this README used to say `ailang test` skipped tests in
modules with package-relative imports. That was true when it was written and
is no longer — the runner executes them. The seven `⊘` are property-based
contract tests whose generators discard, not skipped modules.)*

`_smoke.ail` is the publish gate and now asserts **both** the wave-5 ground
truth and the termination regression, because reintroducing defect 1 above is
a one-line change to the cascade.

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

## Real-world example: professional services

`services_demo.ail` is the other contract shape, and it is the one that found
everything in 0.2.0: no delivery penalty, statutory per-diem interest, a right
to suspend for non-payment, a customer-caused delay, and fees that must
survive termination.

```
delay: [0..20] +21d to undelivered deadlines — cause: Customer: required inputs not supplied
M1 payment: PAID day=110 late=52 interest=8975
M2 payment: OUTSTANDING as_of=110 due=88 late=22 principal=630000 interest=3797
M3 delivery: OVERDUE as_of=110 late=3 penalty=0
suspension: from=87 to=110 by=Vendor grounds=M1-payment
net: Client pays Vendor 642772
```

and the same engagement terminated instead of suspended:

```
M1 payment: OUTSTANDING (survives termination) as_of=120 due=58 late=62 principal=630000 interest=10701
M2 payment: OUTSTANDING (survives termination) as_of=120 due=88 late=32 principal=630000 interest=5523
M3 delivery: CANCELLED late_days=2 penalty=0
termination: day=87 by=Vendor grounds=M1-payment
net: Client pays Vendor 1276224
```

Under 0.1.x that second report read `net: settled`.

## Integrating: API service vs WASM — both spiked, with numbers (2026-07-09)

`api.ail` provides the boundary both paths share:
- `analyzeContract(obligations, events, policy) -> [string]` — structured
  records (serve-api decodes JSON into these natively)
- `analyzeContractJson(obligationsJson, eventsJson, policyJson) -> [string]`
  — one opaque JSON-string wire format (required for WASM, whose host bridge
  currently converts only scalar arguments; also handy for any client)

**API path — measured.** Zero custom code:
```bash
cd packages/deontic && ailang serve-api --port 8080 .
curl -X POST localhost:8080/api/api/analyzeContract -d '{...}'  # 20ms, HTTP 200
```
Full PPA settlement report in ~20ms server-side / ~23ms round-trip local.
This is the docparse deployment shape: containerize + Cloud Run.

**WASM path — measured (Node, fresh dev-build runtime).**
| Metric | Value |
|---|---|
| runtime artifact | 41.1 MB uncompressed (host with brotli + cache-forever) |
| instantiate + boot | ~1.2 s (one-time) |
| load bundled package | ~350 ms (one-time; 421-line single-module bundle) |
| analyzeContractJson | 13 ms first call |
| what-if recompute | **8.9 ms each** (50 consecutive, byte-identical output) |

The report is byte-identical to the API/CLI output. Caveats before
production: bundle the package into a single module (relative imports are
stripped by a build step — the wasm loader takes one module source); pin the
runtime build to the bundle (version drift is the known trap); this spike ran
under Node — do a browser pass before shipping; and the runtime bridge's
scalar-only argument conversion is why the JSON-string surface exists
(upstream enhancement opportunity: array/object conversion in cmd/wasm).

**Recommended for contract platforms (e.g. PPA analysis):** hybrid.
AI extraction of events/terms from contract prose runs server-side (keys +
`std/ai` capabilities), returning the typed event JSON; the reasoning fold
runs client-side in WASM for ~9 ms interactive what-if with contracts never
leaving the browser. Falling back to API-only is a deployment change, not a
redesign — both paths call the same `api.ail` boundary.

## Extension points

- **Custom policies**: `Policy` is plain data — per-contract knobs.
- **New event kinds**: extend the `Event` ADT and `applyEvent`; the
  exhaustiveness pressure of `match` tells you every place to update.
- **Beyond vendor/client**: the two-party delivery/payment role split is
  still fixed; multi-party generalization is the natural 0.3.0 if a real
  consumer needs it.
- **Fees and costs**: collection fees, reminder charges and statutory
  compensation are not modelled. Reconciling against a real statement of
  account means adding them, and they are jurisdiction-specific enough that
  they probably belong in a consumer rather than here.

## Known limitations

- Two parties, two obligation kinds (delivery, payment) per obligation id.
- No fees, costs or statutory compensation — see Extension points.
- Interest is simple and non-compounding in both models. Where a contract or
  a statute compounds, this under-states.
- `AsOf` is a single global valuation date, not per-obligation. A statement
  of account that values different lines at different dates needs one run per
  date.
- A suspension whose `Resume` never arrives holds deadlines open forever;
  the report shows `to=open` and says so, but nothing forces a resolution.
- Engine code hoists local calls out of record-update fields to dodge
  ailang issue #327 (`undefined variable` mis-resolution) — cosmetic only.
