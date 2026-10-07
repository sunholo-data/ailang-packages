#!/bin/bash
# Effectful flow over SharedMem hooks (flow_integration_test.ail): fails on
# any FAIL line or any missing case.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=$(AILANG_RELAX_MODULES=1 ailang run --caps IO,SharedMem,Rand,Clock,FS,Env,Net --entry main flow_integration_test.ail 2>&1)
grep -E '^(PASS|FAIL)' <<<"$OUT"
rc=0
grep -q '^FAIL' <<<"$OUT" && rc=1
for name in "create returns sep-2631 descriptor" "token stored as digest only" "upload round trip sha256" \
            "token is single use" "fileRef deleted after use" "expired token refused" "size cap enforced" \
            "empty upload refused" "unknown token refused" "cross-account refusal" "expired fileRef gone" \
            "foreign fileRef refused" "mime allow-list enforced" "receive via host round trip" "accept upload file" \
            "create needs account and sane config" "no raw token in store" "tampered bytes refused" "refused attempt spends the token"; do
  grep -qxF "PASS $name" <<<"$OUT" || { echo "MISSING PASS: $name"; rc=1; }
done
[ $rc -eq 0 ] && echo "ok: all flow checks pass"
exit $rc
