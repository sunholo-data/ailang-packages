#!/bin/bash
# M1a: pre-registered confidential clients (GE custom MCP data store shape).
# The suite runs WITHOUT --caps Net: a registered (mco_) client is looked up
# in the store and never fetched, so a fetch on that path would kill the run
# (TestRegisteredIdNeverFetched is structural, not just an assertion).
set -uo pipefail
source "$(dirname "$0")/suite_lib.sh"
run_suite confidential IO,SharedMem,Rand,Clock,Env \
  "GE-shaped happy path" "TestWrongSecretInvalidClient" "TestConfidentialWithoutSecret" \
  "refused client auth does not consume the code" "client_secret_post client authenticates in the form only" \
  "TestCimdWithSecretRefused" "TestLegacyExchangeRefusesRegisteredId" "TestLegacyRefreshRefusesRegisteredId" \
  "TestKindMismatchRefused" "TestSecretNeverStored" "TestRegisteredIdNeverFetched" "TestRegisteredRedirectExact" \
  "confidential client still needs PKCE" "rotated secret replaces the old one" \
  "registered clients need cfg.confidential" "deleted client is unknown"
rc=$?
[ $rc -eq 0 ] && echo "ok: confidential client checks pass"
exit $rc
