#!/bin/bash
# Widget HTML sanity beyond widget_test.ail: render the default widget, parse
# it (well-formed, one picker, two inline module scripts, nothing external)
# and syntax-check both scripts with `node --check` (skipped with a loud
# notice when node is absent; the parse checks still run).
set -uo pipefail
cd "$(dirname "$0")/.."
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
rc=0
ailang run --caps IO --entry main tests/print_widget.ail > "$WORK/widget.html" 2>"$WORK/err" || { echo "FAIL: render"; cat "$WORK/err"; exit 1; }
python3 -I tests/widget_check.py "$WORK/widget.html" "$WORK" || rc=1
if command -v node >/dev/null; then
  for s in "$WORK"/script*.mjs; do
    if node --check "$s" 2>"$WORK/node.err"; then echo "ok: node --check $(basename "$s")"
    else echo "FAIL: node --check $(basename "$s")"; head -5 "$WORK/node.err"; rc=1; fi
  done
else
  echo "NOTICE: node not found; JavaScript syntax NOT checked"
fi
[ $rc -eq 0 ] && echo "ok: widget html"
exit $rc
