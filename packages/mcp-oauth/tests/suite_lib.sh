#!/bin/bash
# Shared runner for the 0.2 client-model suites (tests/client_models.ail).
# Runs one suite under `ailang run` and fails on any FAIL line, on a missing
# PASS for a named case, or on a run that dies before printing them.
#   run_suite <suite> <caps> <case>...
run_suite() {
  local suite="$1" caps="$2"; shift 2
  local out run_rc rc=0
  out=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && AILANG_RELAX_MODULES=1 ailang run --caps "$caps" --entry main tests/client_models.ail -- "$suite" 2>&1)
  run_rc=$?
  grep -E '^(PASS|FAIL)' <<<"$out"
  if [ $run_rc -ne 0 ]; then echo "RUN FAILED (rc=$run_rc):"; grep -vE '^(PASS|FAIL|\[mcp_oauth\])' <<<"$out" | grep -v MOD010 | head -20; rc=1; fi
  grep -q '^FAIL' <<<"$out" && rc=1
  for name in "$@"; do
    grep -qxF "PASS $name" <<<"$out" || { echo "MISSING PASS: $name"; rc=1; }
  done
  return $rc
}
