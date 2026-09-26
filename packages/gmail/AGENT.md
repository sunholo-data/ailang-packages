# sunholo/gmail

## When to use this package

Use when an AILANG program needs to **compose and send email as a Google
account** — an agent that reports, escalates, or corresponds. It builds a valid
RFC 5322 message with header-injection guards, encodes it the way Gmail's API
demands, and creates a draft or sends it.

Pair it with `sunholo/oauth`, which gets the bearer token this package needs.
This package deliberately does not do auth.

Not for *reading* mail. `gmail.compose` cannot read a mailbox at all — a
`labelIds=SENT` listing returns 403 — which is a feature, not a gap: an agent
that only writes is a much smaller thing to reason about. Read mail from a
maildir instead.

## Quick start

```ailang
import pkg/sunholo/oauth/token (readCreds, exchangeRefresh)
import pkg/sunholo/gmail/message (Message)
import pkg/sunholo/gmail/api (createDraft, sendMessage)

let m = { to: "someone@example.com",
          cc: [],                       -- copy lines: ["principal@example.com"]
          bcc: [],
          from: "R. Daneel Automation <bot@example.com>",
          subject: "Nightly report",
          body: "..." };

match readCreds("~/.config/agent/gmail-token.json") {
  Ok(creds) => match exchangeRefresh("https://oauth2.googleapis.com/token", creds) {
    Ok(token) => createDraft(token, m),      -- or sendMessage(token, m)
    Err(e) => Err(e)
  },
  Err(e) => Err(e)
}
```

Requires **AILANG >= 0.35.4** for `std/bytes.toBase64URL`. Gmail's `raw` field is
base64url and rejects standard base64; the two alphabets differ in exactly two
characters, and the API's error never mentions encoding.

## The security-critical part

**A header block is terminated by a blank line.** A recipient or subject
containing CR or LF does not look odd — it *ends the headers* and begins a new
section, letting a caller forge `Bcc`, rewrite `From`, or append a body of their
choosing. If any part of `to` or `subject` comes from a document, an inbound
email, or a model, that is a live injection path.

So the pure half is separated from the network half deliberately: the part where
a mistake is a security bug has no effects, needs no credential, and is testable
offline. `_smoke.ail` exercises both attacks.

**Use `safeMessage` / `safeRaw`, not `buildMessage`.** They return a `Result` and
refuse, naming which field was at fault.

### An honest note about the contract

`buildMessage` carries `requires` clauses stating the injection property.
**`ailang verify` currently SKIPS them.** String interpolation desugars to `show`,
which Z3 cannot encode, so *any* function that builds a string is unverifiable
(reported as `fb_913ee851c83c0d8c`). Since `++` is list-only, interpolation is
how strings get built — this is not avoidable by writing it differently.

The contract therefore documents intent and does not yet prove it. That is why
`safeMessage` performs the same check at **runtime**: shipping the contract alone
would claim a guarantee the toolchain has not delivered. When the solver can
encode interpolation, the contract becomes the proof and the runtime check
becomes belt-and-braces.

## Drafts and sends — the scope cannot separate them

Google has **no draft-only scope**. `gmail.compose` covers creating drafts *and*
sending. So "this agent only drafts" is a property of the **caller**, never of
the grant, and a package offering only `createDraft` would imply a safety it
cannot provide. Both are offered plainly.

**Sending is the only irreversible thing here.** A caller sending unattended
wants a per-run cap, a recipient allowlist and a self-reply guard. Those are not
in this package on purpose: a limit each caller re-implements is a limit nobody
enforces. Put them in one place at the boundary you control — for the reference
consumer that is the `daneel` CLI, which owns the limits and the run log.

## Exports

| Function | Module | Signature |
|---|---|---|
| `headerSafe` | message | `(string) -> bool` |
| `headerSafeAll` | message | `([string]) -> bool` — list form, for cc/bcc |
| `buildMessage` | message | `(Message) -> string` — contract-bearing, unguarded |
| `safeMessage` | message | `(Message) -> Result[string, string]` — **prefer this** |
| `encodeRaw` | message | `(string) -> string` — base64url |
| `safeRaw` | message | `(Message) -> Result[string, string]` — compose + encode |
| `createDraft` | api | `(string, Message) -> Result[string, string] ! {Net}` |
| `sendMessage` | api | `(string, Message) -> Result[string, string] ! {Net}` |

`Message` is `{ to, cc, bcc, from, subject, body }`; `Alt` is the same shape
with `text`/`html` in place of `body`. `cc`/`bcc` (0.5.0) are lists of
addresses rendered as one comma-separated `Cc:`/`Bcc:` header and omitted when
empty; every address gets the same CR/LF guard as `to` — a copy recipient
comes from exactly the same untrusted places, and CR/LF in any of them would
terminate the header block. Gmail derives recipients from the raw message, so
a `Cc:` header is folded into the recipients by Google — no API change.
`body` is unconstrained — newlines there are ordinary and cannot escape
upward, because the body is everything after the blank line.

## Sharp edges

1. **`send` is a reserved keyword** and cannot be a module path segment. That is
   why the effectful module is `api`. The parse error says so, but only in the
   *first* error — the cascade after it is noise.
2. **`httpRequest` is `(METHOD, URL, headers, body)`.** Both leading parameters
   are `string`, so swapping them type-checks and fails at runtime as
   `InvalidMethod` in ~1ms, reading exactly like a dead network.
3. **`NetError` carries variants the docs do not list.** An exhaustive match over
   the documented four panics with "no pattern matched". Use `show`.
4. **`gmail.compose` cannot read.** If you need the message back, you need a
   different scope or a maildir.
5. **Gmail does not apply the account's UI signature to API sends.** Whatever you
   want in the footer must be in `body`.

## Effects

`Net` only, at `@limit=1` per call. `IO` appears in the manifest ceiling for
`_smoke.ail` alone; no library function prints.
