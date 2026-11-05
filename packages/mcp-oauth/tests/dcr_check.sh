#!/bin/bash
# M1b: RFC 7591 dynamic client registration and its abuse controls (T12, T15).
set -uo pipefail
source "$(dirname "$0")/suite_lib.sh"
run_suite dcr IO,SharedMem,Rand,Clock,Env \
  "dcr off by default" "dcr public registration" "TestDescribeRequestOmitsClientName" "dcr public client gets tokens" \
  "dcr confidential registration" "dcr secret method needs cfg.confidential" "dcr request validation" \
  "TestDcrRedirectAllowlist" "TestDcrRateLimitPerCaller" "TestTrustedCallerIpIgnoresForgedPrefix" "TestDcrGlobalCap" \
  "TestDcrUnusedExpires" "TestDcrUsedRegistrationSlides" "TestDcrBodyCap"
rc=$?
[ $rc -eq 0 ] && echo "ok: dcr checks pass"
exit $rc
