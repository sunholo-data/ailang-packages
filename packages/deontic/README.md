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
- **Beyond vendor/client**: v0.1.0 fixes the two-party delivery/payment
  role split; multi-party generalization is the natural 0.2.0 if a real
  consumer (e.g. Aitana workflows) needs it.

## Known limitations

- Two parties, two obligation kinds (delivery, payment) per obligation id.
- `ailang test` package-mode skipping (see Ground truth).
- Engine code hoists local calls out of record-update fields to dodge
  ailang issue #327 (`undefined variable` mis-resolution) — cosmetic only.
