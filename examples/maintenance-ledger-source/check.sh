#!/bin/sh
set -eu
AILANG_BIN=${AILANG_BIN:-ailang}
consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
consumer_tmp=$(mktemp -d)
trap 'rm -rf "$consumer_tmp"' EXIT
cd "$consumer_root"
fixtures=../../packages/maintenance-bench/assets/fixtures/ledger
"$AILANG_BIN" lock --check
"$AILANG_BIN" run --caps IO,FS,Env --entry main main.ail "$fixtures/plan.json" "$fixtures/economic-runs.json" "$fixtures/economic-usage.json" source-consumer-control "$consumer_tmp/report.json"
python3 - "$consumer_tmp/report.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]));assert r['packageVersion']=='0.2.0' and r['role']=='instrument_control'
s=r['data']['summary'];assert s['scheduledTrajectories']==8 and s['scheduledStages']==24
c=r['data']['comparison'];assert c['costPerSuccessDeltaMicros']==-22500 and c['freshInputTokenDelta']==-550 and c['freshTokenDelta']==-540
print('PASS: source-path native consumer: 8/24 control; -22500 micros, -550 input, -540 input+generated')
PY
if "$AILANG_BIN" run --caps IO,FS,Env --entry main main.ail "$fixtures/plan.json" "$fixtures/economic-runs.json" "$fixtures/economic-usage.json" source-consumer-control "$consumer_tmp/report.json" >/dev/null 2>&1; then
 echo 'ERROR: existing report overwritten' >&2; exit 1
fi
