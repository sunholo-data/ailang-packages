#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-native-watch.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" >/dev/null
cd "$TMP"
printf '1\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/bootstrap" --seed 42 >/dev/null
jq '.rules |= map(.base=(if .label=="accept" or .label=="request_relief" then 1000 else 0 end)|.influences=[])' "$TMP/bootstrap/response-policy-watch-v2.json" > "$TMP/accept.json"
prepare() { mkdir -p "$TMP/$1"; cp "$TMP/accept.json" "$TMP/$1/response-policy-watch-v2.json"; }
prepare science
# Installation from an unrelated cwd; every run is offline/provider-free.
printf '1\n1\n1\n1\n5\n5\n5\n5\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/science" --seed 42 > "$TMP/science.out"
rg -q 'scientist agreed|scientist agrees' "$TMP/science.out"
rg -q 'Completed|completed' "$TMP/science.out"
journal=("$TMP/science"/runs/*/journal.jsonl)
jq -s -e 'any(.[];.payload.host_input|fromjson? // {}|.command=="start_task") and any(.[];.payload.host_output|fromjson? // {}|.state.tick==4) and all(.[]|select(.payload.metadata.usage!=null);.payload.metadata.usage.calls==0)' "${journal[0]}" >/dev/null
if LC_ALL=C rg -q $'\033' "$TMP/science.out"; then echo 'plain emitted ESC' >&2; exit 1; fi
# All read-only visits, blank idle, and quit-cancel preserve actual host payloads,
# seed, sequence, dialogue rolls and allowance, not merely an immutable fixture.
prepare navigation
printf 'h\nb\n1\nc\nw\nj\nh\ns\npgdn\npgup\nb\n1\nh\nb\n1\nc\nw\nj\nh\ns\npgdn\npgup\nb\nq\nenter\n\n1\n5\n5\n5\n5\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/navigation" --seed 42 > "$TMP/navigation.out"
nav=("$TMP/navigation"/runs/*/journal.jsonl)
jq -s 'map(.payload)' "${journal[0]}" > "$TMP/base-payload.json"
jq -s 'map(.payload)' "${nav[0]}" > "$TMP/nav-payload.json"
cmp "$TMP/base-payload.json" "$TMP/nav-payload.json"
prepare legacy
printf '1\n1\n1\n1\n5\n5\n5\n5\n0\n' | "$TMP/bin/crew-journey-offline" --plain --home "$TMP/legacy" --seed 42 > "$TMP/legacy.out"
old=("$TMP/legacy"/runs/*/journal.jsonl)
jq -s 'map(.payload)' "${old[0]}" > "$TMP/legacy-payload.json"
cmp "$TMP/base-payload.json" "$TMP/legacy-payload.json"
prepare zero_back
printf '1\n1\n1\n0\n7\n1\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/zero_back" --seed 42 > "$TMP/zero-back.out"
rg -q '0 Return to bridge' "$TMP/zero-back.out"
if rg -q 'END WATCH\?' "$TMP/zero-back.out"; then echo 'literal0 incorrectly opened Quit' >&2; exit 1; fi
zero=("$TMP/zero_back"/runs/*/journal.jsonl)
jq -sr '[.[]|select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null)]|last.state' "${zero[0]}" > "$TMP/zero-state.json"
jq -e '.tick==0 and all(.tasks[];.status=="offered") and all(.resources[];.reserved==0 and .consumed==0)' "$TMP/zero-state.json" >/dev/null
# Compute contention remains on the SAME pilot proposal after both rejected
# Starts. Once other jobs finish it can be selected and started successfully.
prepare shortage
printf '1\n1\n1\n1\n1\n2\n1\n1\n4\nup\n1\n1\n2\n5\n5\n5\n5\n7\n1\n1\n5\n5\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/shortage" --seed 42 > "$TMP/shortage.out"
rg -q 'Cannot Start: Archive compute slots' "$TMP/shortage.out"
rg -q 'Not enough available Archive compute slots' "$TMP/shortage.out"
short=("$TMP/shortage"/runs/*/journal.jsonl)
jq -s -e '[.[]|select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.error.code=="insufficient_resource")]|length==2' "${short[0]}" >/dev/null
jq -s -e '[.[]|select(.payload.host_input!=null)|.payload.host_input|fromjson|select(.command=="start_task" and .task=="project-5")]|length==3' "${short[0]}" >/dev/null
jq -sr '[.[]|select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null)]|last.state' "${short[0]}" > "$TMP/short-state.json"
jq -e '.tick==6 and all(.tasks[];.status=="completed") and all(.resources[];.reserved==0) and any(.resources[];.id=="archive_compute" and .available==3 and .consumed==0)' "$TMP/short-state.json" >/dev/null
prepare relief
printf '1\n1\n2\n1\n6\n1\n8\n1\n1\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/relief" --seed 42 > "$TMP/relief.out"
relief=("$TMP/relief"/runs/*/journal.jsonl)
jq -sr '[.[]|select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null)]|last.state' "${relief[0]}" > "$TMP/relief-state.json"
jq -e '.tick==0 and any(.tasks[];.status=="stopped") and all(.resources[];.reserved==0 and .consumed==0)' "$TMP/relief-state.json" >/dev/null
prepare authority
jq '.rules |= map(.base=(if .label=="decline" or .label=="request_relief" then 1000 else 0 end)|.influences=[])' "$TMP/accept.json" > "$TMP/authority/response-policy-watch-v2.json"
printf '2\n1\n2\n1\n6\n1\n8\n1\n2\n5\n5\n5\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/authority" --seed 10001 > "$TMP/authority.out"
authority=("$TMP/authority"/runs/*/journal.jsonl)
jq -s -e 'any(.[];.payload.metadata.selection.selected_label=="decline") and any(.[];.payload.metadata.selection.selected_label=="request_relief")' "${authority[0]}" >/dev/null
jq -sr '[.[]|select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null)]|last.state' "${authority[0]}" > "$TMP/authority-state.json"
jq -e '.tick==3 and any(.tasks[];.status=="completed") and any(.relationships[];.from=="engineer" and .to=="captain" and .value<50) and all(.reliefs[];.resolved)' "$TMP/authority-state.json" >/dev/null
# Replay every accepted and rejected boundary through both pure engines.
for run in science shortage relief authority; do
 records=("$TMP/$run"/runs/*/journal.jsonl)
 jq -r 'select(.payload.host_input!=null)|.payload.host_input' "${records[0]}" > "$TMP/$run-host.ndjson"
 jq -r 'select(.payload.host_output!=null)|.payload.host_output' "${records[0]}" > "$TMP/$run-expected.ndjson"
 jq -Rs 'split("\n")|map(select(length>0))' "$TMP/$run-host.ndjson" > "$TMP/$run-args.json"
 "$AILANG" run --package-dir "$EX" --entry recoveryRecording --args-file "$TMP/$run-args.json" "$EX/play_flow.ail" > "$TMP/$run-interpreter.ndjson"
 "$AILANG" run --bytecode --strict-bytecode --package-dir "$EX" --entry recoveryRecording --args-file "$TMP/$run-args.json" "$EX/play_flow.ail" > "$TMP/$run-vm.ndjson"
 cmp "$TMP/$run-expected.ndjson" "$TMP/$run-interpreter.ndjson"
 cmp "$TMP/$run-interpreter.ndjson" "$TMP/$run-vm.ndjson"
