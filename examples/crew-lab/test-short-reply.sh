#!/usr/bin/env bash
# Acceptance harness only. Pure AILANG owns selection, prompts, cache and host.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-short-reply.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" > "$TMP/install.txt"
printf '1\n1\n1\n2\n' | "$TMP/bin/crew-watch-offline" --mode plain --home "$TMP/bootstrap" --seed 42 > "$TMP/bootstrap.out"
journal=("$TMP/bootstrap"/runs/*/journal.jsonl)
jq -s '[.[]|.payload.metadata.selection // empty]|first' "${journal[0]}" > "$TMP/selection.json"
jq '.bundle + {schema:"content_bundle/1",promptVersion:"crew-dialogue-v1"}' "$TMP/selection.json" > "$TMP/old-bundle.json"
BASE=$(jq -r '.bundle.signature' "$TMP/selection.json")
LABEL=$(jq -r '.selected_label' "$TMP/selection.json")
OLD_KEY=$(jq -r '.bundle.key' "$TMP/selection.json")
jq -s --argjson seed 42 '{request:([.[]|select(.payload.host_output!=null)|.payload.host_output|fromjson|.host.pending[]?]|last|{id,actor,task,tick,revision,expires,threshold,legal,context:.perception,body:.request_body,configBody:.config_body,policyId:.policy_id}),policy:.[0].payload.policy_body,seed:$seed}' "${journal[0]}" > "$TMP/request.json"
"$AILANG" run --package-dir "$EX" --caps IO --entry shortRequestProbe --args-file "$TMP/request.json" "$EX/store_probe.ail" > "$TMP/inspection.json"
test "$(jq -r .label "$TMP/inspection.json")" = "$LABEL"
test "$(jq -r .base "$TMP/inspection.json")" = "$BASE"
jq -r '.prompt' "$TMP/inspection.json" > "$TMP/prompt.txt"
jq -n --rawfile prompt "$TMP/prompt.txt" --arg label "$LABEL" '{version:1,fixtures:[{kind:"text",prompt:($prompt|rtrimstr("\n")),response:({schema:"generated_dialogue/1",variants:[{id:"a",label:$label,text:"I can take that on. Let us keep the scope clear.",weight:1},{id:"b",label:$label,text:"Agreed. I want us to check the readings carefully.",weight:1}]}|tojson)}]}' > "$TMP/valid.json"
printf '%s\n' '{"version":1,"fixtures":[]}' > "$TMP/empty.json"
probe() {
 local home=$1 label=$2 mode=$3 budget=$4 fixture=$5
 jq -n --arg h "$TMP/$home" --arg s "$BASE" --arg l "$label" --arg mode "$mode" --argjson n "$budget" '{home:$h,signature:$s,legal:["accept","decline","concern","defer"],label:$l,mode:$mode,remaining:$n}' > "$TMP/args.json"
 "$AILANG" run --package-dir "$EX" --caps IO,FS,AI --ai-stub --ai-stub-fixtures "$fixture" --entry chosenProbe --args-file "$TMP/args.json" "$EX/store_probe.ail"
}
# Miss generates only two selected-label variants; repeat cannot call provider.
probe fresh "$LABEL" live 1 "$TMP/valid.json" > "$TMP/first.json"
jq -e '.ok and .source=="generated" and .calls==1 and (.body|fromjson|(.variants|length)==2)' "$TMP/first.json" >/dev/null
KEY=$(jq -r '.body|fromjson|.key' "$TMP/first.json")
test "$KEY" != "$OLD_KEY"
test ! -e "$TMP/fresh/cache/$KEY.lock"
cp "$TMP/fresh/cache/$KEY.json" "$TMP/saved-short.json"
probe fresh "$LABEL" live 0 "$TMP/empty.json" > "$TMP/hit.json"
jq -e '.ok and .source=="cache" and .calls==0' "$TMP/hit.json" >/dev/null
cmp "$TMP/saved-short.json" "$TMP/fresh/cache/$KEY.json"
probe budget "$LABEL" live 0 "$TMP/empty.json" > "$TMP/budget.json"
jq -e '(.ok|not) and .calls==0 and (.body|contains("limit"))' "$TMP/budget.json" >/dev/null
probe offline "$LABEL" offline 0 "$TMP/empty.json" > "$TMP/offline.json"
jq -e '.ok and .source=="authored" and .calls==0 and (.body|fromjson|(.variants|length)==4)' "$TMP/offline.json" >/dev/null
# Complete prior bundles are preferred verbatim. Corruption is not regenerated.
mkdir -p "$TMP/old/cache"
cp "$TMP/old-bundle.json" "$TMP/old/cache/$OLD_KEY.json"
probe old "$LABEL" live 0 "$TMP/empty.json" > "$TMP/old.json"
jq -e '.ok and .source=="cache" and .calls==0' "$TMP/old.json" >/dev/null
jq -S '.body|fromjson' "$TMP/old.json" > "$TMP/read-old.json"
jq -S . "$TMP/old-bundle.json" > "$TMP/expected-old.json"
cmp "$TMP/read-old.json" "$TMP/expected-old.json"
printf '{}\n' > "$TMP/old/cache/$OLD_KEY.json"
probe old "$LABEL" live 1 "$TMP/valid.json" > "$TMP/old-corrupt.json"
jq -e '(.ok|not) and .calls==0 and (.body|contains("cached"))' "$TMP/old-corrupt.json" >/dev/null
# A valid legacy signature at its size boundary must not need a short wrapper.
SAVED_BASE=$BASE
BASE=$(python3 - "$BASE" <<'PY'
import json,sys
base=json.loads(sys.argv[1]);base['policy']=''
raw=json.dumps(base,separators=(',',':'),ensure_ascii=False)
base['policy']='x'*(32768-len(raw))
raw=json.dumps(base,separators=(',',':'),ensure_ascii=False)
assert len(raw)==32768
print(raw)
PY
)
probe boundary "$LABEL" offline 0 "$TMP/empty.json" > "$TMP/boundary-offline.json"
jq -e '.ok and .source=="authored" and .calls==0' "$TMP/boundary-offline.json" >/dev/null
BOUNDARY_KEY=$(jq -r '.body|fromjson|.key' "$TMP/boundary-offline.json")
jq -r '.body' "$TMP/boundary-offline.json" > "$TMP/boundary/cache/$BOUNDARY_KEY.json"
probe boundary "$LABEL" live 0 "$TMP/empty.json" > "$TMP/boundary-hit.json"
jq -e '.ok and .source=="cache" and .calls==0' "$TMP/boundary-hit.json" >/dev/null
BASE=$SAVED_BASE
# Every malformed output costs one attempt but is never cached; each lock clears.
for kind in malformed one three long label weights disclosure; do
 case "$kind" in
 malformed) jq '.fixtures[0].response="```json\n{}\n```"' "$TMP/valid.json" > "$TMP/bad.json" ;;
 one) jq '.fixtures[0].response |= (fromjson|.variants=.variants[:1]|tojson)' "$TMP/valid.json" > "$TMP/bad.json" ;;
 three) jq '.fixtures[0].response |= (fromjson|.variants += [(.variants[0]|.id="c")]|tojson)' "$TMP/valid.json" > "$TMP/bad.json" ;;
 long) jq '.fixtures[0].response |= (fromjson|.variants[0].text=([range(241)|"x"]|join(""))|tojson)' "$TMP/valid.json" > "$TMP/bad.json" ;;
 label) jq '.fixtures[0].response |= (fromjson|.variants[0].label="invented"|tojson)' "$TMP/valid.json" > "$TMP/bad.json" ;;
 weights) jq '.fixtures[0].response |= (fromjson|.variants[0].weight=2|tojson)' "$TMP/valid.json" > "$TMP/bad.json" ;;
 disclosure) jq '.fixtures[0].response |= (fromjson|.variants[0].text="My openness is high."|tojson)' "$TMP/valid.json" > "$TMP/bad.json" ;;
 esac
 probe "$kind" "$LABEL" live 1 "$TMP/bad.json" > "$TMP/$kind.json"
 jq -e '(.ok|not) and .calls==1 and .usage_known' "$TMP/$kind.json" >/dev/null
 test ! -e "$TMP/$kind/cache/$KEY.json"
 test ! -e "$TMP/$kind/cache/$KEY.lock"
done
# Tampered saved short bounds/disclosures also fail without a provider attempt.
for kind in cached-long cached-disclosure cached-model; do
 mkdir -p "$TMP/$kind/cache"
 case "$kind" in
 cached-long) jq '.variants[0].text=([range(241)|"x"]|join(""))' "$TMP/saved-short.json" > "$TMP/$kind/cache/$KEY.json" ;;
 cached-disclosure) jq '.variants[0].text="My fatigue: 45"' "$TMP/saved-short.json" > "$TMP/$kind/cache/$KEY.json" ;;
 cached-model) jq '.model="wrong-model"' "$TMP/saved-short.json" > "$TMP/$kind/cache/$KEY.json" ;;
 esac
 probe "$kind" "$LABEL" live 1 "$TMP/empty.json" > "$TMP/$kind.json"
 jq -e '(.ok|not) and .calls==0' "$TMP/$kind.json" >/dev/null
done
# Generated [bin] fixtures use the actual live entrypoints. Since 0.6.0 the watch
# never calls a provider itself: its crew-reply-worker copy has an explicit stub
# provider in this test-only manifest. No live credentials or fake keys.
cp -R "$EX" "$TMP/app"
python3 - "$TMP/app/ailang.toml" "$EX" "$TMP/valid.json" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);s=p.read_text()
for dep in ('terminal-ui','social-dynamics','content-library','crew-core'):
 s=s.replace(f'path = "../../packages/{dep}"',f'path = "{pathlib.Path(sys.argv[2]).parents[1]}/packages/{dep}"')
old='crew-reply-worker = {module = "reply_worker", entry = "main", caps = "FS,Env,AI", run_flags = ["--ai", "z-ai/glm-5.3-flash", "--fs-max-bytes", "16MB"]}'
assert old in s
s=s.replace(old,f'crew-reply-worker = {{module = "reply_worker", entry = "main", caps = "FS,Env,AI", run_flags = ["--ai-stub", "--ai-stub-fixtures", "{sys.argv[3]}", "--fs-max-bytes", "16MB"]}}')
p.write_text(s)
PY
(cd "$TMP/app" && "$AILANG" lock >/dev/null)
"$AILANG" install --path "$TMP/app" --bin-dir "$TMP/fixture-bin" >/dev/null
FIX_PATH="$TMP/fixture-bin:/usr/bin:/bin"
# play HOME OUT: offer the scientist, wait for the background words, then Decide later.
play() {
 { printf '1\n1\n1\n'; n=0; until ls "$TMP/$1"/runs/*/replies/job-1.json.result >/dev/null 2>&1; do n=$((n+1)); [ $n -lt 600 ] || break; sleep 0.1; done; printf '\n2\n'; } | PATH="$FIX_PATH" "$TMP/fixture-bin/crew-watch" --mode plain --prefetch 0 --home "$TMP/$1" --seed 42 > "$2"
}
domain() { jq -sc '[.[].payload|select(.kind=="host")|{host_input,host_output,seed_before,seed_after}]' "$1"; }
# Pass 1: the decision commits at once with the authored line (identical domain
# records to the offline baseline); the selected-reaction words arrive in the
# background as a transport-only wording record charged one attempt.
play installed "$TMP/installed-1.out"
first=("$TMP/installed"/runs/*/journal.jsonl)
test "$(domain "${first[0]}")" = "$(domain "${journal[0]}")"
jq -s -e '([.[]|select(.payload.host_input!=null)|.payload.host_input|fromjson|select(.command=="answer")]|length)==1 and any(.[];.payload.metadata.usage.source=="deferred") and ([.[].payload|select(.kind=="wording")] as $w | ($w|length)==1 and $w[0].usage.calls==1 and ($w[0].text|test("I can take that on|Agreed. I want us")))' "${first[0]}" >/dev/null
rg -q 'Replies: 0 preparing, 1 new' "$TMP/installed-1.out"
cp "${first[0]}" "$TMP/first.jsonl"
# Pass 2: the saved short reply is used inline with no job and no call.
printf '1\n1\n1\n2\n' | PATH="$FIX_PATH" "$TMP/fixture-bin/crew-watch" --mode plain --prefetch 0 --home "$TMP/installed" --seed 42 > "$TMP/installed-2.out"
journals=("$TMP/installed"/runs/*/journal.jsonl)
test "${#journals[@]}" = 2
for j in "${journals[@]}"; do
 test "$(domain "$j")" = "$(domain "${journal[0]}")"
 jq -r 'select(.payload.host_input!=null)|.payload.host_input' "$j" > "$TMP/commands.jsonl"
 for engine in interpreter vm; do AILANG="$AILANG" "$EX/run.sh" "$engine" "$TMP/commands.jsonl" > "$TMP/replay-$engine.jsonl"; done
 cmp "$TMP/replay-interpreter.jsonl" "$TMP/replay-vm.jsonl"
 jq -s -e 'last.state.tick==0 and all(last.state.tasks[];.status=="offered") and all(last.state.resources[];.reserved==0)' "$TMP/replay-interpreter.jsonl" >/dev/null
 if ! cmp -s "$j" "$TMP/first.jsonl"; then
  jq -s -e 'any(.[];.payload.metadata.selection.bundle.signature|fromjson?|.generationProfile=="crew-reply-short-v1") and all(.[]|select(.payload.metadata.selection!=null);.payload.metadata.selection.selected_label=="accept" and (.payload.metadata.selection.bundle.variants|length)==2) and ([.[].payload|select(.kind=="wording")]|length)==0' "$j" >/dev/null
 fi
