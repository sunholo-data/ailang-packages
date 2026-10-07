#!/bin/bash
# fetchFileParam layers, with permissive Net flags ON (--net-allow-http/
# -localhost/-metadata) to prove Net[scope=public] refuses anyway. Needs the
# network (DNS for localtest.me, raw.githubusercontent.com for the pinned
# file); every case asserts a SPECIFIC outcome, so an outage fails the check
# instead of passing it for the wrong reason.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=$(AILANG_RELAX_MODULES=1 ailang run --caps IO,Net --net-allow-http --net-allow-localhost --net-allow-metadata \
  --entry main fetch_integration_test.ail 2>&1)
grep -E '^(PASS|FAIL)' <<<"$OUT"
rc=0
grep -q '^FAIL' <<<"$OUT" && rc=1
for n in "fetch refuses http" "fetch refuses userinfo" "fetch needs file_id" "fetch refuses metadata ip" \
         "fetch refuses private resolution" "fetch public file sha256" "fetch size cap"; do
  grep -qxF "PASS $n" <<<"$OUT" || { echo "MISSING PASS: $n"; rc=1; }
done
exit $rc
