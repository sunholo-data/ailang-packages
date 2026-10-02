#!/bin/bash
# Source rules the type system cannot express (design T6, T3, D4/#1523).
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0
# D4 / #1523: a declared record type field loses its IFC label, so no
# declared type in flow.ail may hold a labelled string.
types=$(grep -nE '^\s*(export\s+)?type\s' flow.ail)
if grep -q 'string<' <<<"$types"; then
  echo "FAIL: declared type with a labelled field in flow.ail"; rc=1
elif awk '/^(export )?type /{t=1} t&&/string</{print; f=1} /^}/{t=0} END{exit !f}' flow.ail >/dev/null; then
  echo "FAIL: declared type with a labelled field in flow.ail"; rc=1
else echo "ok: no declared record type holds a labelled value"; fi
# T3: every function returning a fresh secret declares crypto randomness.
bad=$(grep -nE '^\s*func [a-zA-Z]+\(.*\) -> string<secret>' flow.ail | grep -v 'Rand\[mode=crypto\]' | grep -v 'asSecret')
if [ -n "$bad" ]; then echo "FAIL: secret minted without Rand[mode=crypto]:"; echo "$bad"; rc=1
else echo "ok: secret minting declares Rand[mode=crypto]"; fi
# T6: secrets are compared via constantTimeEqual (in core.pkceOk) or as
# digests in storage keys; never compare raw secret params with ==.
if grep -nE '(codeRaw|refreshRaw|handleRaw|verifier)\s*==|==\s*(codeRaw|refreshRaw|handleRaw|verifier)' flow.ail; then
  echo "FAIL: == on a raw secret"; rc=1
else echo "ok: no == on raw secrets"; fi
grep -q 'constantTimeEqual' core.ail && echo "ok: PKCE uses constantTimeEqual" || { echo "FAIL: constantTimeEqual missing from core"; rc=1; }
exit $rc