done
jq -s -e '[.[]|(.payload.metadata.usage // .payload.usage // empty)|.calls]|add==1' "${journals[@]}" >/dev/null
rg -q 'I can take that on|Agreed. I want us' "$TMP/installed-2.out"
# Rejected personal words: the decision (authored) and seed are unchanged, one
# attempt is charged, nothing is cached and Replies explains.
jq '.fixtures[0].response="not JSON"' "$TMP/valid.json" > "$TMP/rejected.json"
cp "$TMP/rejected.json" "$TMP/valid.json"
play recovery "$TMP/recovery.out"
recovery=("$TMP/recovery"/runs/*/journal.jsonl)
test "$(domain "${recovery[0]}")" = "$(domain "${journal[0]}")"
jq -s -e '([.[]|select(.payload.kind=="library_error")]|length)==0 and ([.[].payload|select(.kind=="wording")] as $w | ($w|length)==1 and $w[0].usage.calls==1 and ($w[0].error|startswith("AI output rejected")) and $w[0].seed==$w[0].seed)' "${recovery[0]}" >/dev/null
test ! -e "$TMP/recovery/cache/$KEY.json"
jq -r 'select(.payload.host_input!=null)|.payload.host_input' "${recovery[0]}" > "$TMP/commands.jsonl"
for engine in interpreter vm; do AILANG="$AILANG" "$EX/run.sh" "$engine" "$TMP/commands.jsonl" > "$TMP/recovery-$engine.jsonl"; done
cmp "$TMP/recovery-interpreter.jsonl" "$TMP/recovery-vm.jsonl"
printf 'Short replies: old cache preserved; selected miss/hit; bounded output/disclosure/budget rejection; installed live fixture and both-engine replay passed (provider calls0).\n'
