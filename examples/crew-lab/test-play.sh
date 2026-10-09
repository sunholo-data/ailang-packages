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
# Help at bridge and start menus is pure: identical host journal, seed and usage.
"$TMP/bin/crew-play-offline" --home "$TMP/newcomer" < "$EX/recordings/play-newcomer.menu" > "$TMP/newcomer.out"
journals=("$TMP/newcomer"/runs/*/journal.jsonl)
original=("$TMP/science"/runs/*/journal.jsonl)
jq -s 'map(.payload)' "${journals[0]}" > "$TMP/newcomer-payload.json"
jq -s 'map(.payload)' "${original[0]}" > "$TMP/science-payload.json"
cmp "$TMP/newcomer-payload.json" "$TMP/science-payload.json"
rg -q 'You are the captain' "$TMP/newcomer.out"
rg -q "CAPTAIN'S GUIDE" "$TMP/newcomer.out"
# Help must remain below the latest dashboard until its current numbered menu.
awk '/^\[ CAPTAIN.S GUIDE \]/{guide=1} guide && /^\[ BRIDGE/{bad=1} /^1\. (Offer|Start)/{guide=0} END{exit bad}' "$TMP/newcomer.out"
rg -q 'Elapsed: 4 ticks. Completed projects: 1' "$TMP/newcomer.out"
# A cached authored bundle stays stock narration; transport provenance remains cache.
mkdir -p "$TMP/cached-stock/cache"
original=("$TMP/science"/runs/*/journal.jsonl)
key=$(jq -r 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle.key' "${original[0]}")
jq 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle' "${original[0]}" > "$TMP/cached-stock/cache/$key.json"
cp "$TMP/science/response-policy.json" "$TMP/cached-stock/response-policy.json"
"$TMP/bin/crew-play-offline" --home "$TMP/cached-stock" < "$EX/recordings/play-science.menu" > "$TMP/cached-stock.out"
rg -q 'Saved stock wording; no AI call' "$TMP/cached-stock.out"
rg -q 'Crew reaction \(narrator\): scientist agrees' "$TMP/cached-stock.out"
if rg -q 'Saved AI wording' "$TMP/cached-stock.out"; then exit 1; fi
journals=("$TMP/cached-stock"/runs/*/journal.jsonl)
jq -s -e 'any(.[]; .payload.metadata.usage.source=="cache" and .payload.metadata.usage.calls==0 and .payload.metadata.selection.bundle.origin=="authored")' "${journals[0]}" > /dev/null
jq 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection' "${original[0]}" > "$TMP/stock-before.json"
jq 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection' "${journals[0]}" > "$TMP/stock-after.json"
cmp "$TMP/stock-before.json" "$TMP/stock-after.json"
# Ordinary published resource rejection must leave the captain playing.
mkdir -p "$TMP/shortage"
cp "$TMP/projects/response-policy.json" "$TMP/shortage/response-policy.json"
"$TMP/bin/crew-play-offline" --home "$TMP/shortage" < "$EX/recordings/play-shortage.menu" > "$TMP/shortage.out"
journals=("$TMP/shortage"/runs/*/journal.jsonl)
jq -s -e 'any(.[]; (.payload.host_output? // "") | startswith("{\"error\"")) and last.payload.kind=="quit"' "${journals[0]}" > /dev/null
jq -s -e '[.[]|select((.payload.host_output? // "") | startswith("{\"error\""))] | length==2 and all(.[]; .payload.seed_before==.payload.seed_after)' "${journals[0]}" > /dev/null
jq -s -e '[.[]|select(.payload.host_output? != null)|.payload.host_output|fromjson|select(.state!=null)]|last.state | .tick==6 and .resources[0].available==2 and .resources[0].consumed==4 and any(.tasks[]; .recipe=="rest_scientist" and .status=="completed")' "${journals[0]}" > /dev/null
# Crew occupancy and consent denial are also recorded, recoverable starts.
mkdir -p "$TMP/occupied" "$TMP/refusal"
cp "$TMP/projects/response-policy.json" "$TMP/occupied/response-policy.json"
jq '.rules |= map(.base=(if .label=="decline" then 1000 elif .label=="defer" then 1000 else 0 end)|.influences=[])' "$TMP/science/response-policy.json" > "$TMP/refusal/response-policy.json"
printf '1\n42\n1\n1\n3\n1\n5\n0\n' | "$TMP/bin/crew-play-offline" --home "$TMP/occupied" > "$TMP/occupied.out"
printf '1\n42\n1\n1\n5\n0\n' | "$TMP/bin/crew-play-offline" --home "$TMP/refusal" > "$TMP/refusal.out"
for path in occupied refusal; do
 journals=("$TMP/$path"/runs/*/journal.jsonl)
 jq -s -e 'last.payload.kind=="quit" and any(.[]; ((.payload.host_output? // "")|startswith("{\"error\"")))' "${journals[0]}" > /dev/null
