#!/bin/bash
# Runs the effectful flow checks (flow_integration_test.ail) and fails on any
# FAIL line or any missing case. Case names = sprint plan P2 criteria.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=$(AILANG_RELAX_MODULES=1 ailang run --caps IO,SharedMem,Rand,Clock,FS,Env,Net --entry main flow_integration_test.ail 2>&1)
echo "$OUT" | grep -E '^(PASS|FAIL)'
rc=0
grep -q '^FAIL' <<<"$OUT" && rc=1
for name in "authorize rejects plain pkce" "authorize rejects unregistered redirect" "code is single use" \
            "code replay revokes" "expired code rejected" "code bound to client and redirect" \
            "refresh rotates" "refresh reuse revokes family" "login url keeps its query" "describe request" "token response has expires_in" "redirect carries iss"; do
  grep -qxF "PASS $name" <<<"$OUT" || { echo "MISSING PASS: $name"; rc=1; }
done
[ $rc -eq 0 ] && echo "ok: all flow checks pass"
exit $rc
