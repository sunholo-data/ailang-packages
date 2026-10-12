#!/usr/bin/env bash
# Acceptance harness only: installed crew-sim is deterministic, sensitive to the
# scenario, summarises without ranking and rejects malformed scenarios up front.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-sim.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" > /dev/null
SIM="$TMP/bin/crew-sim"
"$SIM" --seeds 1..4 --turns 8 > "$TMP/a.ndjson"
"$SIM" --seeds 1..4 --turns 8 > "$TMP/b.ndjson"
cmp "$TMP/a.ndjson" "$TMP/b.ndjson"
test "$(wc -l < "$TMP/a.ndjson" | tr -d ' ')" = 4
jq -s -e 'all(.[]; .schema=="crew_sim/1" and .errors==0 and .tick==8)' "$TMP/a.ndjson" > /dev/null
jq '(.crew[] | select(.id=="scientist") | .ocean.neuroticism) = 90' "$EX/data/watch-scenario.json" > "$TMP/anxious.json"
"$SIM" --seeds 1..4 --turns 8 --scenario "$TMP/anxious.json" > "$TMP/c.ndjson"
if cmp -s "$TMP/a.ndjson" "$TMP/c.ndjson"; then echo "trait change did not change output" >&2; exit 1; fi
"$SIM" --summary "$TMP/a.ndjson" > "$TMP/summary.txt"
grep -q '^4 runs\. Median' "$TMP/summary.txt"
grep -q '^crew.scientist.trust: ' "$TMP/summary.txt"
if tail -n +2 "$TMP/summary.txt" | grep -qiE 'best|winner|score|rank'; then echo "summary must not rank" >&2; exit 1; fi
for bad in 'del(.resources)' '(.crew[0].work[0].costs[0].resource)="sugar"' '(.crew[0].ocean.openness)=101'; do
  jq "$bad" "$EX/data/watch-scenario.json" > "$TMP/bad.json"
  if "$SIM" --seeds 1 --scenario "$TMP/bad.json" > "$TMP/bad.out"; then echo "accepted malformed scenario: $bad" >&2; exit 1; fi
  grep -q '^invalid scenario: ' "$TMP/bad.out"
done
start=$(date +%s); "$SIM" --seeds 1..20 --turns 12 > /dev/null; elapsed=$(( $(date +%s) - start ))
printf 'crew-sim: deterministic, scenario-sensitive, unranked summary, malformed scenarios rejected; 20 seeds x 12 turns in %ss\n' "$elapsed"
