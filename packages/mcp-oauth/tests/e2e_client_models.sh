#!/bin/bash
# End-to-end 0.2 client models against the example service under real
# serve-api (tests/e2e_flow.sh covers the 0.1.2 CIMD path, unchanged):
#   * metadata advertises registration, revocation and the secret methods;
#   * a GE-shaped confidential client (client_secret_basic, the GE redirect):
#     authorize -> sign in -> code -> token with HTTP Basic -> gated tool;
#     a wrong secret -> 401 + WWW-Authenticate: Basic; refresh rotates;
#   * RFC 7009: revoking the refresh token kills the family (tool -> 401);
#   * DCR: a public registration completes a flow; a foreign redirect host is
#     refused; the 11th registration from one caller is 429 whatever the
#     forged X-Forwarded-For prefix;
#   * `ailang mcp check --target both` still passes; the log is clean and
#     never holds a secret, code or token.
set -uo pipefail
cd "$(dirname "$0")/example"
P=${E2E_PORT:-18998}
BASE="http://localhost:$P"
LOG=$(mktemp)
MCP_OAUTH_EXAMPLE_TEST_ROUTES=1 OAUTH_ISSUER=$BASE AILANG_TRACE_VALUES=off ailang serve-api --mcp-http --port "$P" --oauth-issuer "$BASE" \
  --caps IO,SharedMem,Rand,Clock,Env,FS,Net . >"$LOG" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null; rm -f "$LOG"' EXIT
for _ in $(seq 1 60); do curl -s -o /dev/null "$BASE/api/_health" && break; sleep 1; done

rc=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1: $2"; rc=1; }
GECB="https://vertexaisearch.cloud.google.com/oauth-redirect"
CLAUDECB="https://claude.ai/api/mcp/auth_callback"
VERIFIER="dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
CHALLENGE="E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
loc() { curl -s -o /dev/null -w '%{redirect_url}' "$@"; }
qparam() { sed -n "s/.*[?&]$2=\([^&]*\).*/\1/p" <<<"$1"; }
jfield() { sed -n "s/.*\"$2\":\"\([^\"]*\)\".*/\1/p" <<<"$1"; }
code_for() { # client_id redirect state -> code
  local l1 l2
  l1=$(loc -G "$BASE/oauth/authorize" --data-urlencode response_type=code --data-urlencode "client_id=$1" \
    --data-urlencode "redirect_uri=$2" --data-urlencode "code_challenge=$CHALLENGE" \
    --data-urlencode code_challenge_method=S256 --data-urlencode "state=$3")
  l2=$(loc -X POST "$BASE/oauth/login/complete" --data-urlencode "handle=$(qparam "$l1" handle)" --data-urlencode id_token=demo-user-token)
  [[ "$l2" == "$2?"* ]] && qparam "$l2" code
}
call_tool() {
  curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/mcp/connect/" -H 'content-type: application/json' \
    -H 'accept: application/json, text/event-stream' -H "Authorization: Bearer $1" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"whoami","arguments":{}}}'
}

M=$(curl -s "$BASE/.well-known/oauth-authorization-server")
[[ "$M" == *"\"registration_endpoint\":\"$BASE/oauth/register\""* && "$M" == *"\"revocation_endpoint\":\"$BASE/oauth/revoke\""* \
   && "$M" == *'"token_endpoint_auth_methods_supported":["none","client_secret_basic","client_secret_post"]'* \
   && "$M" == *'"client_id_metadata_document_supported":true'* ]] && pass "metadata advertises the enabled client models" || fail "metadata" "$M"

# --- GE-shaped confidential client ---
C=$(curl -s -X POST "$BASE/test/create-client" --data-urlencode method=client_secret_basic --data-urlencode refresh_policy=rotate)
ID=$(jfield "$C" client_id); SECRET=$(jfield "$C" client_secret)
[[ "$ID" == mco_* && "$SECRET" == mcs_* ]] && pass "GE client created" || fail "GE client created" "$C"
CODE=$(code_for "$ID" "$GECB" ge1)
[ -n "$CODE" ] && pass "GE client signs in to the GE redirect" || fail "GE client signs in to the GE redirect" "no code"
WRONG=$(curl -s -D - -u "$ID:mcs_wrong" -X POST "$BASE/oauth/token" --data-urlencode grant_type=authorization_code \
  --data-urlencode "code=$CODE" --data-urlencode "code_verifier=$VERIFIER" --data-urlencode "redirect_uri=$GECB")
[[ "$WRONG" == *" 401"* && "$WRONG" == *'invalid_client'* && "$WRONG" == *'Www-Authenticate: Basic realm="oauth"'* ]] \
  && pass "wrong secret -> 401 invalid_client + WWW-Authenticate: Basic" || fail "wrong secret" "$WRONG"
TOK=$(curl -s -u "$ID:$SECRET" -X POST "$BASE/oauth/token" --data-urlencode grant_type=authorization_code \
  --data-urlencode "code=$CODE" --data-urlencode "code_verifier=$VERIFIER" --data-urlencode "redirect_uri=$GECB")
