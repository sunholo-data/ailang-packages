#!/bin/sh
set -eu
: "${BENCH_BIN:?Set BENCH_BIN to the maintenance-bench command installed from sunholo/maintenance_bench@0.1.0}"
pilot_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
pilot_output=${1:?Supply a fresh absolute output directory}
case "$pilot_output" in /*) ;; *) echo 'Output directory must be absolute' >&2; exit 2;; esac
if [ -e "$pilot_output" ]; then echo 'Output directory already exists' >&2; exit 2; fi
mkdir "$pilot_output"
for pilot_key in parse docparse excelize calamine python-docx; do
  "$BENCH_BIN" analyse "$pilot_root/inputs/$pilot_key.snapshot.json" "$pilot_root/inputs/$pilot_key.annotations.json" "$pilot_root/inputs/$pilot_key.manifest.json" "$pilot_output/$pilot_key.json"
  "$BENCH_BIN" report "$pilot_root/inputs/$pilot_key.snapshot.json" "$pilot_root/inputs/$pilot_key.annotations.json" "$pilot_root/inputs/$pilot_key.manifest.json" "$pilot_output/$pilot_key.md"
  cmp "$pilot_root/reports/$pilot_key.json" "$pilot_output/$pilot_key.json"
  cmp "$pilot_root/reports/$pilot_key.md" "$pilot_output/$pilot_key.md"
done
echo 'All ten native reports reproduced byte for byte.'
