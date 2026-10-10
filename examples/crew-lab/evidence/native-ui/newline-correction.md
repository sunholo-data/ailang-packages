# Native raw-output row correction

Mark's real terminal screenshot revealed staircase text after the first graphical
release. Core v0.54.0 correctly disables output post-processing in raw mode; the
terminal_ui adapter incorrectly relied on LF translating to CRLF. Its output
projection now returns every native row to column zero; Line/Plain remain byte-exact.
The application and all gameplay authority stay pure AILANG as before.

The previous PTY test stripped ANSI and split bytes on LF. That checks frame
content, not visible cursor positions. A harness-only VT subset oracle now handles
clear/home/SGR, independent CR and LF, deferred edge wrapping and scrolling. Its
own controls show raw LF drift, CRLF alignment and a full-width rule without wrap.
Every actual captured frame must match its expected visible cell grid with zero
scrolls, including small screens and220×70 physical bounds beyond160×60 layout.
Old source failed with eight scroll rows at80×24; corrected source passes all
sizes, real four-turn science completion and normal/SIGINT/failure restoration.

Focused terminal controls:42/42 in interpreter and strict VM. Adapter inline:
8 passed/7 skipped (six unsupported generators and one precondition-domain skip).
Exact terminal proof inventory:35 total=12proved+22skipped+1unchanged encoder
error, zero counterexamples/uncontracted exports. frameText's replace contract
is tested at runtime; its unsupported SMT encoding is reported as skipped.
Quality strict and dry-run pass; registry overlap initially unavailable in sandbox.

The full local suite, exact-head CI, independent correction evaluation and actual
registry/installation records accompany landing. No live AI calls are needed.
