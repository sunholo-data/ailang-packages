#!/bin/bash
# Source rules the type system cannot express (mirrors sunholo/mcp_oauth).
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0
# ailang #1523: a declared record type field loses its IFC label, so no
# declared type in flow.ail may hold a labelled string.
if awk '/^(export )?type /{t=1} t&&/string</{print; f=1} /}[[:space:]]*$/{t=0} END{exit !f}' flow.ail >/dev/null \
   || grep -nE '^\s*(export\s+)?type\s.*string<' flow.ail; then
  echo "FAIL: declared type with a labelled field in flow.ail"; rc=1
else echo "ok: no declared record type holds a labelled value"; fi
# Every function returning a fresh secret declares crypto randomness.
bad=$(grep -nE '^\s*func [a-zA-Z]+\(.*\) -> string<secret>' flow.ail | grep -v 'Rand\[mode=crypto\]' | grep -v 'asSecret')
if [ -n "$bad" ]; then echo "FAIL: secret minted without Rand[mode=crypto]:"; echo "$bad"; rc=1
else echo "ok: token minting declares Rand[mode=crypto]"; fi
# Tokens are looked up by digest, never compared raw.
if grep -nE 'tokenRaw\s*[!=]=|[!=]=\s*tokenRaw' flow.ail; then echo "FAIL: == on a raw token"; rc=1
else echo "ok: no == on raw tokens"; fi
# Storage keys and records hold digests: every tok:/used: key is built from digestOf.
if grep -nE '"(tok|used):\$\{' flow.ail | grep -vE '"(tok|used):\$\{(d|digestOf\([a-zA-Z(]+\))\}' ; then
  echo "FAIL: a token store key not built from a digest"; rc=1
else echo "ok: token store keys are digests"; fi
# Storage is reached only through the {not secret} wrappers (IFC gate).
if grep -nE 'h\.(putBytes|getBytes|delBytes|putMeta|claimMeta|getMeta|delMeta)\(' flow.ail | grep -vE '^[0-9]+:(func (putBytes|getBytes|delBytes|putMeta|claimMeta|getMeta|delMeta)\(h: Hooks|--)'; then
  echo "FAIL: a hook called directly, bypassing the {not secret} storage gate"; rc=1
else echo "ok: storage hooks only behind the {not secret} gate"; fi
# The widget (assets/widget.js) never uses ui/message (caution banner), innerHTML or eval.
if grep -nE 'sendMessage|ui/message|innerHTML|eval\(' assets/widget.js; then
  echo "FAIL: widget uses ui/message, innerHTML or eval"; rc=1
else echo "ok: widget reports via ui/update-model-context only"; fi
exit $rc
