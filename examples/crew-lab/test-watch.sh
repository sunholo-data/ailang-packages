#!/usr/bin/env bash
# Hermetic installed controls; product logic and UI remain AILANG.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
LAB_TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-watch.XXXXXX")
trap 'rm -rf "$LAB_TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$LAB_TMP/bin" >/dev/null
cd "$LAB_TMP"
mkdir -p bootstrap
printf '1\n0\n' | "$LAB_TMP/bin/crew-journey-offline" --plain --home "$LAB_TMP/bootstrap" > bootstrap.txt
jq '.rules |= map(.base=(if .label=="accept" or .label=="request_relief" then 1000 else 0 end)|.influences=[])' bootstrap/response-policy-watch-v2.json > accept.json
prepare() { mkdir -p "$LAB_TMP/$1"; cp accept.json "$LAB_TMP/$1/response-policy-watch-v2.json"; }
run_flow() {
 local name=$1 input=$2
 shift 2
 prepare "$name"
 if ! printf '%b' "$input" | "$LAB_TMP/bin/crew-journey-offline" --plain --home "$LAB_TMP/$name" "$@" > "$name.txt"; then tail -30 "$name.txt"; return 1; fi
}
# Introduction and help before state exists, at actual minimum dimensions.
printf 'h\nn\nb\n0\n' | "$LAB_TMP/bin/crew-journey-offline" --plain --columns 40 --rows 16 --home "$LAB_TMP/unstarted" > intro-40x16.txt
test ! -e unstarted
rg -q 'You are captain' intro-40x16.txt
rg -q 'first contact' intro-40x16.txt
rg -q 'Start despite refusal; trust can fall' intro-40x16.txt
rg -q 'Example' intro-40x16.txt
# Newcomer proposal choices are explained on the real minimum frame. Reading,
# deciding later, reviewing and the old0 alias keep the answer/offer unchanged.
run_flow decide_later_40 '1\n1\n1\nc\nb\nn\nn\nn\nn\nn\nn\nn\nn\nv\n2\n7\n1\n0\n0\n' --columns 40 --rows 16
run_flow decide_back_80 '1\n1\n1\n0\n0\n' --columns 80 --rows 24
rg -q 'has agreed' decide_later_40.txt
rg -q '1 Start now: assign \+ hold resources' decide_later_40.txt
rg -q '2 Decide later: keep offer, no costs' decide_later_40.txt
rg -q '0 Also leaves it open' decide_later_40.txt
rg -q 'b Decision' decide_later_40.txt
rg -q 'Starting does not pass time' decide_later_40.txt
for sample in decide_later_40 decide_back_80; do
 decision_journal=("$LAB_TMP/$sample"/runs/*/journal.jsonl)
 jq -s 'map(select(.payload.kind=="host")|.payload)' "${decision_journal[0]}" > "$sample-payload.json"
 jq -sr 'map(select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null))|last.state' "${decision_journal[0]}" > "$sample-state.json"
 jq -e '.tick==0 and all(.tasks[];.status=="offered") and all(.resources[];.reserved==0 and .consumed==0) and any(.commitments[];any(.accepted[];.=="scientist"))' "$sample-state.json" >/dev/null
done
cmp decide_later_40-payload.json decide_back_80-payload.json
# Scientist + engineer use all compute; pilot offer cannot start until capacity returns.
FLOW='1\n1\n1\n1\n1\n2\n1\n1\n4\n1\n5\n5\n5\n5\n1\n3\n1\n1\n5\n1\n5\n5\n5\nc\nn\nv\nw\nn\nj\nh\nn\nb\n0\n'
run_flow journey "$FLOW" --columns 80 --rows 24
rg -q 'Not enough available Archive compute slots' journey.txt
rg -q 'Prepare diagnostic supplies' journey.txt
rg -q 'Rehearse first-contact signals' journey.txt
rg -q 'Crew reaction \(narrator\)' journey.txt
# Normal surfaces and recap may show inventory/progress, never psychological scores/traits.
if rg -in 'OCEAN|openness|conscientiousness|extraversion|agreeableness|neuroticism|hidden (variable|score|stat)|fatigue[: ]+[0-9]|stress[: ]+[0-9]|morale[: ]+[0-9]|trust[: ]+[0-9]|readiness[: ]+[0-9]|observations[: ]+[0-9]' journey.txt; then exit 1; fi
journal=("$LAB_TMP/journey"/runs/*/journal.jsonl)
jq -s -e 'all(.[]|select(.payload.metadata.usage!=null);.payload.metadata.usage.calls==0)' "${journal[0]}" >/dev/null
jq -r 'select(.payload.host_input!=null)|.payload.host_input' "${journal[0]}" > inputs.ndjson
jq -r 'select(.payload.host_output!=null)|.payload.host_output' "${journal[0]}" > expected.ndjson
jq -Rs 'split("\n")|map(select(length>0))' inputs.ndjson > inputs.json
for engine in interpreter vm; do
 flags=(); if [[ "$engine" == vm ]]; then flags=(--bytecode --strict-bytecode); fi
 "$AILANG" run ${flags[@]+"${flags[@]}"} --package-dir "$EX" --entry recoveryRecording --args-file inputs.json "$EX/play_flow.ail" > "$engine.ndjson"
 cmp expected.ndjson "$engine.ndjson"
