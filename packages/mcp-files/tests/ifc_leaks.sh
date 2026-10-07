#!/bin/bash
# The IFC guarantee is only real if a leak in the ACTUAL flow module fails to
# compile. Inject each leak into a copy of the package and require
# `ailang check` to reject it with an information-flow violation; the clean
# copy must pass.
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
leak "log-received-token"  'func leakToken(raw: string) -> unit ! {IO} = audit("t=${asSecret(raw)}")'
leak "log-minted-token"    'func leakMinted() -> unit ! {IO, Rand[mode=crypto]} = audit("t=${newSecret()}")'
leak "log-descriptor"      'func leakDesc() -> unit ! {IO, Rand[mode=crypto]} = audit(uploadDescriptor("https://u", newSecret(), "mcp-file://s/file_x", "", "", 0, 1))'
leak "store-raw-token-key"  'func leakKey(h: Hooks, raw: string) -> bool ! {IO, FS, Env, Net, Clock, SharedMem} = putMeta(h, "tok:${asSecret(raw)}", "{}", 0)'
leak "store-token-in-record" 'func leakRec(h: Hooks) -> bool ! {IO, FS, Env, Net, Clock, SharedMem, Rand[mode=crypto]} = putMeta(h, "k", "{\"t\":\"${newSecret()}\"}", 0)'
leak "store-descriptor"     'func leakDescStore(h: Hooks) -> bool ! {IO, FS, Env, Net, Clock, SharedMem, Rand[mode=crypto]} = putMeta(h, "k", uploadDescriptor("https://u", newSecret(), "mcp-file://s/file_x", "", "", 0, 1), 0)'
exit $rc
