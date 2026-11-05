#!/bin/bash
# M1d against the LIVE documents: fetches https://chatgpt.com/oauth/client.json
# and Claude Code's CIMD document through cimd.fetchClient and requires both to
# be accepted. Needs network. It also prints whether ChatGPT's live document
# still carries the shape the pure fixture pins (cimd_test.ail chatgptDoc), so
# a vendor change is visible rather than silent.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=$(AILANG_RELAX_MODULES=1 ailang run --caps IO,Net --entry main tests/cimd_live.ail 2>&1)
grep -E '^(PASS|FAIL)' <<<"$OUT"
rc=0
grep -q '^FAIL' <<<"$OUT" && rc=1
for n in "cimd accepts chatgpt live doc (network)" "cimd accepts claude live doc (network)"; do
  grep -qxF "PASS $n" <<<"$OUT" || { echo "MISSING PASS: $n"; rc=1; }
done
DOC=$(curl -s --max-time 20 https://chatgpt.com/oauth/client.json)
if [[ "$DOC" == *'"token_endpoint_auth_method":"private_key_jwt"'* && "$DOC" == *'"token_endpoint_auth_methods_supported":["none","private_key_jwt"]'* ]]; then
  echo "ok: live ChatGPT document still has the E17 shape"
else echo "NOTE: live ChatGPT document changed shape; re-check cimd_test.ail chatgptDoc: $DOC"; fi
[ $rc -eq 0 ] && echo "ok: live cimd documents accepted"
exit $rc
