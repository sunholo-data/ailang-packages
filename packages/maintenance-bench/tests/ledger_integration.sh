#!/bin/sh
set -eu
AILANG_BIN=${AILANG_BIN:-ailang}
ledger_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ledger_tmp=$(mktemp -d)
trap 'rm -rf "$ledger_tmp"' EXIT
cd "$ledger_root"
fixture=assets/fixtures/ledger
"$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail validate "$fixture/plan.json" "$fixture/runs.json" "$fixture/empty-usage.json"
"$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail runs "$fixture/plan.json" "$fixture/runs.json" "$fixture/empty-usage.json" fixture-runtime "$ledger_tmp/runs.json"
"$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail runs "$fixture/plan.json" "$fixture/runs.json" "$fixture/empty-usage.json" fixture-runtime "$ledger_tmp/replay.json"
cmp "$ledger_tmp/runs.json" "$ledger_tmp/replay.json"
"$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail runs "$fixture/plan.json" "$fixture/economic-runs.json" "$fixture/economic-usage.json" fixture-runtime "$ledger_tmp/economic.json"
"$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail index assets/fixtures/analytical.snapshot.json "$fixture/index.json" fixture-runtime "$ledger_tmp/index.json"
"$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail cards-md "$fixture/cards.json" fixture-runtime "$ledger_tmp/cards.md"
python3 - "$fixture" "$ledger_tmp" <<'PY'
import json,sys
from pathlib import Path
f,t=map(Path,sys.argv[1:]);got=json.loads((t/'runs.json').read_text());expected=json.loads((f/'expected.json').read_text())
assert got['role']=='instrument_control'
for key,value in expected.items():assert got['data']['summary'][key]==value,(key,got['data']['summary'][key],value)
c=got['data']['comparison'];assert c['costStatus']!='available' and c['costPerSuccessNumerator'] is None
actual=json.loads((t/'economic.json').read_text())['data']['comparison'];want=json.loads((f/'economic-expected.json').read_text())
assert actual['left']['usage']['costMicros']['total']==150000
assert actual['right']['usage']['costMicros']['total']==240000
assert actual['costPerSuccessDeltaMicros']==-22500 and actual['freshTokenDelta']==-540 and actual['freshInputTokenDelta']==-550
assert json.loads((t/'index.json').read_text())['data']['indexSelected']==1
assert 'reproduced' in (t/'cards.md').read_text()
print('PASS: independent staged counts, replay bytes, exact economics, scoped index and roadmap cards')
PY
if "$AILANG_BIN" run --caps IO,FS,Env --entry main ledger_cli.ail runs "$fixture/plan.json" "$fixture/runs.json" "$fixture/empty-usage.json" fixture-runtime "$ledger_tmp/runs.json" >/dev/null 2>&1; then
 echo 'ERROR: existing evidence output overwritten' >&2;exit 1
fi
