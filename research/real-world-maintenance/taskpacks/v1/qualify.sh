#!/bin/sh
set -eu
pack_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
pack_tmp=$(mktemp -d)
trap 'rm -rf "$pack_tmp"' EXIT
sh "$pack_root/resource-ownership/qualify.sh" --output "$pack_tmp/resource.json"
sh "$pack_root/text-fidelity/qualify.sh" --output "$pack_tmp/text.json"
python3 -m unittest discover -s "$pack_root/resource-ownership" -p oracle_test.py
python3 -m unittest discover -s "$pack_root/text-fidelity" -p oracle_test.py
python3 - "$pack_tmp" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);rows=[json.loads((p/n).read_text()) for n in ('resource.json','text.json')]
assert all(r['qualified'] for r in rows), 'unqualified native task family'
print('PASS: both native real-requirement families qualified; exposed development controls, no model campaign')
PY
