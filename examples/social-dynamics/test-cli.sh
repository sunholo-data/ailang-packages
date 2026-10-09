#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
AILANG=${AILANG:-ailang}
TMP=$(mktemp -d "${TMPDIR:-/tmp}/social-cli.XXXXXX")
trap 'rm -rf "$TMP"' EXIT
"$AILANG" install --path "$ROOT/examples/social-dynamics" --bin-dir "$TMP/bin"
cd "$TMP"
for recording in "$ROOT"/examples/social-dynamics/recordings/*.ndjson; do
 name=$(basename "$recording" .ndjson)
 "$TMP/bin/social-lab" < "$recording" > "$TMP/$name.ndjson"
 cmp "$TMP/$name.ndjson" "$ROOT/.ailang/state/social-experiments/$name.ndjson"
done
set +e
printf '%s\n' '{"invalid":true}' | "$TMP/bin/social-lab" > "$TMP/invalid.ndjson"
rc=$?
set -e
test "$rc" = 1
jq -e '.error.code == "invalid_schema"' "$TMP/invalid.ndjson" >/dev/null
printf 'CLI install: five traces identical from unrelated cwd; malformed command exits 1\n'