ACCESS=$(jfield "$TOK" access_token); REFRESH=$(jfield "$TOK" refresh_token)
[[ -n "$ACCESS" && -n "$REFRESH" ]] && pass "client_secret_basic token exchange" || fail "client_secret_basic token exchange" "$TOK"
[ "$(call_tool "$ACCESS")" = 200 ] && pass "GE token reaches the gated tool" || fail "GE token reaches the gated tool" "not 200"
TOK2=$(curl -s -u "$ID:$SECRET" -X POST "$BASE/oauth/token" --data-urlencode grant_type=refresh_token --data-urlencode "refresh_token=$REFRESH")
ACCESS2=$(jfield "$TOK2" access_token); REFRESH2=$(jfield "$TOK2" refresh_token)
[[ -n "$ACCESS2" && -n "$REFRESH2" && "$REFRESH2" != "$REFRESH" ]] && pass "GE refresh rotates" || fail "GE refresh rotates" "$TOK2"

# --- RFC 7009 ---
RV=$(curl -s -w ' HTTP%{http_code}' -u "$ID:$SECRET" -X POST "$BASE/oauth/revoke" --data-urlencode "token=$REFRESH2" --data-urlencode token_type_hint=refresh_token)
AFTER=$(curl -s -u "$ID:$SECRET" -X POST "$BASE/oauth/token" --data-urlencode grant_type=refresh_token --data-urlencode "refresh_token=$REFRESH2")
[[ "$RV" == *HTTP200 && "$(call_tool "$ACCESS2")" = 401 && "$(call_tool "$ACCESS")" = 401 && "$AFTER" == *invalid_grant* ]] \
  && pass "revocation kills the family" || fail "revocation kills the family" "$RV / $AFTER"
RV=$(curl -s -w ' HTTP%{http_code}' -u "$ID:$SECRET" -X POST "$BASE/oauth/revoke" --data-urlencode "token=never-issued")
[[ "$RV" == *HTTP200 ]] && pass "revoking an unknown token is 200" || fail "revoking an unknown token is 200" "$RV"

# --- DCR ---
R=$(curl -s -w ' HTTP%{http_code}' -X POST "$BASE/oauth/register" -H 'content-type: application/json' \
  -d "{\"redirect_uris\":[\"$CLAUDECB\"],\"client_name\":\"Totally Official\"}")
DID=$(jfield "$R" client_id)
[[ "$R" == *HTTP201 && "$DID" == mco_* && "$R" == *'"token_endpoint_auth_method":"none"'* && "$R" != *client_secret* && "$R" != *Official* ]] \
  && pass "DCR public registration" || fail "DCR public registration" "$R"
DCODE=$(code_for "$DID" "$CLAUDECB" d1)
DTOK=$(curl -s -X POST "$BASE/oauth/token" --data-urlencode grant_type=authorization_code --data-urlencode "code=$DCODE" \
  --data-urlencode "code_verifier=$VERIFIER" --data-urlencode "client_id=$DID" --data-urlencode "redirect_uri=$CLAUDECB")
[ "$(call_tool "$(jfield "$DTOK" access_token)")" = 200 ] && pass "DCR client reaches the gated tool" || fail "DCR client reaches the gated tool" "$DTOK"
R=$(curl -s -w ' HTTP%{http_code}' -X POST "$BASE/oauth/register" -H 'content-type: application/json' -d '{"redirect_uris":["https://evil.example/cb"]}')
[[ "$R" == *invalid_redirect_uri*HTTP400 ]] && pass "DCR refuses a host outside dcrRedirectHosts" || fail "DCR refuses a host outside dcrRedirectHosts" "$R"
codes=""
for i in $(seq 1 11); do
  codes="$codes $(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/oauth/register" -H 'content-type: application/json' \
    -H "X-Forwarded-For: 10.$i.0.1, 198.51.100.77" -d "{\"redirect_uris\":[\"$CLAUDECB\"]}")"
done
[ "$codes" = " 201 201 201 201 201 201 201 201 201 201 429" ] && pass "DCR 11th registration per caller is 429 (rightmost XFF)" || fail "DCR rate limit" "$codes"

CHECK=$(ailang mcp check "$BASE/mcp/connect/" --target both 2>&1); CHECK_RC=$?
NPASS=$(grep -c "^  PASS" <<<"$CHECK"); NFAIL=$(grep -c "^  FAIL" <<<"$CHECK")
FRAMING=$(grep -E "authorization-framing" <<<"$CHECK" | head -1 | sed 's/^ *//')
if [ $CHECK_RC -eq 0 ] && [ "$NFAIL" -eq 0 ] && [ "$NPASS" -ge 5 ]; then pass "mcp check $NPASS/$NPASS"; else fail "mcp check" "rc=$CHECK_RC pass=$NPASS fail=$NFAIL"; fi
echo "info: $FRAMING"
grep -E "  WARN|  ERROR" "$LOG" | grep -v MOD010 && fail "server log clean" "warnings above" || pass "server log clean"
if grep -qF "$SECRET" "$LOG" || grep -qF "$ACCESS" "$LOG" || grep -qF "$REFRESH" "$LOG" || grep -qF "$CODE" "$LOG"; then
  fail "log never holds a secret, code or token" "leaked"
elif [ -z "$SECRET$ACCESS" ]; then fail "log never holds a secret, code or token" "nothing was issued to look for"
else pass "log never holds a secret, code or token"; fi
[ $rc -eq 0 ] && echo "ok: e2e client models"
exit $rc