done
jq -r 'select(.payload.host_output!=null)|.payload.host_output' "${journal[0]}" | tail -1 | jq -e '.state.resources|any(.id=="archive_compute" and .reserved==0 and .consumed==0)' >/dev/null
# Installed repeated rest/work reaches bounds and continues, without stranded capacity.
REST_LIMITS='2\n'
for turn in 1 2 3 4; do REST_LIMITS+='2\n1\n1\n5\n5\n'; done
run_flow rest_limits "${REST_LIMITS}0\n" --columns 80 --rows 24
WORK_LIMITS='2\n'
for turn in 1 2 3 4 5; do WORK_LIMITS+='1\n4\n1\n5\n5\n'; done
run_flow work_limits "${WORK_LIMITS}0\n" --columns 80 --rows 24
for sample in rest_limits work_limits; do
 limit_journal=("$LAB_TMP/$sample"/runs/*/journal.jsonl)
 jq -sr 'map(select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null))|last.state' "${limit_journal[0]}" > "$sample-state.json"
 jq -e 'all(.tasks[];.status=="completed") and all(.resources[];.reserved==0 and .consumed==0)' "$sample-state.json" >/dev/null
done
jq -e '.tick==8 and (.tasks|length)==4 and any(.actors[];.id=="scientist" and any(.indicators[];.id=="fatigue" and .value==0))' rest_limits-state.json >/dev/null
jq -e '.tick==10 and (.tasks|length)==5 and any(.actors[];.id=="pilot" and all(.indicators[]|select(.id=="fatigue" or .id=="readiness");.value==100))' work_limits-state.json >/dev/null
# Reading/paging around a pending Start changes no host payload, seed, selection or AI count.
run_flow nav_base '1\n1\n1\n1\n5\n0\n'
run_flow nav_reads '1\n1\n1\nc\nn\nv\nw\nj\nh\nn\nb\n1\n5\nc\nn\nb\n0\n'
for sample in nav_base nav_reads; do
 nav_journal=("$LAB_TMP/$sample"/runs/*/journal.jsonl)
 jq -s 'map(select(.payload.kind=="host")|.payload)' "${nav_journal[0]}" > "$sample-payload.json"
done
if ! cmp nav_base-payload.json nav_reads-payload.json; then diff -u nav_base-payload.json nav_reads-payload.json | tail -35; exit 1; fi
# An installed working engineer can request relief; grant returns slots and unspent module.
run_flow relief '2\n1\n2\n1\n6\n1\n8\n1\n1\n0\n'
relief_journal=("$LAB_TMP/relief"/runs/*/journal.jsonl)
jq -sr 'map(select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null))|last.state' "${relief_journal[0]}" > relief-state.json
jq -e 'all(.tasks[];.status=="stopped") and all(.resources[];.reserved==0 and .consumed==0) and any(.resources[];.id=="archive_compute" and .available==3) and any(.resources[];.id=="replacement_modules" and .available==3)' relief-state.json >/dev/null
# Refusal is a meaningful choice under each command style on the installed modern profile.
for style in consent orders; do
 prepare "decline_$style"
 jq '.rules |= map(.base=(if .label=="decline" then 1000 else 0 end)|.influences=[])' accept.json > "decline_$style/response-policy-watch-v2.json"
 choice=1; if [[ "$style" == orders ]]; then choice=2; fi
 printf '%b' "${choice}\n1\n1\n1\n0\n" | "$LAB_TMP/bin/crew-journey-offline" --plain --home "$LAB_TMP/decline_$style" --seed 10001 > "decline_$style.txt"
 decline_journal=("$LAB_TMP/decline_$style"/runs/*/journal.jsonl)
 jq -sr 'map(select(.payload.host_output!=null)|.payload.host_output|fromjson|select(.state!=null))|last.state' "${decline_journal[0]}" > "$style-decline-state.json"
