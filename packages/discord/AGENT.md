# sunholo/discord 0.1.0

Use for Discord **bot** REST v10 reads and writes in AILANG. The host application
loads credentials and enforces its channel/write policy. This package has only Net
as an effect; codecs and validators are pure. Never pass a bot token as an MCP tool
argument. Guild membership of a human user does not imply bot channel access.

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
| validId(id), messagePath(...), messageBody(...) | Pure request validation/building |
| responseJson(status, headers, body) | Pure response classification |
| parseMessage(json), parseMessages(array), messageJson(message) | Typed message codecs |
| problem(kind, message), errorJson(error) | Structured errors |

`DiscordMessage` stores IDs as strings, author identity/name, content, timestamp,
reply reference and mentioned user IDs. Empty content can be legitimate (non-text
messages or Message Content Intent restrictions); missing content is a decode error.
Unknown Discord fields are ignored. Attachments, embeds and edits are not modeled
in this first version. Host should construct guild message links from its guild ID.

`DiscordError`: kind, status, code, message, retryAfter (seconds, may be fractional),
global. HTTP bodies and token-bearing headers are not echoed. A 429 is returned to
the caller; there is no sleeping or automatic retry. Network errors on POST mean
unknown outcome. Reconcile before retrying. Discord nonce dedup is time-limited and
is not a durable exactly-once guarantee.

Validate: `ailang check --package .`. Cross-package runtime and upstream protocol
checks live in `ailang-demos/discord/tests/`; run `npm test` in that demo after
`ailang lock` and `npm ci`. No live credentials are used in that suite.
