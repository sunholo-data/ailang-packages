#!/bin/bash
# M1c: per-client refresh policy. rotate stays the default; stable is opt-in
# for confidential clients, with 30-day idle and 180-day absolute lifetimes (D3).
set -uo pipefail
source "$(dirname "$0")/suite_lib.sh"
run_suite refresh_policy IO,SharedMem,Rand,Clock,Env \
  "TestStableRefreshNoRotation" "TestStableRefreshNeedsClientAuth" "TestStableRefreshAbsoluteExpiry" \
  "TestFamilyDigestsPruned" "TestStableRefreshIdleExpiry" "TestStableRefusedForPublicClient" "rotate client refresh is single use"
rc=$?
[ $rc -eq 0 ] && echo "ok: refresh policy checks pass"
exit $rc
