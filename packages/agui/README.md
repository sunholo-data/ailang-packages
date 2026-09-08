# sunholo/agui 0.1.0

Pure AG-UI codecs for AILANG. Import `pkg/sunholo/agui/events`.

`Event` constructors: RunStarted(threadId, runId), RunFinished(threadId, runId),
RunError(message), TextStart(messageId), TextContent(messageId, delta),
TextEnd(messageId), ToolStart(toolCallId, toolName), ToolArgs(toolCallId, delta),
ToolEnd(toolCallId), ToolResult(messageId, toolCallId, content), StateSnapshot(Json),
Custom(name, Json).

Functions: eventJson(Event), encodeEvent(Event), decodeEvent(string),
jsonLines([Event]), sseFrame(Event), validateRun([Event]).

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

Validate with `ailang check --package .`. Demo integration uses pinned
`@ag-ui/core` 0.0.59 to validate every emitted event independently.
Specification: https://docs.ag-ui.com/concepts/events
