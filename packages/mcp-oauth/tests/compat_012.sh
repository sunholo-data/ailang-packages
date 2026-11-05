#!/bin/bash
# Backward-compatibility gate (design success metric 1): the 0.1.2 test suites
# and the 0.1.2 example service, BYTE FOR BYTE as released (git f2568be,
# "sunholo/mcp_oauth 0.1.2"), run against this tree's package code. The
# in-tree ifc_leaks.sh / lint.sh / svc.ail have grown 0.2 cases; this proves
# the originals still pass. Needs the git history (any clone of the repo).
set -uo pipefail
PKG="$(cd "$(dirname "$0")/.." && pwd)"
REV="${COMPAT_REV:-f2568be}"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cp -R "$PKG" "$WORK/pkg"
rm -rf "$WORK/pkg/tests/example"; mkdir -p "$WORK/pkg/tests/example"
for f in flow_check.sh cimd_check.sh ifc_leaks.sh lint.sh e2e_flow.sh; do
  git -C "$PKG" show "$REV:packages/mcp-oauth/tests/$f" > "$WORK/pkg/tests/$f" || { echo "FAIL: cannot read $f at $REV"; exit 1; }
done
for f in svc.ail ailang.toml; do
  git -C "$PKG" show "$REV:packages/mcp-oauth/tests/example/$f" > "$WORK/pkg/tests/example/$f" || { echo "FAIL: cannot read example/$f at $REV"; exit 1; }
done
(cd "$WORK/pkg/tests/example" && ailang lock >/dev/null 2>&1) || { echo "FAIL: ailang lock for the 0.1.2 example"; exit 1; }
rc=0
for t in flow_check cimd_check ifc_leaks lint e2e_flow; do
  if out=$(cd "$WORK/pkg" && bash "tests/$t.sh" 2>&1); then echo "ok: 0.1.2 $t.sh passes against this tree"
  else echo "FAIL: 0.1.2 $t.sh"; grep -vE '^(PASS|ok)' <<<"$out" | head -10; rc=1; fi
done
exit $rc