done
jq -e 'all(.tasks[];.status=="offered") and all(.resources[];.reserved==0)' consent-decline-state.json >/dev/null
jq -e 'all(.tasks[];.status=="working") and any(.relationships[];.from=="scientist" and .to=="captain" and .value<50)' orders-decline-state.json >/dev/null
run_flow debug '1\nc\nn\nn\nn\nn\n0\n' --debug --columns 80 --rows 60
rg -q 'OCEAN' debug.txt
rg -q 'stress 65' debug.txt
rg -q 'diplomat' debug.txt
# Exact cached AI words and rejected cached disclosure keep request pending, no provider calls.
source_bundle=$(jq -sc 'map(select(.payload.metadata.selection.bundle!=null)|.payload.metadata.selection.bundle)|first' "${journal[0]}")
key=$(printf '%s' "$source_bundle" | jq -r .key)
for label in ai leaking; do
 prepare "$label";mkdir -p "$label/cache"
 wording='I am tired, but I want to understand these readings.'
 if [[ "$label" == leaking ]]; then wording='fatigue is real; my fatigue: 45'; fi
 printf '%s' "$source_bundle" | jq --arg t "$wording" '.origin="ai"|.model="z-ai/glm-5.3-flash"|.variants|=map(.text=$t)' > "$label/cache/$key.json"
 printf '1\n1\n1\n2\n0\n' | "$LAB_TMP/bin/crew-journey-offline" --plain --home "$LAB_TMP/$label" > "$label.txt"
done
rg -q 'scientist: I am tired, but I want to understand' ai.txt
rg -q 'Reply pending|CREW REPLY PENDING' leaking.txt
if rg -q 'my fatigue: 45|development metrics|hidden variables' leaking.txt; then exit 1; fi
rg -q 'The reply could not be used' leaking.txt
# Modern policy leaves unrelated legacy user policy and cache bytes untouched.
prepare isolation
printf 'legacy policy sentinel\n' > isolation/response-policy.json
mkdir -p isolation/cache;printf 'legacy cache sentinel\n' > isolation/cache/legacy.json
cp isolation/response-policy.json policy-before.txt;cp isolation/cache/legacy.json cache-before.txt
printf '1\n0\n' | "$LAB_TMP/bin/crew-journey-offline" --plain --home "$LAB_TMP/isolation" > isolation.txt
cmp policy-before.txt isolation/response-policy.json;cmp cache-before.txt isolation/cache/legacy.json
# Effectful store publication guard: rejected generated disclosures spend one stub call, never cache.
sig=$(printf '%s' "$source_bundle" | jq -r .signature)
arg=$(jq -nc --arg s "$sig" '$s')
"$AILANG" run --package-dir "$EX" --caps IO --entry promptProbe --args-json "$arg" "$EX/store_probe.ail" > prompt.txt
jq -n --rawfile p prompt.txt '{version:1,fixtures:[{kind:"text",prompt:($p|rtrimstr("\n")),response:({schema:"generated_dialogue/1",variants:(["accept","decline","concern","defer"]|map({id:.,label:.,text:"Stress: 85",weight:1}))}|tojson)}]}' > disclosures.json
arg=$(jq -nc --arg h "$LAB_TMP/generated-reject" --arg s "$sig" '{home:$h,signature:$s,mode:"live",remaining:6}')
"$AILANG" run --package-dir "$EX" --caps IO,FS,AI --ai-stub --ai-stub-fixtures disclosures.json --entry cacheProbe --args-json "$arg" "$EX/store_probe.ail" > reject.json
jq -e '(.ok|not) and .calls==1 and (.body|contains("development metrics"))' reject.json >/dev/null
test ! -e "generated-reject/cache/$key.json"
if [[ -n "${EVIDENCE_DIR:-}" ]]; then
 mkdir -p "$EVIDENCE_DIR"
 for item in intro-40x16 decide_later_40 decide_back_80 journey rest_limits work_limits relief debug ai leaking; do sed "s|$LAB_TMP|<temporary-home>|g" "$item.txt" > "$EVIDENCE_DIR/$item.txt"; done
 cp reject.json "$EVIDENCE_DIR/generated-disclosure.json"
fi
printf 'Watch: installed intro/help, five-role resource contention/completion, normal/debug views, cache guard/isolation and both-engine exact recovery passed; provider calls0 (one deterministic AI stub attempt).\n'
