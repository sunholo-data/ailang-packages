# sunholo/discord

Discord **bot** REST v10 client for AILANG: typed messages, safe request
construction, pagination, rate-limit classification and structured errors.
Pure codecs and validators; a thin effectful Net surface.

## Install

```sh
ailang install sunholo/discord@0.2.0
```

```ailang
import pkg/sunholo/discord/client (readMessages, sendMessage, parseMessage, messageJson)
```

## Effects and capabilities

| Surface | Effects | Notes |
|---|---|---|
| `identity`, `channels`, `readMessages`, `readMessage`, `sendMessage`, `editMessage`, `typing`, `startThread`, `activeThreads` | `Net` (`@limit=1` each: exactly one HTTP request per call) | run with `--caps Net`; the caller supplies the token |
| codecs and validators (`validId`, `messagePath`, `messageBody`, `responseJson`, `parse*`, `messageJson`, `problem`, `errorJson`) | pure | runnable offline, no capabilities |

The package ceiling is `[Net, IO]`; IO exists solely for the offline `_smoke.ail`
boot gate — no library module uses IO.

## Quickstart

```ailang
module myapp/discordbot

import pkg/sunholo/discord/client (readMessages, messagePath)
import std/io (println)
import std/result (isOk)

export func main() -> () ! {Net} {
  -- Offline, no token needed: validate and build a request path first.
  println("path-ok=${show(isOk(messagePath("123", {limit: 50, before: "", after: ""})))}");

  -- Live read (--caps Net): the token comes from your environment or a
  -- protected file — never hardcode it, never pass it through MCP tool arguments.
  match readMessages(tokenFromYourSecretStore(), "1549868288002236417", {limit: 5, before: "", after: ""}) {
    Ok(_) => println("read ok"),
    Err(e) => println("error kind=${e.kind} status=${show(e.status)}")
  }
}
```

Pagination: pass the previous page's oldest message ID as `before` (or the newest
as `after`); the two are mutually exclusive and validated. `limit` is bounded to
1..100.

Threads: a thread is a channel — pass its ID to `readMessages`/`sendMessage` and
everything works unchanged. `startThread(token, channelId, messageId, name)`
creates a thread from an existing message (names 1..100 chars) and returns the
thread channel; `activeThreads(token, channelId)` lists a channel's active
threads. `editMessage` PATCHes content on an existing message (same 1..2000
validation and mention suppression as sends; the reply reference is untouched);
`typing` raises the ~10s typing indicator and treats any 2xx as success
(Discord answers 204 with an empty body).

## Error handling

Every effectful call returns `Result[_, DiscordError]`. `DiscordError` carries
`kind` (`validation`, `decode`, `authentication`, `permission`, `rate_limit`,
`network`, `http`), Discord's `status`/`code`, a `message` that never echoes
remote bodies or tokens, `retryAfter` seconds (fractional; 429 only) and `global`.
There is no sleeping or automatic retry — callers decide. A `network` error on
POST means the outcome is unknown; reconcile before retrying. Discord's nonce
dedup (`sendMessage`'s `nonce` parameter, `enforce_nonce`) is time-limited and not
a durable exactly-once guarantee.

## Types and semantics

- `DiscordMessage`: IDs as strings (64-bit snowflakes survive JSON/WASM), author
  id/name, content, timestamp, reply reference, mentioned user IDs. Empty content
  can be legitimate (non-text messages, Message Content Intent restrictions);
  a *missing* content field is a decode error.
- `DiscordChannel`: id, name, kind (0 = text).
- `MessageQuery`: `limit` 1..100, exclusive `before`/`after` cursors.
- Outgoing mentions are suppressed by policy (`allowed_mentions.parse: []`,
  `replied_user: false`).
- Not modeled in this version: attachments, embeds, edits, gateway/websocket.
- Build guild message links yourself from your guild ID:
  `https://discord.com/channels/{guild}/{channel}/{message}`.

## Validation

- `ailang check --package .` — clean.
- `ailang test --package .` — 22 native tests, zero skips.
- `ailang run -caps IO --entry main _smoke.ail` — 12/12 boot checks (run
  automatically by `ailang publish`).
- `ailang pkg quality --strict .` — 0 declaration gaps.
- Upstream protocol checks live in `ailang-demos/discord` (`npm test`), which
  additionally validates live behavior and the MCP tool surface.