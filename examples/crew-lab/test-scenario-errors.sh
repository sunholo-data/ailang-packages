#!/usr/bin/env bash
# Acceptance harness only: the installed watch runs a custom scenario JSON,
# records its hash, and rejects malformed scenarios or policies before any
# journal exists.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-scenario.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" > /dev/null
W="$TMP/bin/crew-watch-offline"
journal() { ls "$1"/runs/*/journal.jsonl | head -1; }
printf '1\n1\n1\n0\n' | "$W" --mode plain --home "$TMP/default" --seed 42 > "$TMP/default.out"
DEFAULT_HASH=$(head -1 "$(journal "$TMP/default")" | jq -r .payload.scenario_hash)
jq '(.crew[] | select(.id=="scientist") | .work[0].name) = "Model the Spire biosphere"' "$EX/data/watch-scenario.json" > "$TMP/ship.json"
printf '1\n1\n1\n0\n' | "$W" --mode plain --home "$TMP/custom" --seed 42 --scenario "$TMP/ship.json" > "$TMP/custom.out"
grep -q 'Model the Spire biosphere' "$TMP/custom.out"
CUSTOM_HASH=$(head -1 "$(journal "$TMP/custom")" | jq -r .payload.scenario_hash)
test "${#CUSTOM_HASH}" = 64 && test "$CUSTOM_HASH" != "$DEFAULT_HASH"
head -1 "$(journal "$TMP/custom")" | jq -e '.payload.scenario | fromjson | .crew[0].work[0].name == "Model the Spire biosphere"' > /dev/null
n=0
for bad in 'del(.resources)' '(.crew[0].work[0].costs[0].resource)="sugar"' '(.crew[0].ocean.openness)=101' '(.captain.id)="skipper"'; do
  n=$((n+1)); jq "$bad" "$EX/data/watch-scenario.json" > "$TMP/bad$n.json"
  if "$W" --mode plain --home "$TMP/bad$n" --scenario "$TMP/bad$n.json" < /dev/null > "$TMP/bad$n.out" 2>&1; then echo "accepted: $bad" >&2; exit 1; fi
  grep -q '^Invalid scenario ' "$TMP/bad$n.out"
  if ls "$TMP/bad$n"/runs/*/journal.jsonl > /dev/null 2>&1; then echo "journal created for $bad" >&2; exit 1; fi
done
printf '{"schema":"nope"}' > "$TMP/policy.json"
if "$W" --mode plain --home "$TMP/badpolicy" --policy "$TMP/policy.json" < /dev/null > "$TMP/policy.out" 2>&1; then echo "accepted bad policy" >&2; exit 1; fi
grep -q '^Invalid policy ' "$TMP/policy.out"
printf 'Scenario files: custom ship runs and is journaled by hash; %s malformed scenarios and a malformed policy rejected before any journal\n' "$n"
