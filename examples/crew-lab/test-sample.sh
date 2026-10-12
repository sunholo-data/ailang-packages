#!/usr/bin/env bash
# Acceptance harness only: crew-sample picks varied moments deterministically,
# fetches words through the watch's library within a call budget, and reports.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EX="$ROOT/examples/crew-lab"
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/crew-sample.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$EX" --bin-dir "$TMP/bin" >/dev/null
# Offline (authored words, no provider): bounded, varied, deterministic, reported.
"$TMP/bin/crew-sample" --offline --home "$TMP/a" --count 8 --report "$TMP/report.txt" > "$TMP/a.ndjson"
"$TMP/bin/crew-sample" --offline --home "$TMP/b" --count 8 > "$TMP/b.ndjson"
cmp "$TMP/a.ndjson" "$TMP/b.ndjson"
jq -s -e 'length==8 and all(.[]; .schema=="crew_sample/1" and .calls==0 and .source=="authored" and (.words|length)>=1 and .narrative_ok) and ([.[0:5][].actor]|unique|length)==5' "$TMP/a.ndjson" >/dev/null
grep -q '^CREW WORDING SAMPLES: 8 moments, 0 provider calls' "$TMP/report.txt"
grep -q '^diplomat$' "$TMP/report.txt"
# Live under the AI stub (no provider): the real fetch path runs, rejected words
# are reported, and no more than --max-calls attempts are made.
EX_RUN=("$AILANG" run --quiet --package-dir "$EX" --caps IO,FS,Env,AI --ai-stub --fs-max-bytes 16MB "$EX/sample_cli.ail" --)
"${EX_RUN[@]}" --home "$TMP/live" --count 4 --max-calls 2 > "$TMP/live.ndjson"
jq -s -e '([.[].calls]|add)==2 and ([.[]|select(.source=="error")]|length)==2 and ([.[]|select(.error=="call budget used")]|length)==2' "$TMP/live.ndjson" >/dev/null
# Invalid input fails before any fetch.
if "$TMP/bin/crew-sample" --offline --home "$TMP/c" --count 0 > "$TMP/bad.out"; then echo "accepted --count 0" >&2; exit 1; fi
grep -q 'count must be 1..100' "$TMP/bad.out"
printf 'crew-sample: varied deterministic moments, readable report, call budget respected, stub rejections reported\n'
