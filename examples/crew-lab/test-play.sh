#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-play-test.XXXXXX")
PLAY_PID=""
trap 'if [[ -n "$PLAY_PID" ]]; then kill "$PLAY_PID" 2>/dev/null || true; fi; rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin"
cd "$TMP"
"$TMP/bin/crew-play-offline" --home "$TMP/science" < "$EX/recordings/play-science.menu" > "$TMP/science.out"
test -f "$TMP/science/response-policy.json"
# For care/denial/project controls, use an explicit authored test policy to make
# response intents predictable. Normal default weights remain in the science run.
for path in care deny projects; do
 mkdir -p "$TMP/$path"
 jq '.rules |= map(.base = (if .label=="accept" or .label=="request_relief" then 1000 else 0 end) | .influences=[])' "$TMP/science/response-policy.json" > "$TMP/$path/response-policy.json"
 "$TMP/bin/crew-play-offline" --home "$TMP/$path" < "$EX/recordings/play-$path.menu" > "$TMP/$path.out"
done
for path in science care deny projects; do
 journals=("$TMP/$path"/runs/*/journal.jsonl)
 test "${#journals[@]}" = 1
 journal=${journals[0]}
 jq -r 'select(.payload.host_input != null) | .payload.host_input' "$journal" > "$TMP/$path-input.ndjson"
 jq -r 'select(.payload.host_output != null) | .payload.host_output' "$journal" > "$TMP/$path-expected.ndjson"
 AILANG="$AILANG" "$EX/run.sh" interpreter "$TMP/$path-input.ndjson" > "$TMP/$path-replay.ndjson"
 cmp "$TMP/$path-expected.ndjson" "$TMP/$path-replay.ndjson"
 AILANG="$AILANG" "$EX/run.sh" vm "$TMP/$path-input.ndjson" > "$TMP/$path-vm.ndjson"
 cmp "$TMP/$path-replay.ndjson" "$TMP/$path-vm.ndjson"
 jq -s -e 'map(.seq) == [range(0;length)] and all(.[]; .version==1) and
 any(.[]; .payload.metadata.selection.bundle.origin=="authored") and
 all(.[] | select(.payload.metadata.usage!=null); .payload.metadata.usage.calls==0 and .payload.metadata.usage.input_tokens==0 and .payload.metadata.usage.output_tokens==0)' "$journal" > /dev/null
done
jq -s -e 'last.state.tasks | any(.[]; .recipe=="observations" and .status=="completed")' "$TMP/science-replay.ndjson" > /dev/null
jq -s -e 'last.state | (.resources[0].available==6 and .resources[0].consumed==0) and any(.tasks[]; .recipe=="rest_scientist" and .status=="completed") and any(.tasks[]; .recipe=="observations" and .status=="stopped")' "$TMP/care-replay.ndjson" > /dev/null
jq -s -e 'last.state | .resources[0].consumed==4 and any(.tasks[]; .recipe=="observations" and .status=="completed")' "$TMP/deny-replay.ndjson" > /dev/null
jq -s -e 'last.state | .resources[0].consumed==6 and .resources[0].available==0 and ([.tasks[]|select(.status=="completed")]|length)==2' "$TMP/projects-replay.ndjson" > /dev/null
# Force journal publication failure after startup: an existing directory at the
# temporary file path makes Result-returning file write fail before rename.
mkfifo "$TMP/input.fifo"
exec 3<> "$TMP/input.fifo"
"$TMP/bin/crew-play-offline" --home "$TMP/failure" --seed 42 < "$TMP/input.fifo" > "$TMP/failure.out" 2> "$TMP/failure.err" &
PLAY_PID=$!
printf '1\n' >&3
shopt -s nullglob
for attempt in {1..100}; do
 journals=("$TMP/failure"/runs/*/journal.jsonl)
 if [[ ${#journals[@]} = 1 ]]; then break; fi
 sleep 0.05
done
test "${#journals[@]}" = 1
journal=${journals[0]}
cp "$journal" "$TMP/before.jsonl"
mkdir "$journal.tmp"
printf '1\n' >&3
set +e
wait "$PLAY_PID"
rc=$?
set -e
PLAY_PID=""
exec 3>&-
test "$rc" = 1
cmp "$journal" "$TMP/before.jsonl"
rg -q 'Journal failed; prior Session and seed retained' "$TMP/failure.out"
if rg -q '^scientist:' "$TMP/failure.out"; then printf 'Dialogue exposed before failed journal publication\n' >&2; exit 1; fi
# Installed argument boundary is independent of cwd and has no secret/network access.
if "$TMP/bin/crew-play-offline" --wat > "$TMP/args.out" 2>&1; then exit 1; fi
printf 'Guided offline UI: science/care/denial/material competition, extracted replay + strict VM, zero calls, journal rollback and arguments pass\n'
