#!/bin/bash
# Z3: every contract in core.ail verifies, and each negative fixture is
# REFUTED (a fixture that verifies means the corresponding proof stopped
# meaning anything).
set -uo pipefail
cd "$(dirname "$0")/.."
rc=0
OUT=$(ailang verify core.ail 2>&1)
grep -E "VERIFIED|VIOLATION|ERROR|SKIPPED|exported functions" <<<"$OUT"
if grep -qE "VIOLATION|ERROR|SKIPPED" <<<"$OUT"; then echo "FAIL: core.ail has an unproved contract"; rc=1; fi
n=$(grep -c "VERIFIED" <<<"$OUT")
[ "$n" -ge 10 ] && echo "ok: core.ail $n contracts verified" || { echo "FAIL: expected >= 10 verified, got $n"; rc=1; }
for f in tests/broken_single_use.ail:uploadVerdictBroken tests/broken_expiry.ail:isExpiredBroken tests/broken_expiry.ail:ownerMatchesBroken; do
  file=${f%%:*}; fn=${f##*:}
  vout=$(ailang verify "$file" 2>&1)
  if grep -q "VIOLATION $fn" <<<"$vout"; then echo "ok: $fn refuted"
  else echo "FAIL: $fn was not refuted"; rc=1; fi
done
exit $rc
