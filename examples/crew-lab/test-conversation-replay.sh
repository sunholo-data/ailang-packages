#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
AILANG=${AILANG:-ailang}
TEMP_RUN=$(mktemp -d "${TMPDIR:-/tmp}/crew-conversation-replay.XXXXXX")
trap 'rm -rf "$TEMP_RUN"' EXIT
for fixture in "$ROOT"/examples/crew-lab/recordings/conversations/*.jsonl; do
 name=$(basename "$fixture" .jsonl)
 AILANG="$AILANG" "$ROOT/examples/crew-lab/run.sh" interpreter "$fixture" > "$TEMP_RUN/$name-eval"
 AILANG="$AILANG" "$ROOT/examples/crew-lab/run.sh" vm "$fixture" > "$TEMP_RUN/$name-vm"
 cmp "$TEMP_RUN/$name-eval" "$TEMP_RUN/$name-vm"
 jq -s -e 'all(.[];.error==null and .blocked==null)' "$TEMP_RUN/$name-eval" >/dev/null
 done
jq -s -e 'last | .state.tick==0 and (.state.tasks|length)==1 and .state.tasks[0].status=="working" and all(.host.personalities[];.current==.baseline)' "$TEMP_RUN/medic-reply-eval" >/dev/null
jq -s -e 'last | .state.tick==10 and (.state.tasks|length)==1 and .state.tasks[0].status=="completed" and any(.host.personalities[];.actor=="medic" and any(.current[];.id=="neuroticism" and .value==56) and any(.history[];.interaction=="support"))' "$TEMP_RUN/major-response-eval" >/dev/null
printf 'PASS same-proposal medic recording and major-response/influence evaluator/strict-VM replay\n'
