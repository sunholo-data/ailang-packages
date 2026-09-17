# sunholo/agui

Pure AG-UI codecs for AILANG. Import `pkg/sunholo/agui/events`. The package ceiling
declares IO solely for the offline `_smoke.ail` boot gate (`ailang run -caps IO
--entry main _smoke.ail`); every library module is pure (zero effects) — consumer
programs need no capabilities beyond their own effects.

Install: `ailang install sunholo/agui@0.2.0`. Full quickstart, the sequential
run profile and the round-trip guarantee: package README.md and
`ailang pkg-docs sunholo/agui` (this file).

Second module `sunholo/agui/input` decodes the request side: `decodeRunAgentInput`
parses the RunAgentInput payload a client sends to start a run — required
`threadId`/`runId`, strict role discrimination (user, assistant, system,
developer, tool; tool messages must carry toolCallId), tool names required,
`state`/`forwardedProps` defaulted to empty objects. Malformed JSON and unknown
roles are errors; empty message/tool lists are valid.

`Event` constructors: RunStarted(threadId, runId), RunFinished(threadId, runId),
RunError(message), TextStart(messageId), TextContent(messageId, delta),
TextEnd(messageId), ToolStart(toolCallId, toolName), ToolArgs(toolCallId, delta),
ToolEnd(toolCallId), ToolResult(messageId, toolCallId, content), StateSnapshot(Json),
Custom(name, Json).

Functions: eventName(Event), eventJson(Event), encodeEvent(Event), decodeEvent(string),
jsonLines([Event]), sseFrame(Event), validateRun([Event]). `eventName` returns the
canonical AG-UI type discriminator per variant ("RUN_STARTED", "TEXT_MESSAGE_CONTENT",
…) and is the single source of the type mapping shared by `eventJson` and `decodeEvent`.

`validateRun` implements a sequential profile: one active text stream and one
active tool at a time; a matching terminal run event; complete JSON arguments before
ToolEnd; a ToolResult before successful completion. ToolEnd closes argument
streaming, NOT execution. Errors may terminate an interrupted stream.

The decoder accepts only the documented subset (assistant text role). Unsupported
variants are errors. Optional metadata/extensions are not retained by the typed
representation: do not use it as a lossless proxy for arbitrary upstream events.
`jsonLines` and `sseFrame` are serializers, not a live HTTP server.

For A2UI fixed layouts, put `a2ui_operations` in a tool result JSON object as described
by upstream AG-UI's A2UI middleware; consumers register a compatible catalog.
`ailang-demos/discord` demonstrates real draft creation and deterministic replay.

Validation (2026-09-15, AILANG dev + `pkg quality` on `build/package-authoring-followups`):

- `ailang check --package .`: clean.
- `ailang test --package .`: 13 native tests, 13 passed, 0 failed, 0 skipped.
- `ailang test events.ail --allow-skips`: 1 contract-derived property case runs
  (`decodeEvent`, 100 generated cases: malformed JSON never produces an event); 7 skip
  because the generator cannot derive `Event`/`[Event]` — `Event` is same-file but its
  `StateSnapshot(Json)`/`Custom(_, Json)` payloads reference the imported `Json` ADT,
  which has no generator. Structural, not a test failure. 0 failures.
- `ailang verify events.ail` (with `--relax-modules`): 8 skipped — no SMT encoding for
  the `Json` ADT sort, `std/json.encode`/`decode`, string interpolation (`show`), or
  callees returning `Option`/`Result`. 0 counterexamples. Behavioral evidence is the
  13 native tests plus the runtime property above.
- `ailang pkg quality --strict .` (2026-09-17, the shipped command — the 2026-09-15 line
  above came from a branch prototype): compile ✓ 5 files · contracts 0/12 verified,
  12 skipped by Z3 (`PUB016`, unencodable `Json`/string builtins — runtime assertions,
  not proofs) · interface v2 24 signatures · effects `[IO]` · 8/8 exported funcs pure ·
  tests 19/19 in 2 files · smoke ✓. Under `--strict` three gates: `PUB001` (no
  `## 0.2.1` CHANGELOG section), `PUB002` (no `[release] kind`), `PUB021` (no
  `[metadata] repository` → no `pkg:sunholo/agui` inbox agent). Fix all three on the
  next release.
- Explicit `properties [...]` (forall) blocks are not used: the forall lowering is
  broken upstream (core #624).

Demo integration uses pinned `@ag-ui/core` 0.0.59 to validate every emitted event
independently. Specification: https://docs.ag-ui.com/concepts/events
