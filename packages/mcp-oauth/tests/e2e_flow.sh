#!/bin/bash
# End-to-end PKCE flow against the example service under real serve-api:
# authorize -> login complete -> token -> gated MCP tool (200); then replay
# the code -> invalid_grant, and the revoked token -> 401 on the tool.
# Also runs `ailang mcp check --target both` (all five checks must PASS).
set -uo pipefail
cd "$(dirname "$0")/example"
P=${E2E_PORT:-18999}
BASE="http://localhost:$P"
LOG=$(mktemp)
OAUTH_ISSUER=$BASE AILANG_TRACE_VALUES=off ailang serve-api --mcp-http --port "$P" --oauth-issuer "$BASE" \
  --caps IO,SharedMem,Rand,Clock,Env,FS,Net . >"$LOG" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null; rm -f "$LOG"' EXIT
for _ in $(seq 1 60); do curl -s -o /dev/null "$BASE/api/_health" && break; sleep 1; done

rc=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1: $2"; rc=1; }
CLIENT="https://claude.ai/oauth/claude-code-client-metadata"
CB="https://claude.ai/api/mcp/auth_callback"
VERIFIER="dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
CHALLENGE="E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
loc() { curl -s -o /dev/null -w '%{redirect_url}' "$@"; }
qparam() { sed -n "s/.*[?&]$2=\([^&]*\).*/\1/p" <<<"$1"; }

L1=$(loc -G "$BASE/oauth/authorize" --data-urlencode response_type=code --data-urlencode "client_id=$CLIENT" \
  --data-urlencode "redirect_uri=$CB" --data-urlencode "code_challenge=$CHALLENGE" \
  --data-urlencode code_challenge_method=S256 --data-urlencode state=st1)
HANDLE=$(qparam "$L1" handle)
[ -n "$HANDLE" ] && pass "authorize redirects to login" || fail "authorize redirects to login" "location=$L1"

L2=$(loc -X POST "$BASE/oauth/login/complete" --data-urlencode "handle=$HANDLE" --data-urlencode id_token=demo-user-token)
CODE=$(qparam "$L2" code)
[[ "$L2" == "$CB?"* && -n "$CODE" && "$(qparam "$L2" state)" == st1 ]] && pass "login returns code to redirect_uri" || fail "login returns code to redirect_uri" "location=$L2"

TOK_BODY=$(curl -s -X POST "$BASE/oauth/token" --data-urlencode grant_type=authorization_code --data-urlencode "code=$CODE" \
  --data-urlencode "code_verifier=$VERIFIER" --data-urlencode "client_id=$CLIENT" --data-urlencode "redirect_uri=$CB")
ACCESS=$(sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p' <<<"$TOK_BODY")
[ -n "$ACCESS" ] && pass "token issued" || fail "token issued" "$TOK_BODY"

call_tool() {
  curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/mcp/connect/" -H 'content-type: application/json' \
    -H 'accept: application/json, text/event-stream' -H "Authorization: Bearer $1" \
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"whoami","arguments":{}}}'
}
[ "$(call_tool "$ACCESS")" = 200 ] && pass "gated tool accepts the issued token" || fail "gated tool accepts the issued token" "not 200"

REPLAY=$(curl -s -w ' HTTP%{http_code}' -X POST "$BASE/oauth/token" --data-urlencode grant_type=authorization_code \
  --data-urlencode "code=$CODE" --data-urlencode "code_verifier=$VERIFIER" --data-urlencode "client_id=$CLIENT" --data-urlencode "redirect_uri=$CB")
[[ "$REPLAY" == *invalid_grant*"HTTP400" ]] && pass "code replay rejected" || fail "code replay rejected" "$REPLAY"
if [ -z "$ACCESS" ]; then fail "replay revoked the token" "no token was issued, so revocation cannot be shown"
elif [ "$(call_tool "$ACCESS")" = 401 ]; then pass "replay revoked the token"
else fail "replay revoked the token" "still accepted"; fi

CHECK=$(ailang mcp check "$BASE/mcp/connect/" --target both 2>&1); CHECK_RC=$?
NPASS=$(grep -c "^  PASS" <<<"$CHECK")
if [ $CHECK_RC -eq 0 ] && [ "$NPASS" -eq 5 ]; then pass "mcp check 5/5"; else fail "mcp check" "rc=$CHECK_RC pass=$NPASS"; fi
grep -E "  WARN|  ERROR" "$LOG" | grep -v MOD010 && fail "server log clean" "warnings above" || pass "server log clean"
[ $rc -eq 0 ] && echo "ok: e2e flow"
exit $rc
