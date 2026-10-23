#!/bin/sh
set -eu
: "${AILANG_BIN:?Set AILANG_BIN to the validated v0.54.17 compiler}"
: "${BENCH_BIN:?Set BENCH_BIN to maintenance-bench installed from sunholo/maintenance_bench@0.1.0}"
mature_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mature_out=${1:?Supply a fresh absolute output directory}
case "$mature_out" in /*) ;; *) echo 'Use an absolute output directory' >&2; exit 2;; esac
if [ -e "$mature_out" ]; then echo 'Output directory exists' >&2; exit 2; fi
mkdir "$mature_out"
cd "$mature_root"
"$BENCH_BIN" validate inputs/combined.all.snapshot.json inputs/parse.annotations.json inputs/parse.manifest.json
"$AILANG_BIN" run --package-dir . --entry main --caps IO,FS,Env analysis.ail -- inputs/combined.all.snapshot.json inputs/combined.index.snapshot.json "$mature_out/mature-touches.json"
cmp reports/mature-touches.json "$mature_out/mature-touches.json"
"$BENCH_BIN" analyse inputs/parse.all.snapshot.json inputs/parse.annotations.json inputs/parse.manifest.json "$mature_out/parse-linked-repair.json"
"$BENCH_BIN" report inputs/parse.all.snapshot.json inputs/parse.annotations.json inputs/parse.manifest.json "$mature_out/parse-linked-repair.md"
cmp reports/parse-linked-repair.json "$mature_out/parse-linked-repair.json"
cmp reports/parse-linked-repair.md "$mature_out/parse-linked-repair.md"
for mature_key in parse excelize calamine; do
  "$BENCH_BIN" analyse "inputs/$mature_key.index.snapshot.json" "inputs/$mature_key.annotations.json" "inputs/$mature_key.manifest.json" "$mature_out/$mature_key.index.json"
  cmp "reports/$mature_key.index.json" "$mature_out/$mature_key.index.json"
done
echo 'All six study reports reproduced byte for byte.'
