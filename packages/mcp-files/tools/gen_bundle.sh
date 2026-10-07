#!/bin/bash
# Regenerate the two generated modules widget.ail inlines:
#   widget_assets.ail  from assets/widget.{html,js,css}  (always)
#   extapps_bundle.ail from the pinned @modelcontextprotocol/ext-apps release
#                      (with --bundle; needs npm and the network)
# The sha256 pin is of dist/src/app-with-deps.js as the F1 spike ran it in
# claude.ai (2026-10-07). Bumping the version = update both pins, rerun with
# --bundle, then re-test the widget in claude.ai before releasing.
set -euo pipefail
VERSION=2.0.3
SHA256=fb56376b7583ecafb4820bdebc150abee18feb6258ff84b83c2c944ebd9c3602
PKG="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PKG"
GEN="ailang run --caps IO,FS,Env --entry main tools/gen_bundle.ail --"
OUT=${ASSETS_OUT:-widget_assets.ail}
$GEN assets "$OUT" widgetHtmlTemplate=assets/widget.html widgetJs=assets/widget.js widgetCss=assets/widget.css
if [ "${1:-}" = "--bundle" ]; then
  WORK=$(mktemp -d)
  trap 'rm -rf "$WORK"' EXIT
  (cd "$WORK" && npm pack --silent "@modelcontextprotocol/ext-apps@$VERSION" >/dev/null && tar xzf ./*.tgz)
  SRC="$WORK/package/dist/src/app-with-deps.js"
  got=$(shasum -a 256 "$SRC" | cut -d' ' -f1)
  if [ "$got" != "$SHA256" ]; then echo "sha256 mismatch: got $got, pinned $SHA256"; exit 1; fi
  $GEN bundle "$SRC" "$VERSION" extapps_bundle.ail
fi
