#!/bin/bash
# Node simulation of the widget's after-upload flow (tests/widget_sim.mjs):
# mocked ext-apps App, DOM, fetch. Fails loudly when node is absent.
set -uo pipefail
cd "$(dirname "$0")/.."
command -v node >/dev/null || { echo "FAIL: node not found; the widget simulation needs it"; exit 1; }
node tests/widget_sim.mjs assets/widget.js
