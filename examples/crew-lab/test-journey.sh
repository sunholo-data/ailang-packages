#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-journey.XXXXXX")
PLAY_PID=""
trap 'if [[ -n "$PLAY_PID" ]]; then kill "$PLAY_PID" 2>/dev/null || true; fi; rm -rf "$TMP"' EXIT
"$AILANG" install --path "$ROOT/packages/terminal-ui" --bin-dir "$TMP/bin"
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin"
cd "$TMP"
printf 'n\nh\na\n0\n' | "$TMP/bin/terminal-ui-demo" > "$TMP/demo.out"
rg -q 'Demo ended' "$TMP/demo.out"
# Bootstrap existing default policy without playing; all providers stubbed.
printf '1\n0\n' | "$TMP/bin/crew-play-offline" --home "$TMP/policy" --seed 42 > /dev/null
for flow in science care deny projects shortage occupied refusal; do
 for kind in baseline journey; do
  home="$TMP/$flow-$kind"
  mkdir -p "$home"
  if [[ "$flow" == science ]]; then cp "$TMP/policy/response-policy.json" "$home/response-policy.json";
  elif [[ "$flow" == refusal ]]; then
   jq '.rules |= map(.base=(if .label=="decline" then 1000 else 0 end)|.influences=[])' "$TMP/policy/response-policy.json" > "$home/response-policy.json"
  else
   jq '.rules |= map(.base=(if .label=="accept" or .label=="request_relief" then 1000 else 0 end)|.influences=[])' "$TMP/policy/response-policy.json" > "$home/response-policy.json"
  fi
 done
 if [[ "$flow" == occupied ]];then printf '1\n1\n1\n3\n1\n5\n0\n' > "$TMP/$flow.menu";elif [[ "$flow" == refusal ]];then printf '1\n1\n1\n5\n0\n' > "$TMP/$flow.menu";else awk 'NR!=2' "$EX/recordings/play-$flow.menu" > "$TMP/$flow.menu";fi
 # Every view/page visit preserves the current host decision and journal payload.
 awk '{print; if ($0!="0") {print "c"; print "w"; print "j"; print "h"; print "n"; print "v"; print "b"; print "n"; print "v"}}' "$TMP/$flow.menu" > "$TMP/$flow-nav.menu"
 "$TMP/bin/crew-play-offline" --home "$TMP/$flow-baseline" --seed 42 < "$TMP/$flow.menu" > "$TMP/$flow-baseline.out"
 "$TMP/bin/crew-journey-offline" --legacy --debug --home "$TMP/$flow-journey" --plain --columns 60 --rows 24 < "$TMP/$flow-nav.menu" > "$TMP/$flow-journey.out"
 old=("$TMP/$flow-baseline"/runs/*/journal.jsonl); new=("$TMP/$flow-journey"/runs/*/journal.jsonl)
 jq -s 'map(.payload)' "${old[0]}" > "$TMP/before.json"
 jq -s 'map(.payload)' "${new[0]}" > "$TMP/after.json"
 cmp "$TMP/before.json" "$TMP/after.json"
 jq -s -e 'all(.[] | select(.payload.metadata.usage!=null);.payload.metadata.usage.calls==0)' "${new[0]}" > /dev/null
 jq -r 'select(.payload.host_input!=null)|.payload.host_input' "${new[0]}" > "$TMP/host.ndjson"
 jq -r 'select(.payload.host_output!=null)|.payload.host_output' "${new[0]}" > "$TMP/expected.ndjson"
 jq -Rs 'split("\n")|map(select(length>0))' "$TMP/host.ndjson" > "$TMP/host-args.json"
 "$AILANG" run --package-dir "$EX" --entry recoveryRecording --args-file "$TMP/host-args.json" "$EX/play_flow.ail" > "$TMP/interpreter.ndjson"
 "$AILANG" run --bytecode --strict-bytecode --package-dir "$EX" --entry recoveryRecording --args-file "$TMP/host-args.json" "$EX/play_flow.ail" > "$TMP/vm.ndjson"
 cmp "$TMP/expected.ndjson" "$TMP/interpreter.ndjson"
 cmp "$TMP/interpreter.ndjson" "$TMP/vm.ndjson"
 printf 'PASS %s: navigation payloads and both-engine recovery replay\n' "$flow"
 if LC_ALL=C rg -q $'\033' "$TMP/$flow-journey.out"; then printf 'Plain output emitted escape\n' >&2; exit 1; fi
 # Actual printed page text (including empty prompt row) fits 60x24. Quit recap is separate.
 awk '/^VOYAGE|^Stapledon/{frame=1;n=0} frame && /^Choose > / {if(n!=23)bad=1;frame=0} frame {if(length($0)>60)bad=1;n++} END {exit bad}' "$TMP/$flow-journey.out"
 if [[ -n "${EVIDENCE_DIR:-}" ]]; then mkdir -p "$EVIDENCE_DIR";sed "s|$TMP|<temporary-home>|g" "$TMP/$flow-journey.out" > "$EVIDENCE_DIR/$flow-journey.txt";fi
