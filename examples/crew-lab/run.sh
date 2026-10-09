#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
AILANG=${AILANG:-ailang}
MODE=${1:-interpreter}
INPUT=${2:?input recording required}
if [[ ! -f "$INPUT" ]]; then printf 'Missing recording: %s\n' "$INPUT" >&2; exit 1; fi
if [[ "$MODE" != interpreter && "$MODE" != vm ]]; then printf 'Unknown engine: %s\n' "$MODE" >&2; exit 1; fi
LC_ALL=C awk 'length($0)==0 || length($0)>65536 {bad=1} END {exit (bad || NR==0 || NR>10000)}' "$INPUT" || { printf 'Recording must contain 1..10000 nonblank NDJSON lines of at most 65536 bytes\n' >&2; exit 1; }
if [[ "$MODE" == interpreter ]]; then
 exec "$AILANG" run --package-dir "$ROOT/examples/crew-lab" --caps IO --entry main "$ROOT/examples/crew-lab/main.ail" < "$INPUT"
fi
ARGFILE=$(mktemp "${TMPDIR:-/tmp}/crew-args.XXXXXX")
TRACEFILE=$(mktemp "${TMPDIR:-/tmp}/crew-trace.XXXXXX")
trap 'rm -f "$ARGFILE" "$TRACEFILE"' EXIT
jq -Rs 'split("\n") | map(select(length>0))' "$INPUT" > "$ARGFILE"
"$AILANG" run --bytecode --strict-bytecode --package-dir "$ROOT/examples/crew-lab" --entry recording --args-file "$ARGFILE" "$ROOT/examples/crew-lab/session.ail" > "$TRACEFILE"
cat "$TRACEFILE"
jq -s -e 'all(.[]; (has("error") or has("blocked")) | not)' "$TRACEFILE" >/dev/null
