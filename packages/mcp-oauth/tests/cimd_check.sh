#!/bin/bash
# CIMD fetch layers. Runs with serve-api's permissive Net settings ON
# (--net-allow-localhost/--net-allow-metadata/--net-allow-http) to prove
# Net[scope=public] refuses anyway. The private-resolution case needs DNS
# for localtest.me; it asserts the SPECIFIC refusal, so a DNS outage fails
# the check rather than passing it for the wrong reason.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=$(AILANG_RELAX_MODULES=1 ailang run --caps IO,Net --net-allow-http --net-allow-localhost --net-allow-metadata \
  --entry main cimd_integration_test.ail 2>&1)
grep -E '^(PASS|FAIL)' <<<"$OUT"
rc=0
grep -q '^FAIL' <<<"$OUT" && rc=1
for n in "cimd fetch refuses http" "cimd fetch refuses metadata ip" "cimd fetch refused for private resolution"; do
  grep -qxF "PASS $n" <<<"$OUT" || { echo "MISSING PASS: $n"; rc=1; }
done
exit $rc
