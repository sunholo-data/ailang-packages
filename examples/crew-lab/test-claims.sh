#!/usr/bin/env bash
# Acceptance harness only: crew-sim --check states expectations and reports each
# as PASS/FAIL, deterministically, failing loudly on changed ships and bad claims.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-claims.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" >/dev/null
SIM="$TMP/bin/crew-sim"
# The shipped claims hold for the default ship, the same way twice.
"$SIM" --check "$EX/data/watch-claims.json" > "$TMP/a.txt"
"$SIM" --check "$EX/data/watch-claims.json" > "$TMP/b.txt"
cmp "$TMP/a.txt" "$TMP/b.txt"
grep -q '^10 of 10 claims hold' "$TMP/a.txt"
if grep -q '^FAIL' "$TMP/a.txt"; then echo "default ship fails a claim" >&2; exit 1; fi
# A well-supplied ship breaks the named supplies claim: exit 1, others still checked.
jq '.resources |= map(.initial=99)' "$EX/data/watch-scenario.json" > "$TMP/rich.json"
if "$SIM" --check "$EX/data/watch-claims.json" --scenario "$TMP/rich.json" --seeds 1..8 > "$TMP/rich.txt"; then echo "changed ship passed every claim" >&2; exit 1; fi
grep -q '^FAIL supplies-block-work: ' "$TMP/rich.txt"
grep -q '^PASS orders-erode-medic-trust: ' "$TMP/rich.txt"
# Malformed claims are rejected before any run, naming the problem.
bad() { printf '%s' "$2" > "$TMP/bad.json"; if "$SIM" --check "$TMP/bad.json" --seeds 1 > "$TMP/bad.out"; then echo "accepted: $1" >&2; exit 1; fi; grep -q "^invalid claims: .*$3" "$TMP/bad.out" || { echo "wrong message for $1:" >&2; cat "$TMP/bad.out" >&2; exit 1; }; }
bad typo '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"crew.medic.trst","stat":"median","op":"<","value":40}]}' 'unknown metric'
bad crew '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"crew.cook.trust","stat":"median","op":"<","value":40}]}' 'unknown metric'
bad share '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"starts","stat":"share","op":">=","value":0.5}]}' 'share needs when'
bad field '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"starts","stat":"max","op":">=","value":1,"weight":2}]}' 'unknown field'
bad dup '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"starts","stat":"max","op":">=","value":1},{"id":"t","captain":"consent","metric":"starts","stat":"max","op":">=","value":1}]}' 'duplicate'
bad reason '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"refusal_reasons.no_such_reasn","stat":"max","op":"==","value":0}]}' 'unknown metric'
bad note '{"schema":"crew_claims/1","claims":[{"id":"t","captain":"orders","metric":"starts","stat":"max","op":">=","value":1,"note":7}]}' 'text fields must be strings'
bad schema '{"schema":"crew_claims/2","claims":[]}' 'schema'
# Long runs no longer stop at the old 64-answer limit.
"$SIM" --turns 60 --seeds 1..3 > "$TMP/long.ndjson"
jq -s -e 'length==3 and all(.[]; .tick==60 and .errors==0)' "$TMP/long.ndjson" >/dev/null
printf 'crew-sim --check: shipped claims hold deterministically; a changed ship fails the named claim (exit 1); malformed claims rejected; 60-turn runs clean\n'