done
rg -q 'scientist observations: 0 -> 25' "$TMP/science-journey.out"
rg -q 'scientist fatigue: 45 -> 70' "$TMP/science-journey.out"
rg -q 'Not enough available materials' "$TMP/shortage-journey.out"
# Eight ticks is factual review, not arrival or failure.
printf '1\n5\n5\n5\n5\n5\n5\n5\n5\n0\n' | "$TMP/bin/crew-journey-offline" --legacy --debug --plain --home "$TMP/marker" > "$TMP/marker.out"
rg -q 'PREPARATION REVIEW' "$TMP/marker.out"
# AI cache fixture: exact selected wording in journal; renderer wraps without rephrasing.
orig=("$TMP/science-baseline"/runs/*/journal.jsonl)
key=$(jq -r 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle.key' "${orig[0]}")
for origin in authored ai; do
 home="$TMP/cached-$origin";mkdir -p "$home/cache"
 cp "$TMP/policy/response-policy.json" "$home/response-policy.json"
 jq --arg origin "$origin" 'select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle|.origin=$origin|if $origin=="ai" then .model="z-ai/glm-5.3-flash"|.inputTokens=17|.outputTokens=9|.variants|=map(.text="I would like to gather observations carefully. This is saved fixture wording.") else . end' "${orig[0]}" > "$home/cache/$key.json"
 printf '1\n1\nn\nv\nc\nb\n0\n' | "$TMP/bin/crew-journey-offline" --legacy --debug --home "$home" --plain > "$TMP/cached-$origin.out"
 journal=("$home"/runs/*/journal.jsonl)
 jq -s -e --arg origin "$origin" 'any(.[];.payload.metadata.usage.source=="cache" and .payload.metadata.usage.calls==0 and .payload.metadata.selection.bundle.origin==$origin)' "${journal[0]}" > /dev/null
 if [[ "$origin" == ai ]]; then rg -q 'Saved AI wording' "$TMP/cached-$origin.out"; rg -q 'scientist: I would like to gather observations carefully' "$TMP/cached-$origin.out";
 else rg -q 'Saved stock wording' "$TMP/cached-$origin.out"; rg -q 'Crew reaction \(narrator\)' "$TMP/cached-$origin.out"; fi
done
# Corrupt matching cache retains pending response across all read-only views.
mkdir -p "$TMP/corrupt/cache"; cp "$TMP/policy/response-policy.json" "$TMP/corrupt/response-policy.json";printf '{}' > "$TMP/corrupt/cache/$key.json"
printf '1\n1\nc\nw\nj\nh\nn\nv\nb\n2\n0\n' | "$TMP/bin/crew-journey-offline" --legacy --debug --home "$TMP/corrupt" --plain > "$TMP/corrupt.out"
rg -q 'Reply pending' "$TMP/corrupt.out"
rg -q 'explicit-authored|Stock wording' "$TMP/corrupt.out"
# Real ANSI frame stream (clear/home only, no alternate buffer or cursor hiding).
printf 'n\n1\n1\n0\n' | "$TMP/bin/crew-journey-offline" --legacy --debug --home "$TMP/ansi" --ansi --columns 80 --rows 28 > "$TMP/ansi.out"
LC_ALL=C rg -q $'\033\[2J' "$TMP/ansi.out"
if LC_ALL=C rg -q $'\033\[\?25|\033\[\?1049' "$TMP/ansi.out";then exit 1;fi
if [[ -n "${EVIDENCE_DIR:-}" ]];then sed "s|$TMP|<temporary-home>|g" "$TMP/ansi.out" > "$EVIDENCE_DIR/ansi-80x28.txt";fi
# Oversized onboarding input is rejected before creating a policy/journal.
head -c 65537 /dev/zero | tr '\000' 'x' > "$TMP/oversized.txt";printf '\n' >> "$TMP/oversized.txt"
if "$TMP/bin/crew-journey-offline" --legacy --debug --home "$TMP/oversized" --plain < "$TMP/oversized.txt" > "$TMP/oversized.out";then exit 1;fi
rg -q 'Onboarding input limit reached' "$TMP/oversized.out"
test ! -e "$TMP/oversized/runs"
# Validate each ANSI frame by its actual trusted clear/home delimiters; input prompt
# owns the last row. Final recap is normal scrollback outside the final frame.
awk -v RS='\033\\[2J\033\\[H' 'NR>1 {gsub(/\033\[[0-9;]*[A-Za-z]/, ""); pos=index($0,"Choose > "); if(pos){s=substr($0,1,pos-1);n=split(s,rows,"\n");if(n!=28)bad=1; for(i=1;i<=n;i++){gsub(/─/,"-",rows[i]);if(length(rows[i])>80)bad=1}; seen++}} END{exit(bad || seen<3)}' "$TMP/ansi.out"
# Journal publication failure remains fatal and no uncommitted reply is exposed.
mkfifo "$TMP/in.fifo";exec 3<> "$TMP/in.fifo"
"$TMP/bin/crew-journey-offline" --legacy --debug --home "$TMP/failure" --plain < "$TMP/in.fifo" > "$TMP/failure.out" 2> "$TMP/failure.err" &
PLAY_PID=$!;printf '1\n' >&3
shopt -s nullglob
for attempt in {1..100};do journals=("$TMP/failure"/runs/*/journal.jsonl);if [[ ${#journals[@]} == 1 ]];then break;fi;sleep 0.05;done
test "${#journals[@]}" == 1;journal=${journals[0]};cp "$journal" "$TMP/prefix.jsonl";mkdir "$journal.tmp";printf '1\n' >&3
set +e;wait "$PLAY_PID";rc=$?;set -e;PLAY_PID="";exec 3>&-
test "$rc" == 1;cmp "$journal" "$TMP/prefix.jsonl"
rg -q 'Journal failed; prior Session and seed retained' "$TMP/failure.out"
if rg -q '^scientist:|^Crew reaction \(narrator\):' "$TMP/failure.out";then exit 1;fi
if "$TMP/bin/crew-journey-offline" --legacy --debug --rows nope > /dev/null 2>&1;then exit 1;fi
printf 'Journey installed: seven navigation/baseline payloads identical, evaluator/strictVM recovery replay, completion deltas, cachedAI/stock, pending error, 8-turn review, plain/ANSI bounds and journal failure; zero provider calls.\n'
