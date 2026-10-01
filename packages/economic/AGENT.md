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

For a real agreement, build `{ appSecret, grant }` from two tokens; see
[Connecting to a real agreement](#connecting-to-a-real-agreement).

## Connecting to a real agreement

e-conomic needs two tokens. The **App Secret Token** identifies your app.
The **Agreement Grant Token** is issued when the owner of the books installs
that app. e-conomic's own guide is at
<https://www.e-conomic.com/developer/connect>.

**Before you start:** e-conomic gives API access on the Plus package and
above; Basis is limited. `/self` reports the plan as
`agreementType.subscriptionPlanLevel`.

1. **Create a developer agreement.** It is free: sign up at
   <https://www.e-conomic.com/developer>. You get a separate agreement,
   emailed to you, that exists only to own apps. It is not the agreement
   holding the books.
2. **Create the app.** Log in to the *developer* agreement and open the
   **Apps** tab (top left). Click **New app**, name it, and pick a role.
   - Roles are e-conomic's, not read/write levels. The installing user must
     hold every role the app requires. What each package call needs:

     | Role | Covers | Package calls |
     |---|---|---|
     | **Accounting** | journals, entries, accounts, departments, scanned documents | `accounts`, `accountingYears`, `yearEntries`, `accountEntries` |
     | **Sales** | invoices, orders, quotes, customers, employees, inventory, subscriptions | `invoices`, `invoicesChecked`, `customers` |
     | Project employee | projects and products | none |
     | SuperUser | everything except other users' logins | all, but more than this package needs |

   - Require **Accounting + Sales** rather than SuperUser. No role is
     read-only, so the tokens could write through some other client; this
     package cannot, because its only request is a `GET`.
   - The **App Secret Token** is shown once. Store it straight away; **reset**
     issues a new one.
3. **Get the installation URL.** Click the app's **Tokens** button.
4. **Install the app on the books.** A user of the agreement that holds the
   books logs in to *that* agreement and opens the installation URL.
   Approving it shows the **Agreement Grant Token**. That user must hold
   the roles the app requires.
5. **Store both tokens in 1Password** and refer to them as `op://` references.
   `std/secret` resolves them by shelling `op read`. It needs the
   [1Password CLI](https://developer.1password.com/docs/cli/), either signed
   in or with `OP_SERVICE_ACCOUNT_TOKEN` set:
   - `brew install 1password-cli`;
   - in the 1Password app, turn on **Settings → Developer → Integrate with
     1Password CLI**;
   - check with `op vault list`.

   If `op` is missing or fails, `secret()` errors with `E_SECRET_UNAVAILABLE`.
   There is no fallback to a blank token.
6. **Check the connection** before reading anything else. Call
   `requireAgreement(c, n)` with your agreement number. To find the number
   the first time, call `agreement(c)` or `GET /self`. The rest of the `/self`
   response is worth reading once:

| `/self` field | Tells you |
|---|---|
| `agreementNumber` | Which books the tokens opened. Pin it in your config. |
| `agreementType.subscriptionPlanLevel` | The plan. |
| `application.requiredRoles` | The roles the app requires. |
| `modules` | Enabled modules. "Smart Bank" is the bank feed. Payments show up as entries only once they are reconciled. |

```ailang
import std/io (println)
import std/secret (secret)
import pkg/sunholo/economic/client (Creds, showError)
import pkg/sunholo/economic/api (requireAgreement)

export func main() -> () ! {Net, IO, Secret} {
  let c = { appSecret: secret("op://Vault/e-conomic/app-secret-token", "e-conomic app token"),
            grant: secret("op://Vault/e-conomic/agreement-grant-token", "e-conomic grant") };
  match requireAgreement(c, 1234567) {
    Err(e) => println(showError(e)),
    Ok(a) => println("connected to ${a.companyName}")
  }
}
```

Run with `--caps Net,IO,Secret --net-allow-domains restapi.e-conomic.com`,
with **tracing off**. `std/secret` values are written verbatim to execution
traces (M-TRACE-LABEL-AWARE), so never pass `-emit-trace` and keep
`AILANG_TRACE` unset or `off` when secrets resolve.

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