done
# Valid saved AI wording remains exact in the journal and is wrapped for display.
# Invalid control-bearing library entries remain pending, never executed.
prepare cached
mkdir -p "$TMP/cached/cache"
key=$(jq -r 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle.key' "${journal[0]}")
jq 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle|.origin="ai"|.model="z-ai/glm-5.3-flash"|.variants|=map(.text="I will check the readings. Carefully, then report back.")' "${journal[0]}" > "$TMP/cached/cache/$key.json"
printf '1\n1\n1\npgdn\npgdn\npgdn\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/cached" --seed 42 > "$TMP/cached.out"
cached=("$TMP/cached"/runs/*/journal.jsonl)
jq -s -e 'any(.[];.payload.metadata.selection.dialogue=="I will check the readings. Carefully, then report back." and .payload.metadata.usage.source=="cache" and .payload.metadata.usage.calls==0)' "${cached[0]}" >/dev/null
rg -q 'I will check the readings' "$TMP/cached.out"
if LC_ALL=C rg -q $'\033' "$TMP/cached.out"; then echo 'cache injected terminal control' >&2; exit 1; fi
prepare invalid_cache
mkdir -p "$TMP/invalid_cache/cache"
jq 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle|.origin="ai"|.model="z-ai/glm-5.3-flash"|.variants|=map(.text="Unsafe\u001b[2J reply")' "${journal[0]}" > "$TMP/invalid_cache/cache/$key.json"
printf '1\n1\n1\nj\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/invalid_cache" --seed 42 > "$TMP/invalid_cache.out"
invalid=("$TMP/invalid_cache"/runs/*/journal.jsonl)
jq -s -e 'any(.[];.payload.kind=="library_error" and .payload.usage.calls==0) and all(.[];.payload.metadata.selection==null)' "${invalid[0]}" >/dev/null
rg -q 'The reply could not be used' "$TMP/invalid_cache.out"
if LC_ALL=C rg -q $'\033' "$TMP/invalid_cache.out"; then echo 'invalid cache injected terminal control' >&2; exit 1; fi
# A blank line before onboarding is idle, not EOF; exact EOF creates no run.
printf '\n1\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/blank" --seed 42 > "$TMP/blank.out"
test -d "$TMP/blank/runs"
"$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/eof" --seed 42 </dev/null > "$TMP/eof.out"
test ! -e "$TMP/eof/runs"
printf '1\ns\n' | "$TMP/bin/crew-watch-offline" --mode plain --ascii --home "$TMP/ascii" --seed 42 > "$TMP/ascii.out"
rg -q 'COMMONS' "$TMP/ascii.out"
if rg -q '─|│|╭|╰|█|░' "$TMP/ascii.out"; then echo 'ASCII glyph regression' >&2; exit 1; fi
if [[ -n "${EVIDENCE_DIR:-}" ]]; then mkdir -p "$EVIDENCE_DIR"; for flow in science shortage relief authority cached invalid_cache; do sed "s|$TMP|<temporary-home>|g" "$TMP/$flow.out" > "$EVIDENCE_DIR/$flow-plain.txt"; done; fi
echo 'PASS installed native-watch science/contention/recovery/relief, actual navigation+legacy payload parity, both-engine replay, blank/EOF, ASCII and zero providers'
