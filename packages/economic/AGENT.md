# sunholo/economic

## When to use this package

Use it when an AILANG program needs to **read a Visma e-conomic agreement**:
booked, paid, unpaid or overdue invoices, customers, the chart of accounts,
accounting years, and the entries posted to an account (for example the bank
account, which is where a reconciled payment shows up).

It is **read-only by construction**. The one network call is a literal `GET`,
and no exported function takes a method, a body or a URL. Callers pass a path
relative to a fixed base URL, and paths that could switch host are refused
before any request is sent. Writing to the books is out of scope.

It works with no account at all against e-conomic's public demo agreement:

```ailang
import pkg/sunholo/economic/client (demoCreds, showError)
import pkg/sunholo/economic/api (requireAgreement, invoicesChecked)
import pkg/sunholo/economic/types (Unpaid)
import pkg/sunholo/economic/money (showMinor)

export func main() -> () ! {IO, Net} {
  let c = demoCreds();
  match requireAgreement(c, 1583064) {
    Err(e) => println(showError(e)),
    Ok(_) => match invoicesChecked(c, Unpaid, None, 5) {
      Err(e) => println(showError(e)),
      Ok(r) => {
        println("${show(length(r.items))} unpaid, issues: ${show(r.issues)}");
        println(showMinor(sumMinor(map(\i. i.remainder, r.items))))
      }
    }
  }
}
```

Run with `--caps Net,IO --net-allow-domains restapi.e-conomic.com`.

For a real agreement, build `{ appSecret, grant }` from your developer app's
App Secret Token and the Agreement Grant Token issued when the agreement owner
installs the app. Resolve both with `std/secret`, not from env files. Note
that `std/secret` values are written verbatim to execution traces
(M-TRACE-LABEL-AWARE), so run with tracing off.

## What is proved, and what is only tested

`ailang verify` reports 23 contracts proved across `money`, `filter`, `page`,
`types` and `client`. The ones that matter:

| Module | Proved |
|---|---|
| `money.toBase` | Conversion to base currency is the exact product rounded to the nearest minor unit, **and** the product stays inside int64. |
| `money.roundDiv1e8` | Rounding is half away from zero and within half a unit. |
| `money.paidPart` | Paid + remainder = gross, and each stays between 0 and gross. Credit notes (≤ 0) are included. |
| `money.payState` | `Settled` iff remainder = 0; `Open` iff nothing has been paid on a non-zero invoice; `Partial` exactly in between. |
| `filter.renderPred` | The first `$` in a rendered predicate is the operator's, whatever the value contains, so a field cannot smuggle in an operator. |
| `filter.fieldSafe` | Implies `renderPred`'s precondition. |
| `page.nextSkip` | The walker advances by exactly one page and never requests a page past the last row. |
| `page.pagesNeeded` | Exact ceiling division. |
| `client.pathSafe` | An accepted path cannot carry a scheme, host, query or `..`. |

Each of these was **mutation-tested**: a planted bug in the implementation,
or a widened bound, turns VERIFIED into VIOLATION with a counterexample.

**What is not proved:**
- **The float edge** (`toMinor`, `toRateMicro`). A float parameter puts it
  outside the decidable fragment. It is checked over a table of edge amounts
  in `_smoke.ail`.
- **Value escaping** (`escapeValue`). It uses `std/string.replaceMany`, which
  Z3 cannot encode. It is covered by:
  - a round-trip test over every special character;
  - `wellEscaped`;
  - a live check against the demo: the classic `x$or:currency$eq:DKK`
    injection widens the query when unescaped, and matches nothing through
    this package.
- **Anything recursive or higher-order** (the page walker, decoders). These are
  tested, and the walker's termination rests on the proved `nextSkip` plus a
  page budget.

**Proofs are over unbounded integers; the runtime is int64.** Every
multiplication in `money` is therefore bounded by a `requires`, and the bound
is itself part of what is proved. Amounts are limited to ±10^15 minor units
(±10^10 for currency conversion), and rates to 900 per 100 units. Outside
those limits the checked functions return `Err`; they never wrap.

## Trust checks you get for free

- **`requireAgreement(c, n)`**: refuses unless the tokens opened agreement `n`.
  The demo tokens and a stale grant both return a plausible company.
- **`invoicesChecked`**: every invoice is re-checked against the proved
  arithmetic:
  - net + VAT + rounding = gross;
  - base-currency figures agree with the rate;
  - no overpayment;
  - a three-letter currency code.

  Problems come back as `issues`. Nothing is "fixed".
- **Collections are complete or an error.**
  - Before walking, the page budget is checked against e-conomic's row count.
  - After walking, the number of rows collected must equal that count.
- **Decoders never invent a value.** `std/json.getInt` silently truncates
  `1187.50` to `1187`, so identifiers go through `wholeNumber`, which refuses
  a fraction instead, and money goes through `toMinor`. A bad row fails its
  page and names every bad field.

## Gotchas

- **Entries by account:** use `accountEntries(c, account, year, …)`. The
  year-wide endpoint refuses `account.accountNumber` as a filter field.
- **Dates:** ISO `YYYY-MM-DD` strings are checked on decode, so string
  comparison is safe. Filter date ranges with `dateBetween`.
- **Exchange rates:** e-conomic quotes them per 100 units of foreign
  currency (EUR ≈ 746). They are held ×10^6 as `rateMicro`.
- **Tests:** the float edge lives in `_smoke.ail`, not in `test` blocks.
  On ailang v0.47.0, float operations can fail inside `test` blocks, and
  `property` declarations do not run (both reported upstream).
