#!/bin/bash
# End-to-end under real serve-api (tests/example/svc.ail, SharedMem hooks):
#   create -> multipart POST /uploads (curl -F, the descriptor's own curl line)
#   -> resolve: sha256 of a binary file round-trips; replay 409; another
#   account 404; second resolve 404; via-host base64 round trip; expired-cap
#   refusal; and what happens to a file above serve-api's --max-upload-size.
set -uo pipefail
cd "$(dirname "$0")/example"
P=${E2E_PORT:-18997}
BASE="http://localhost:$P"
LOG=$(mktemp); WORK=$(mktemp -d)
# The widget origin claude.ai would use for this server (widget.claudeWidgetOrigin).
WIDGET_ORIGIN="https://$(printf '%s' "$BASE/mcp/" | shasum -a 256 | cut -c1-32).claudemcpcontent.com"
AILANG_TRACE_VALUES=off ailang serve-api --port "$P" --max-upload-size 3000000 --cors-origin "$WIDGET_ORIGIN" \
  --caps IO,SharedMem,Rand,Clock,Env,FS,Net . >"$LOG" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null; rm -rf "$LOG" "$WORK"' EXIT
for _ in $(seq 1 60); do curl -s -o /dev/null "$BASE/api/_health" && break; sleep 1; done

rc=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1: $2"; rc=1; }
jget() { python3 -I -c 'import json,sys; d=json.loads(sys.stdin.read()); [d:=d[k] for k in sys.argv[1:]]; print(d)' "$@"; }
create() { curl -s -X POST "$BASE/api/create" -H 'content-type: application/json' -H "x-account: $1" -d "{\"filename\":\"$2\",\"maxBytes\":${3:-0}}"; }
upload() { curl -s -w '\n%{http_code}' -F "token=$1" -F "file=@$2;filename=$3" "$BASE/uploads"; }
resolve() { curl -s -w '\n%{http_code}' -X POST "$BASE/api/resolve" -H 'content-type: application/json' -H "x-account: $1" -d "{\"fileRef\":\"$2\"}"; }
code() { tail -n1 <<<"$1"; }
body() { sed '$d' <<<"$1"; }

# a 1.5 MB binary file with every byte value
python3 -I -c 'import os,sys; sys.stdout.buffer.write(bytes(range(256))*6000)' > "$WORK/big.docx"
SHA=$(shasum -a 256 "$WORK/big.docx" | cut -d' ' -f1)

D=$(create acct-1 "AGM.docx")
TOKEN=$(jget upload multipart fields token <<<"$D" 2>/dev/null)
REF=$(jget fileRef <<<"$D" 2>/dev/null)
[ ${#TOKEN} -eq 64 ] && [[ "$REF" == mcp-file://svc.example/file_* ]] && pass "create returns descriptor" || fail "create returns descriptor" "$D"

U=$(upload "$TOKEN" "$WORK/big.docx" "AGM.docx")
[ "$(code "$U")" = 200 ] && [ "$(body "$U" | jget sha256)" = "$SHA" ] && [ "$(body "$U" | jget fileRef)" = "$REF" ] \
  && pass "multipart upload sha256 matches" || fail "multipart upload sha256 matches" "$(head -c 300 <<<"$U")"

R=$(upload "$TOKEN" "$WORK/big.docx" "AGM.docx")
[ "$(code "$R")" = 409 ] && pass "replayed token refused" || fail "replayed token refused" "$(head -c 300 <<<"$R")"

X=$(resolve acct-2 "$REF")
[ "$(code "$X")" = 404 ] && pass "other account gets 404" || fail "other account gets 404" "$X"

O=$(resolve acct-1 "$REF")
[ "$(code "$O")" = 200 ] && [ "$(body "$O" | jget sha256)" = "$SHA" ] && [ "$(body "$O" | jget sizeBytes)" = 1536000 ] \
  && pass "owner resolves identical bytes" || fail "owner resolves identical bytes" "$O"

A=$(resolve acct-1 "$REF")
[ "$(code "$A")" = 404 ] && pass "fileRef single read" || fail "fileRef single read" "$A"

D2=$(create acct-1 "small.pdf" 1000); T2=$(jget upload multipart fields token <<<"$D2")
L=$(upload "$T2" "$WORK/big.docx" "small.pdf")
[ "$(code "$L")" = 413 ] && pass "token size cap 413" || fail "token size cap 413" "$(head -c 300 <<<"$L")"

D3=$(create acct-1 ""); T3=$(jget upload multipart fields token <<<"$D3")
B64=$(head -c 4096 "$WORK/big.docx" | base64 | tr -d '\n')
V=$(curl -s -w '\n%{http_code}' -X POST "$BASE/api/viaHost" -H 'content-type: application/json' \
  -d "{\"token\":\"$T3\",\"filename\":\"via.bin\",\"base64\":\"$B64\"}")
[ "$(code "$V")" = 200 ] && [ "$(body "$V" | jget sha256)" = "$(head -c 4096 "$WORK/big.docx" | shasum -a 256 | cut -d' ' -f1)" ] \
  && pass "via-host base64 round trip" || fail "via-host base64 round trip" "$(head -c 300 <<<"$V")"

# Above serve-api's --max-upload-size (3000000) but under the token cap (2000000 ceiling => no).
# Probe only: what does serve-api do with a file larger than --max-upload-size?
python3 -I -c 'import sys; sys.stdout.buffer.write(b"x"*3500000)' > "$WORK/huge.bin"
D4=$(create acct-1 "huge.bin"); T4=$(jget upload multipart fields token <<<"$D4")
H=$(upload "$T4" "$WORK/huge.bin" "huge.bin")
echo "NOTE above --max-upload-size: HTTP $(code "$H") $(body "$H" | head -c 160)"
[ "$(code "$H")" != 200 ] && pass "file above serve-api limit not accepted" || fail "file above serve-api limit not accepted" "accepted"

# CORS: the widget's multipart POST is a "simple" request (no preflight); it can
# read the receipt only if the response echoes its origin. Other origins: 403.
D5=$(create acct-1 "c.txt"); T5=$(jget upload multipart fields token <<<"$D5")
printf 'hello' > "$WORK/c.txt"
HDRS=$(curl -s -D - -o /dev/null -H "Origin: $WIDGET_ORIGIN" -F "token=$T5" -F "file=@$WORK/c.txt" "$BASE/uploads")
grep -qi "^access-control-allow-origin: $WIDGET_ORIGIN" <<<"$HDRS" && pass "widget origin may read the receipt" || fail "widget origin may read the receipt" "$HDRS"
D6=$(create acct-1 "c.txt"); T6=$(jget upload multipart fields token <<<"$D6")
EV=$(curl -s -o /dev/null -w '%{http_code}' -H "Origin: https://evil.example" -F "token=$T6" -F "file=@$WORK/c.txt" "$BASE/uploads")
[ "$EV" = 403 ] && pass "other origins refused before the handler" || fail "other origins refused before the handler" "HTTP $EV"

[ -n "$TOKEN" ] && grep -qF "$TOKEN" "$LOG" && fail "server log has no token" "token found in log" || pass "server log has no token"
[ $rc -eq 0 ] && echo "ok: e2e uploads"
exit $rc
