# sunholo/agui

Pure AG-UI protocol codecs for AILANG: typed events, JSON/SSE encoding, strict
decoding and sequential run validation. Zero effects — runnable anywhere.

## Install

```sh
ailang install sunholo/agui@0.2.0
```

```ailang
import pkg/sunholo/agui/events (RunStarted, TextContent, encodeEvent, decodeEvent, validateRun)
```

## Effects

None. Every module is pure; no capabilities required. (The package ceiling
declares `IO` solely for the offline `_smoke.ail` boot gate.)

## Quickstart

```ailang
module myapp/agentui

import pkg/sunholo/agui/events (RunStarted, TextStart, TextContent, TextEnd,
  RunFinished, validateRun, jsonLines, sseFrame)
import std/io (println)
import std/result (isOk)

export func main() -> () ! {IO} {
  let run = [RunStarted("t1", "r1"), TextStart("m1"), TextContent("m1", "hello"),
    TextEnd("m1"), RunFinished("t1", "r1")];
  println("legal run: ${show(isOk(validateRun(run)))}");
  println(jsonLines(run));
  -- one SSE frame per event: "data: {json}\n\n"
  println(sseFrame(TextContent("m1", "hi")))
}
```

## Request side

`sunholo/agui/input` decodes what a client sends to start a run:
`decodeRunAgentInput(raw) -> Result[RunAgentInput, string]` — required
`threadId`/`runId`, strict role discrimination (user, assistant, system,
developer, tool; tool messages must carry `toolCallId`), tool names required,
`state`/`forwardedProps` defaulted to empty objects. Malformed JSON and unknown
roles are errors; empty message/tool lists are valid.

Round-trip: `decodeEvent(encodeEvent(e))` reconstructs every supported event;
unsupported or malformed upstream events decode to `Err` — nothing is silently
coerced into a supported type.

## The Event type

`RunStarted(threadId, runId)`, `RunFinished(threadId, runId)`, `RunError(message)`,
`TextStart(messageId)`, `TextContent(messageId, delta)`, `TextEnd(messageId)`,
`ToolStart(toolCallId, toolName)`, `ToolArgs(toolCallId, delta)`,
`ToolEnd(toolCallId)`, `ToolResult(messageId, toolCallId, content)`,
`StateSnapshot(Json)`, `Custom(name, Json)`.

`eventName` returns the canonical AG-UI discriminator string per variant
("RUN_STARTED", "TEXT_MESSAGE_CONTENT", …); `eventJson`/`decodeEvent` share that
single mapping.

## Sequential run profile

`validateRun` enforces a deliberately narrower profile than AG-UI itself:

- the run starts with `RunStarted` and ends with exactly one terminal event
  (`RunFinished` matching the run identity, or `RunError`);
- one active text stream and one active tool at a time;
- `ToolEnd` closes argument streaming, NOT tool execution;
- tool arguments must be complete JSON before `ToolEnd`, and a `ToolResult`
  requires completed arguments;
- `StateSnapshot`/`Custom` may appear anywhere inside the run.

The decoder accepts only this subset (assistant role for text). Optional
metadata/extensions are not retained by the typed representation — do not use it
as a lossless proxy for arbitrary upstream events. `jsonLines` and `sseFrame` are
serializers, not a live HTTP server.

For A2UI fixed layouts, put `a2ui_operations` in a tool result JSON object per
upstream AG-UI's A2UI middleware; consumers register a compatible catalog.
`ailang-demos/discord` demonstrates real draft creation and deterministic replay.

## Validation

- `ailang check --package .` — clean.
- `ailang test --package .` — 13 native tests, zero skips.
- `ailang run -caps IO --entry main _smoke.ail` — 10/10 boot checks (run
  automatically by `ailang publish`).
- `ailang pkg quality --strict .` — 0 declaration gaps.
- The demo additionally validates every emitted event against pinned
  `@ag-ui/core` 0.0.59.
- Specification: https://docs.ag-ui.com/concepts/events