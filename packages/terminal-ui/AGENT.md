# sunholo/terminal_ui

Reusable safe rendering, pure widgets/replay and a native terminal adapter. Preserve
application data and sanitize display projections only. `terminal-ui-demo` is an
independent `[bin]` command; it does not alter the Go CLI or message store.

## Modules and effects

- `ui` (pure): existing Dimensions/Screen, dimensions, safeText, cells, wrap, pad,
  rule, gauge, clampPage and screen. The v0.1 contracts/behavior remain unchanged.
- `events` (pure): Event/KeyCode ADTs, lineEvent, ending. `Some("")` is NoInput;
  None is Finished. Native keys normalize to the same vocabulary.
- `widgets` (pure): Menu, Confirmation, Pager; constructors and update functions.
  Menus clamp rather than wrap; empty menus cannot select; completed widgets stay
  stable. Confirmation defaults are explicit, and cancellation has no answer.
  viewport caps maxima at 160×60 while retaining physical small dimensions;
  frame emits an ASCII compact message below 40×16, fitting even 1×1.
- `transcript` (pure): Config, Transcript, TranscriptError, Replay;
  encodeTranscript/decodeTranscript, replaySelection, selectionFrame/selectionBody.
- `text_field` (pure): create/update a 1..4096-codepoint Field. Exact text is
  kept through Unicode insertion, left/right/home/end, backward/forward deletion,
  submission and cancellation. Reject control-containing/overlength insertions
  atomically. Accept submits nonblank exact text; cancelled/completed fields stay
  stable. No application hotkeys are interpreted: Character("q") is text.
- `adapter` (IO only): choose/resolve explicit Native/Line/Plain/Auto; run scopes
  a host session; readInput and writeFrame adapt normalized inputs/frames.

The manifest ceiling is IO,Env because demo arguments use std/env.getArgs. Library
adapters require only IO. Pure modules need no capabilities. No FS, Process, AI,
Clock or shell host is introduced. Native support requires a supporting core release
(AILANG >=0.54.0); development validation uses the sprint binary and its stdlib.
Native sessions are macOS/Linux only. Windows/WASM hosts return typed Unsupported;
plain/line and pure replay remain available. Real mode/signal cleanup belongs to
std/terminal, including callbacks that fail or exit, not to an AILANG success path.

## Use

```ailang
import pkg/sunholo/terminal_ui/events (Input, Next, Accept)
import pkg/sunholo/terminal_ui/widgets (menu, updateMenu)
let selected = updateMenu(updateMenu(menu(3), Input(Next)), Input(Accept));
-- selected.selected is Some(1); selected.done is true
```

Consumers map business state through pure event updates, render sanitized frames,
then write through the IO adapter. `run(resolved, body)` supplies
Option[TerminalSession]: Some(handle) for native, None for line/plain. The callback
can return its own Result; run preserves it inside the outer acquisition Result.

```sh
terminal-ui-demo --mode auto
terminal-ui-demo --mode native
terminal-ui-demo --mode line --columns 60 --rows 24
printf '\nq\n' | terminal-ui-demo --mode plain
```

Auto resolves once from input/output TTY facts: supported TTYs → native, remaining
TTY pair → line, redirected endpoints → plain. The demo reports selected mode to
stderr. Native uses measured size and ignores layout flags; line/plain use explicit
layout, default 60×24 in this demo. The library never invents a missing measured
size: supply Dimensions or receive MissingSize. Native acquisition/query errors
remain HostError; they never trigger a later mode downgrade.

Native: arrows choose, Enter selects/accepts, Left/Right choose No/Yes; reading uses
arrows/PageUp/PageDown/Home/End. h guide, b menu, q/0/Escape quit immediately.
Line/plain: up/down/enter/left/right/pgup/pgdn/home/end plus Enter, n/v aliases,
h/b/q/0 controls. A blank line leaves the state unchanged; exact EOF exits.
Plain output contains no ANSI escapes. The legacy ui.screen reserves an empty
prompt row; use print(text), then a prompt, flush. Avoid appending a newline before
input. Larger viewports retain state and clamp the displayed page after resize.

## Replay and bounds

Version 1 JSON stores config and ordered events. Config has initial columns/rows,
ansi, max_events (0..4096), max_bytes (1..4194304), max_frame_bytes (1..1048576).
Sizes must be positive and <=65535. A text key has 1..4096 UTF-8 bytes. The decoder
also requires its caller's byte ceiling. Exact integer fields are required;
fractional sizes, unknown event/key/version, malformed JSON and invalid bounds
fail BadFormat. Exceeding any budget fails LimitExceeded; no events/frames are
silently dropped. Canonical event forms are `["key","down"]`,
`["key","text","data"]`, `["resize",20,8]`, `["idle"]`, `["eof"]`,
`["interrupted"]`. All navigation keys roundtrip. No live IO occurs during replay.

replaySelection returns the initial frame and one frame per event, plus final Menu;
identical inputs/config/labels give identical ordered frames/model. A resize changes
viewport while retaining cursor; a completed model remains completed. Caller-owned
labels/business configuration are supplied separately and must match when replaying.
Capture includes original text (possibly sensitive); it is explicit caller data,
not telemetry. Callers decide consent, redaction and persistence. Existing rendered
IO traces are observational and do not substitute for this lossless event format.

`ui` keeps its existing minimum layout clamp 40×16; use widgets.viewport/frame for
actual measured sizes. For ordinary frames, keep wrapped header/action rows <=
rows-5 as required by ui.screen. Cells conservatively count known Latin/punctuation/
box drawing as one, other glyphs including CJK as two; no grapheme/emoji precision
is promised. C0/C1/bidi are stripped from display text. ANSI sequences are trusted
renderer output only. Never print raw untrusted source text directly.

IO budgets: choose/readInput each permit one observation, writeFrame at most three
IO operations. run/interactive demo duration is intentionally user-driven and has
no fixed total operation ceiling; consumers can supply an outer IO budget. Decoder,
transcript and viewport sizes are explicitly bounded.

Native output uses `frameText(Native, text)` to convert LF/CRLF to CRLF exactly
once: raw mode disables driver newline translation. Line/Plain projections keep
their input bytes unchanged. Screen.lines and cached application text stay untouched.

## Validation

Run lock, check --package, test --package (evaluator and strict VM), each implementation
module's inline tests, pkg quality --strict and publish --dry-run against the supporting
binary/stdlib. Run `_smoke.ail` without a real terminal; it checks codec/replay plus
plain scope. Package named/property checks are distinct from Z3 contracts, and inline
precondition-domain shortages are reported as skips, not proofs. Real PTY navigation,
resize and host cleanup are core/installed-bin integration controls.

The current strict VM rejects functions with `@limit` budget frames before execution.
The effectful adapter/demo therefore uses the evaluator; this is an explicit backend
diagnostic, not a fallback. Pure named widget/codec/adapter-decision tests run under
strict VM with zero evaluator fallback; core unbudgeted native API parity is tested
separately. Do not remove budgets merely to suppress the backend limitation.
