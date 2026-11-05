#!/bin/bash
# The IFC guarantee is only real if a leak in the ACTUAL flow module fails to
# compile. Inject each leak into a copy of the package and require
# `ailang check` to reject it with an information-flow violation; the clean
# copy must pass. (Design T7 item 6.)
set -uo pipefail
PKG="$(cd "$(dirname "$0")/.." && pwd)"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
rc=0
check_copy() { (cd "$1" && ailang check --package . 2>&1); }

# Capture output before grepping: with pipefail, `cmd | grep -q` turns a
# MATCH into a failure (grep exits early, cmd gets SIGPIPE).
cp -R "$PKG" "$WORK/clean"
out=$(check_copy "$WORK/clean")
if grep -q "all passed" <<<"$out"; then echo "ok: clean copy compiles"; else echo "FAIL: clean copy does not compile"; rc=1; fi

leak() {
  local name="$1" code="$2"
  cp -R "$PKG" "$WORK/$name"
  printf '\n%s\n' "$code" >> "$WORK/$name/flow.ail"
  out=$(check_copy "$WORK/$name")
  if grep -q "information-flow violation" <<<"$out"; then
    echo "ok: leak rejected: $name"
  else
    echo "FAIL: leak not rejected by IFC: $name"; grep -m2 -E "Error|error" <<<"$out"; rc=1
  fi
}
leak "log-classified-token" 'func leakToken(raw: string) -> unit ! {IO} = audit("t=${asSecret(raw)}")'
leak "log-minted-code"      'func leakCode() -> unit ! {IO, Rand[mode=crypto]} = audit("c=${newSecret()}")'
leak "log-token-body"       'func leakBody(a: string, b: string) -> unit ! {IO} = audit(tokenBody(asSecret(a), asSecret(b), 3600))'
# 0.2 client secrets (T11): minted, returned by createClient, and carried in
# the DCR registration response.
leak "log-client-secret"    'func leakClientSecret() -> unit ! {IO, Rand[mode=crypto]} = audit("s=${newClientSecret()}")'
leak "log-created-client"   'func leakCreated(h: Hooks, cfg: ClientConfig) -> unit ! {IO, FS, Env, Net, Clock, SharedMem, Rand[mode=crypto], Declassify} = match createClient(h, cfg, ["https://a.example/cb"], "client_secret_basic", "rotate", 0) { Ok((id, s)) => audit("created ${id} ${s}"), Err(e) => audit(e) }'
leak "log-dcr-response"     'func leakDcr(h: Hooks, cfg: ClientConfig) -> unit ! {IO, FS, Env, Net, Clock, SharedMem, Rand[mode=crypto], Declassify} = match registerClientDcr(h, cfg, "ip", "{}", 0) { Ok((st, b)) => audit(b), Err(e) => audit(e) }'
leak "log-token-request"    'func leakTokenRequest(h: Hooks, cfg: ClientConfig) -> unit ! {IO, FS, Env, Net, Clock, SharedMem, Rand[mode=crypto], Declassify} = match tokenRequest(h, cfg, "", "", 0) { (st, b, w) => audit(b) }'
leak "log-login-handle"     'func leakHandle(h: Hooks, cfg: ClientConfig) -> unit ! {IO, FS, Env, Net, Clock, SharedMem, Rand[mode=crypto], Declassify} = match beginAuthorizeFor(h, cfg, "https://l.example", "mco_0123456789abcdef0123456789abcdef", "https://a.example/cb", "code", "c", "S256", "s", 0) { Ok(u) => audit(u), Err(e) => audit(e) }'
leak "log-presented-secret" 'func leakPresented(b: string) -> unit ! {IO} = audit("p=${asSecret(formGet(b, "client_secret"))}")'
exit $rc