done
# Compare the accepted host snapshot immediately around the rejected start.
# The following advance commits tick movement but none of the attempted start.
journals=("$TMP/shortage"/runs/*/journal.jsonl)
jq -s -e '[.[]|select(.payload.host_output!=null)] as $xs | [range(1;($xs|length)-1)|select(($xs[.].payload.host_output|fromjson|has("error")))] | all(.[]; . as $i | ($xs[$i-1].payload.host_output|fromjson).state.resources == ($xs[$i+1].payload.host_output|fromjson).state.resources and $xs[$i].payload.seed_before==$xs[$i].payload.seed_after)' "${journals[0]}" > /dev/null
# Recovery journals include rejected commands; the old run.sh remains fail-fast.
for path in shortage occupied refusal; do
 journals=("$TMP/$path"/runs/*/journal.jsonl)
 journal=${journals[0]}
 jq -r 'select(.payload.host_input != null)|.payload.host_input' "$journal" > "$TMP/$path-input.ndjson"
 jq -r 'select(.payload.host_output != null)|.payload.host_output' "$journal" > "$TMP/$path-expected.ndjson"
 jq -Rs 'split("\n")|map(select(length>0))' "$TMP/$path-input.ndjson" > "$TMP/$path-args.json"
 "$AILANG" run --package-dir "$EX" --entry recoveryRecording --args-file "$TMP/$path-args.json" "$EX/play_flow.ail" > "$TMP/$path-replay.ndjson"
 "$AILANG" run --bytecode --strict-bytecode --package-dir "$EX" --entry recoveryRecording --args-file "$TMP/$path-args.json" "$EX/play_flow.ail" > "$TMP/$path-vm.ndjson"
 cmp "$TMP/$path-expected.ndjson" "$TMP/$path-replay.ndjson"
 cmp "$TMP/$path-expected.ndjson" "$TMP/$path-vm.ndjson"
done
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
if rg -q '^scientist:|^Crew reaction \(narrator\):' "$TMP/failure.out"; then printf 'Dialogue exposed before failed journal publication\n' >&2; exit 1; fi
if [[ -n "${EVIDENCE_DIR:-}" ]]; then
 mkdir -p "$EVIDENCE_DIR"
 for path in newcomer shortage occupied refusal; do
  # Paths/owners are run-specific; preserve all actual game output otherwise.
  sed "s|$TMP|<temporary-home>|g" "$TMP/$path.out" > "$EVIDENCE_DIR/$path-transcript.txt"
 done
fi
# Installed argument boundary is independent of cwd and has no secret/network access.
if "$TMP/bin/crew-play-offline" --wat > "$TMP/args.out" 2>&1; then exit 1; fi
printf 'Guided offline UI: science/care/denial/material competition/shortage/occupancy/refusal/help, extracted replay + strict VM, zero calls, journal rollback and arguments pass\n'
