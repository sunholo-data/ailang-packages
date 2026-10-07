#!/bin/bash
# widget_assets.ail must be exactly what tools/gen_bundle.sh generates from
# assets/ (a hand edit of the generated module, or an asset edit without
# regenerating, fails here). Also syntax-checks assets/widget.js with node.
set -uo pipefail
cd "$(dirname "$0")/.."
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
rc=0
ASSETS_OUT="$WORK/widget_assets.ail" ./tools/gen_bundle.sh >/dev/null
if cmp -s "$WORK/widget_assets.ail" widget_assets.ail; then echo "ok: widget_assets.ail in sync with assets/"
else echo "FAIL: widget_assets.ail differs from assets/ (run tools/gen_bundle.sh)"; rc=1; fi
grep -q 'export pure func extAppsSourceSha256() -> string = "fb56376b7583ecafb4820bdebc150abee18feb6258ff84b83c2c944ebd9c3602"' extapps_bundle.ail \
  && echo "ok: ext-apps bundle is the pinned 2.0.3 build" || { echo "FAIL: ext-apps bundle pin"; rc=1; }
exit $rc
