# Changelog — sunholo/gmail

All notable changes to this package are documented here. Versions follow
semver; the registry is immutable, so every published version appears exactly
once.

## 0.5.0 — 2026-09-21

**BREAKING**: `Message` and `Alt` gain required `cc` and `bcc` fields. Every
existing record literal `{ to, from, subject, body }` / `{ to, from, subject,
text, html }` fails to compile until `cc: [], bcc: []` is added; with empty
lists the emitted bytes are identical to 0.4.1. `altFrom` gains the two lists
as parameters (`to, cc, bcc, from, subject, text, html`) for the same reason.

### Added

- `cc: [string]` and `bcc: [string]` on `Message` and `Alt` (and therefore on
  `Related`, which wraps `Alt`). Rendered as a single `Cc:` / `Bcc:` header,
  comma-separated, positioned after `To:` and before `From:`. An empty list
  emits no header line at all. Motivated by sunholo-data/daneel#147: mail sent
  to a third-party tenant is copied to the principal as ONE message with a
  `Cc:` — not a second send with its own cap line, Message-ID and no threading.
- `headerSafeAll(addrs: [string]) -> bool` — the list form of the CR/LF guard,
  exported because callers constructing recipient lists programmatically want
  the same check before they build a `Message`.
- The same guard runs at runtime in `safeMessage`, `safeAlt` and `safeRelated`,
  rejecting with `a cc address contains CR or LF — header injection` (and the
  bcc wording). A copy recipient comes from exactly the same untrusted places
  as `to`, so it gets exactly the same door-guard: CR/LF in any address would
  terminate the header block and forge arbitrary headers.

### Notes

- Gmail's API derives recipients from the raw RFC 5322, so `api.ail` is
  unchanged: a `Cc:` header in `raw` is folded into the recipients by Google.
- `buildMessage`, `buildAlt` and `buildRelated` carry the cc/bcc guard in their
  `requires` clauses. As documented on the module, string interpolation makes
  these contracts unverifiable by Z3 today; the runtime check in the `safe*`
  functions is the enforced half.

## 0.4.1 — 2026-09

Non-ASCII subjects sent as RFC 2047 encoded words (`=?UTF-8?B?…?=`) in 11-char
chunks; an all-ASCII subject is untouched. Found when an em dash arrived in
Gmail as "Ã¢Â€Â”". (Pre-changelog release; recorded here for completeness.)

## 0.4.0

multipart/related — inline images referenced as `cid:<id>` from the HTML, two
checked boundaries. (Pre-changelog release; recorded here for completeness.)
