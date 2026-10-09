#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
AILANG=${AILANG:-ailang}
MODE=${1:-interpreter}
INPUT=${2:?input recording required}
if [[ ! -f "$INPUT" ]]; then printf 'Missing recording: %s\n' "$INPUT" >&2; exit 1; fi
if [[ "$MODE" != interpreter && "$MODE" != vm ]]; then printf 'Unknown engine: %s\n' "$MODE" >&2; exit 1; fi
# Blank lines and oversized inputs are refused, not silently truncated at readLine EOF.
awk 'length($0)==0 || length($0)>65536 {bad=1} END {exit (bad || NR==0 || NR>10000)}' "$INPUT" || { printf 'Recording must contain 1..10000 nonblank NDJSON lines of at most 65536 bytes\n' >&2; exit 1; }
if [[ "$MODE" == interpreter ]]; then
 exec "$AILANG" run --package-dir "$ROOT/examples/social-dynamics" --caps IO --entry main "$ROOT/examples/social-dynamics/main.ail" < "$INPUT"
fi
# std/io.readLine is evaluator-only on pinned0.52.0. The same pure input/session
# functions replay on strict VM through structured entry arguments (zero caps).
ARGFILE=$(mktemp "${TMPDIR:-/tmp}/social-args.XXXXXX")
TRACEFILE=$(mktemp "${TMPDIR:-/tmp}/social-trace.XXXXXX")
trap 'rm -f "$ARGFILE" "$TRACEFILE"' EXIT
jq -Rs 'split("\n") | map(select(length>0))' "$INPUT" > "$ARGFILE"
"$AILANG" run --bytecode --strict-bytecode --package-dir "$ROOT/examples/social-dynamics" --entry recording --args-file "$ARGFILE" "$ROOT/examples/social-dynamics/session.ail" > "$TRACEFILE"
cat "$TRACEFILE"
jq -s -e 'all(.[]; (has("error") or has("blocked")) | not)' "$TRACEFILE" >/dev/null
