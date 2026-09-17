# sunholo/discord

Use for Discord **bot** REST v10 reads and writes in AILANG. The host application
loads credentials and enforces its channel/write policy. The library surface has
only Net as an effect; codecs and validators are pure. The package ceiling also
declares IO solely for the offline `_smoke.ail` boot gate (`ailang run -caps IO
--entry main _smoke.ail`); no library module uses IO. Never pass a bot token as an MCP tool
argument. Guild membership of a human user does not imply bot channel access.

Install: `ailang install sunholo/discord@0.2.0`, then
`import pkg/sunholo/discord/client (...)`. Consumer programs need `--caps Net`
for the effectful entry points; the pure codecs run with no capabilities. Full
quickstart, pagination pattern and error-kind table: package README.md and
`ailang pkg-docs sunholo/discord` (this file).

```ailang
import pkg/sunholo/discord/client (readMessages, messageJson)
import std/result (Ok, Err)

-- Caller supplies token from Env or a protected file.
-- readMessages(token, channelId, {limit: 50, before: "", after: ""})
```

Exports in `sunholo/discord/client`:

| Function | Purpose |
|---|---|
| identity(token) | Bot identity via /users/@me |
| channels(token, guildId) | Guild channel metadata; permissions must still be checked by reading |
| readMessages(token, channelId, query) | One page, limit 1..100, exclusive before/after cursors |
| readMessage(token, channelId, messageId) | One message, useful for read-back |
| sendMessage(token, channelId, text, replyTo, nonce) | Text or reply; mentions disabled; optional nonce dedup |
| editMessage(token, channelId, messageId, text) | PATCH content on an existing message; reply reference untouched |
| typing(token, channelId) | Typing indicator (~10s); 204 No Content handled, any 2xx is success |
| startThread(token, channelId, messageId, name) | Start a thread from a message; returns the thread channel |
| activeThreads(token, channelId) | Active threads of a channel (response {threads, members} → thread channels) |
| classifyError(status, headers, body) | Shared non-2xx classification (responseJson and unit requests) |
| validId(id), messagePath(...), messageBody(...) | Pure request validation/building |
| responseJson(status, headers, body) | Pure response classification |
| parseMessage(json), parseMessages(array), parseChannel(json), parseChannels(array), messageJson(message) | Typed message and channel codecs |
| problem(kind, message), errorJson(error) | Structured errors |

`DiscordMessage` stores IDs as strings, author identity/name, content, timestamp,
reply reference and mentioned user IDs. Empty content can be legitimate (non-text
messages or Message Content Intent restrictions); missing content is a decode error.
Unknown Discord fields are ignored. Attachments, embeds and edits are not modeled
in this first version. Host should construct guild message links from its guild ID.

Threads are channels: pass a thread ID to readMessages/sendMessage and it works
unchanged. `startThread` creates one from an existing message; thread names are
1..100 characters. `activeThreads` unwraps the `{threads, members}` response to
just the thread channels.

`DiscordError`: kind, status, code, message, retryAfter (seconds, may be fractional),
global. HTTP bodies and token-bearing headers are not echoed. A 429 is returned to
the caller; there is no sleeping or automatic retry. Network errors on POST mean
unknown outcome. Reconcile before retrying. Discord nonce dedup is time-limited and
is not a durable exactly-once guarantee.

Validation (2026-09-15, AILANG dev + `pkg quality` on `build/package-authoring-followups`):

- `ailang check --package .`: clean.
- `ailang test --package .`: 22 native tests, 22 passed, 0 failed, 0 skipped. Offline
  only; no network, no credentials.
- `ailang test client.ail --allow-skips`: 18 contract-derived property cases pass with
  100 generated cases each. 4 skips, all structural: 3 × no generator for the imported
  `std/json` `Json` type (parseChannels/parseMessage/parseMessages ensures), 1 ×
  out-of-contract `requires { i >= 0 }` on `digits` (random negative samples are
  correctly discarded). 0 failures.
- `ailang verify client.ail`: 1 proved (`problem`), 12 skipped — Z3 has no encoding for
  `trim`/`charAt`/`toLower`/`stringToFloat`, string interpolation (`show`), or callees
  returning `Option`/`Result`. 0 counterexamples, 0 unknown. Contracts are also
  executed as runtime properties (above), which is the primary behavioral evidence.
- `ailang pkg quality --strict .`: 0 declaration gaps (22 native tests, 22 contract
  clauses, `@limit=1` on all six `Net` functions, each performing exactly one request).
- Explicit `properties [...]` (forall) blocks are not used: the forall lowering is
  broken upstream (core #624). Runtime property evidence comes from `ensures` clauses.

Cross-package runtime and upstream protocol checks live in `ailang-demos/discord/tests/`;
run `npm test` in that demo after `ailang lock` and `npm ci`. No live credentials are
used in that suite.
