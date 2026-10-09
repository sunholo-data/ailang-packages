#!/usr/bin/env bash
# Integration harness only: AILANG owns content, policy and FS operations.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/crew-store.XXXXXX")
trap 'rm -rf "$TEST_ROOT"' EXIT
SIGNATURE='{"situation":"same-personality-same-perception-v1"}'
SIGNATURE_ARG=$(jq -nc --arg s "$SIGNATURE" '$s')
"$AILANG" run --package-dir "$EX" --caps IO --entry promptProbe --args-json "$SIGNATURE_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/prompt.txt"
jq -n --rawfile prompt "$TEST_ROOT/prompt.txt" '{version:1,fixtures:[{kind:"text",prompt:($prompt|rtrimstr("\n")),response:({schema:"generated_dialogue/1",variants:(["accept","decline","concern","defer"]|map({id:.,label:.,text:("Saved fixture response: "+.),weight:1}))}|tojson)}]}' > "$TEST_ROOT/valid-fixtures.json"
printf '%s\n' '{"version":1,"fixtures":[]}' > "$TEST_ROOT/empty-fixtures.json"
run_cache() {
 local home=$1 signature=$2 mode=$3 remaining=$4 fixture=$5
 local arguments
 arguments=$(jq -nc --arg h "$home" --arg s "$signature" --arg m "$mode" --argjson n "$remaining" '{home:$h,signature:$s,mode:$m,remaining:$n}')
 "$AILANG" run --package-dir "$EX" --caps IO,FS,AI --ai-stub --ai-stub-fixtures "$fixture" --entry cacheProbe --args-json "$arguments" "$EX/store_probe.ail"
}
HOME_TEST="$TEST_ROOT/library"
run_cache "$HOME_TEST" "$SIGNATURE" live 2 "$TEST_ROOT/valid-fixtures.json" > "$TEST_ROOT/first.json"
jq -e '.ok and .source=="generated" and .calls==1' "$TEST_ROOT/first.json" >/dev/null
KEY=$(jq -r .key "$TEST_ROOT/first.json")
CACHE_FILE="$HOME_TEST/cache/$KEY.json"
test -f "$CACHE_FILE"
test ! -e "$HOME_TEST/cache/$KEY.lock"
cp "$CACHE_FILE" "$TEST_ROOT/cache-before.json"
# An empty fixture map fails any AI call, proving a hit uses no provider.
run_cache "$HOME_TEST" "$SIGNATURE" live 0 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/second.json"
jq -e '.ok and .source=="cache" and .calls==0 and .input_tokens==0 and .output_tokens==0 and .usage_known' "$TEST_ROOT/second.json" >/dev/null
cmp "$CACHE_FILE" "$TEST_ROOT/cache-before.json"
run_cache "$HOME_TEST" "$SIGNATURE" offline 0 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/offline-hit.json"
jq -e '.ok and .source=="cache" and .calls==0' "$TEST_ROOT/offline-hit.json" >/dev/null
# A changed situation is a miss; the zero budget cannot call AI or silently copy text.
run_cache "$HOME_TEST" '{"situation":"different-history"}' live 0 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/budget.json"
jq -e '(.ok|not) and .calls==0 and (.body|contains("limit"))' "$TEST_ROOT/budget.json" >/dev/null
run_cache "$HOME_TEST" '{"situation":"different-history"}' offline 0 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/authored.json"
jq -e '.ok and .source=="authored" and .calls==0 and (.body|fromjson|.origin)=="authored"' "$TEST_ROOT/authored.json" >/dev/null
# Corrupt bundles and false model metadata are visible, never regenerated.
printf '%s\n' '{}' > "$CACHE_FILE"
run_cache "$HOME_TEST" "$SIGNATURE" live 2 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/corrupt.json"
jq -e '(.ok|not) and .calls==0 and (.body|contains("cached"))' "$TEST_ROOT/corrupt.json" >/dev/null
jq '.model="wrong-model"' "$TEST_ROOT/cache-before.json" > "$CACHE_FILE"
run_cache "$HOME_TEST" "$SIGNATURE" live 2 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/model.json"
jq -e '(.ok|not) and .calls==0 and (.body|contains("model"))' "$TEST_ROOT/model.json" >/dev/null
rm "$CACHE_FILE"
mkdir "$HOME_TEST/cache/$KEY.lock"
run_cache "$HOME_TEST" "$SIGNATURE" live 2 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/busy.json"
jq -e '(.ok|not) and .calls==0 and (.body|contains("busy"))' "$TEST_ROOT/busy.json" >/dev/null
rmdir "$HOME_TEST/cache/$KEY.lock"
# Bad generated output spends one attempt but cannot enter the library.
jq '.fixtures[0].response="{}"' "$TEST_ROOT/valid-fixtures.json" > "$TEST_ROOT/bad-fixtures.json"
run_cache "$HOME_TEST" "$SIGNATURE" live 2 "$TEST_ROOT/bad-fixtures.json" > "$TEST_ROOT/bad.json"
jq -e '(.ok|not) and .calls==1 and .usage_known and (.body|contains("rejected"))' "$TEST_ROOT/bad.json" >/dev/null
test ! -f "$CACHE_FILE"
test ! -e "$HOME_TEST/cache/$KEY.lock"
run_cache "$HOME_TEST" "$SIGNATURE" live 2 "$TEST_ROOT/empty-fixtures.json" > "$TEST_ROOT/unavailable.json"
jq -e '(.ok|not) and .calls==1 and (.usage_known|not)' "$TEST_ROOT/unavailable.json" >/dev/null
test ! -e "$HOME_TEST/cache/$KEY.lock"
# Initial local config is created once. Invalid user edits are not overwritten.
POLICY_ARG=$(jq -nc --arg h "$HOME_TEST" '$h')
"$AILANG" run --package-dir "$EX" --caps IO,FS --entry policyProbe --args-json "$POLICY_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/policy-before.json"
printf '%s\n' '{}' > "$HOME_TEST/response-policy.json"
if "$AILANG" run --package-dir "$EX" --caps IO,FS --entry policyProbe --args-json "$POLICY_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/policy-error.txt"; then exit 1; fi
cmp "$HOME_TEST/response-policy.json" <(printf '%s\n' '{}')
# Atomic whole-journal commit keeps the last accepted prefix on write failure.
"$AILANG" run --package-dir "$EX" --caps IO,FS --entry openProbe --args-json "$POLICY_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/run-path.txt"
JOURNAL=$(cat "$TEST_ROOT/run-path.txt")
JOURNAL_ARG=$(jq -nc --arg p "$JOURNAL" '$p')
cp "$JOURNAL" "$TEST_ROOT/prefix.jsonl"
mkdir "$JOURNAL.tmp"
if "$AILANG" run --package-dir "$EX" --caps IO,FS --entry appendProbe --args-json "$JOURNAL_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/write-error.txt"; then exit 1; fi
cmp "$JOURNAL" "$TEST_ROOT/prefix.jsonl"
rmdir "$JOURNAL.tmp"
"$AILANG" run --package-dir "$EX" --caps IO,FS --entry appendProbe --args-json "$JOURNAL_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/commit.txt"
jq -s -e 'length==2 and .[0].seq==0 and .[1].seq==1' "$JOURNAL" >/dev/null
cp "$JOURNAL" "$TEST_ROOT/committed.jsonl"
# Existing ownership never replaces previous accepted actions.
if "$AILANG" run --package-dir "$EX" --caps IO,FS --entry openProbe --args-json "$POLICY_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/owner-error.txt"; then exit 1; fi
cmp "$JOURNAL" "$TEST_ROOT/committed.jsonl"
# Duplicate sequence is refused, leaving valid committed journal intact.
if "$AILANG" run --package-dir "$EX" --caps IO,FS --entry appendProbe --args-json "$JOURNAL_ARG" "$EX/store_probe.ail" > "$TEST_ROOT/sequence-error.txt"; then exit 1; fi
cmp "$JOURNAL" "$TEST_ROOT/committed.jsonl"
printf 'Content store: generated miss/cache-only repeat; invalid/model/busy/budget/provider/config controls; atomic journal write failure and ownership/sequence controls pass\n'
