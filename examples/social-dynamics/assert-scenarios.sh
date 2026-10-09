#!/usr/bin/env bash
set -euo pipefail
OUT=${1:?trace directory required}
value() { jq -s -r --arg actor "$2" --arg indicator "$3" 'last.state.actors[] | select(.id==$actor) | .indicators[] | select(.id==$indicator) | .value' "$OUT/$1.ndjson"; }
[[ $(value ship-care scientist fatigue) == 25 ]]
[[ $(value ship-care scientist readiness) == 70 ]]
[[ $(value ship-care scientist observations) == 0 ]]
[[ $(value ship-collaboration scientist fatigue) == 80 ]]
[[ $(value ship-collaboration scientist observations) == 50 ]]
[[ $(value ship-renegotiate scientist fatigue) == 40 ]]
[[ $(value community-repair resident readiness) == 70 ]]
[[ $(value community-festival resident observations) == 15 ]]
jq -s -e 'last.state.conditions[0].active == true' "$OUT/ship-collaboration.ndjson" >/dev/null
for trace in "$OUT"/ship-{care,collaboration,renegotiate}.ndjson "$OUT"/community-{repair,festival}.ndjson; do
 jq -s -e 'all(.[].state.resources[]; .available+.reserved+.consumed == .initial+.transferred_in-.transferred_out)' "$trace" >/dev/null
 jq -s -e '.[-1].state == .[-2].state and .[-1].events == []' "$trace" >/dev/null
 jq -s -e '[.[].events[] | .seq] as $ids | ($ids | length) == ($ids | unique | length)' "$trace" >/dev/null
 done
printf 'Five contrasting outcomes, resource conservation and repeated delivery checks pass\n'
