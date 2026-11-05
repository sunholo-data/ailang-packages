#!/bin/bash
# M1c: RFC 7009 revocation (POST /oauth/revoke).
set -uo pipefail
source "$(dirname "$0")/suite_lib.sh"
run_suite revoke IO,SharedMem,Rand,Clock,Env \
  "family keeps unexpired tokens" "TestRevokeEndpointKillsFamily" "revoke ends a stable refresh token" "TestRevokeAlways200" \
  "revocation needs client auth, cfg.revocation and a token" "CIMD client revokes its refresh token"
rc=$?
[ $rc -eq 0 ] && echo "ok: revocation checks pass"
exit $rc
