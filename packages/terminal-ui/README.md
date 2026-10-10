# Terminal UI for AILANG

`sunholo/terminal_ui` helps packages build attractive keyboard-driven CLIs: safe
ANSI/plain rendering, selection and confirmation widgets, paging, resize handling,
and deterministic recorded-event replay. It evolves the existing renderer package.

The native adapter uses AILANG's scoped `std/terminal` API; the host restores the
terminal when the application returns, fails or exits. Native support targets
macOS and Linux. The pure renderer and replay layer require no capabilities.

Native frames return to column zero on every row using explicit CRLF: raw-mode
terminals do not translate LF automatically. Line/plain output remains byte-exact.

```sh
# Development checkout with a supporting AILANG binary:
ailang install --path packages/terminal-ui
terminal-ui-demo --mode native
terminal-ui-demo --mode line --columns 60 --rows 24
printf '\nq\n' | terminal-ui-demo --mode plain
```

Native mode takes immediate arrows/Enter/Escape, follows measured resize events,
and retains selection while a small viewport shows a compact message. The demo
walks through selection, confirmation and paged reading. Line mode uses named
keys such as `down`, `enter`, `right`, `pgdn`, each followed by Enter. Blank lines
are idle; EOF and q quit. Auto resolves once and reports the selected mode.

The CLI requires IO and Env for command arguments. Library adapters require IO
only. See [AGENT.md](AGENT.md) for public modules, event/transcript schemas, bounds,
consumer patterns and effect budgets. Existing `ui` exports remain compatible.

Version 0.2.0 requires a supporting AILANG >=0.54.0 release. Source/dry-run readiness
is distinct from registry availability. The current strict VM rejects budget-frame
functions explicitly; the effectful demo uses the evaluator. Pure package controls
run on the strict VM with zero fallback.

Validation and the release prerequisite are recorded in [VALIDATION.md](VALIDATION.md).

### Text entry

`text_field.create(text, limit)` constructs a pure editor; `update(field, event)`
returns the next field. `Character(text)` inserts exact text; arrows, Home/End,
Backspace/Delete move or remove Unicode codepoints. Enter sets `submitted` only
for a nonblank draft, while Escape sets `cancelled` without sending. Input is
bounded and control-free. Applications choose whether submission opens a review
step or commits a domain command. This widget performs neither IO nor inference.
