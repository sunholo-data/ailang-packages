# Changelog

## 0.2.0

Add reusable pure selection, confirmation and paging widgets with normalized events.
Add native/line/plain/auto IO adapters backed by `std/terminal` and exact line EOF
from `std/io.readLineOpt`; native acquisition errors are surfaced without changing
interaction mode. Preserve all existing `ui` APIs and sanitation behavior.

Add version-1 JSON transcripts with explicit viewport/style/bounds, complete event
round trips, UTF-8 byte limits and deterministic selection replay with ordered
frames. Persistence stays with the caller; capture is not automatic telemetry.

Upgrade `terminal-ui-demo` with immediate native keys, resizing, selection →
confirmation → paged reading, explicit mode/size flags and measured small-terminal
output. The binary needs IO and Env for arguments; the adapter library needs only IO.
Requires a supporting AILANG v0.54.0+ release; macOS/Linux native scopes only.

## 0.1.0

Experimental pure bounded terminal layout, sanitized cell wrapping, paging,
ANSI/plain frames and IO-only independent demo. Line-key input; no raw mode.
