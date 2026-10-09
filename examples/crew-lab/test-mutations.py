#!/usr/bin/env python3
"""Test harness only: compile-success mutants must fail native behaviour controls.
No simulation/data pipeline or provider calls. Each copy has its own path dependency.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]
ailang = os.environ.get("AILANG", "ailang")
mutants = [
    ("confidence-bypass", "actor_policy.ail", [("gate(ChoiceA(c), threshold)", "gate(ChoiceA(c), 0.0)")]),
    ("consent-guard-bypass", "session.ail", [('s.policy == "consent" && not agreed', 'false')]),
    ("other-actor-delegation", "session.ail", [('b.worker != actor', 'false'), ('r.actor != b.worker', 'false')]),
    ("revision-rebase", "session.ail", [('r.revision != s.state.revision', 'false')]),
    ("clock-rebase", "session.ail", [('r.tick != s.state.tick', 'false'), ('s.state.tick >= r.expires', 'false')]),
    ("duplicate-resource-charge", "session.ail", [('then Ok(output(s, [])) else Err(HostFailure("altered/cancelled retry"))', 'then Ok(output({s | state: {s.state | resources: map(\\r. {r | available: r.available - 1, consumed: r.consumed + 1}, s.state.resources)}}, [])) else Err(HostFailure("altered/cancelled retry"))')]),
    ("unseen-evidence-context", "session.ail", [('perception(context, task, b.recipe)', 'perception({context | visible: s.state.evidence}, task, b.recipe)')]),
    ("trust-without-receipt", "session.ail", [('state: received.state }, events ++ step.events ++ received.events)', 'state: {received.state | relationships: map(\\r. if r.from != b.worker then {r | value: r.value - 8} else r, received.state.relationships)} }, events ++ step.events ++ received.events)')]),
]
results = []
for name, filename, edits in mutants:
    with tempfile.TemporaryDirectory(prefix="crew-mutant-") as temporary:
        workspace = Path(temporary)
        package = workspace / "examples/crew-lab"
        shutil.copytree(root / "examples/crew-lab", package)
        shutil.copytree(root / "packages/social-dynamics", workspace / "packages/social-dynamics")
        source = package / filename
        original = source.read_text()
        changed = original
        for old, new in edits:
            if changed.count(old) != 1:
                raise SystemExit(f"{name}: expected one mutation site, found {changed.count(old)}")
            changed = changed.replace(old, new, 1)
        source.write_text(changed)
        check = subprocess.run([ailang, "check", "--package", str(package)], capture_output=True, text=True)
        if check.returncode:
            raise SystemExit(f"{name}: did not compile\n{check.stdout}\n{check.stderr}")
        test = subprocess.run([ailang, "test", "--package", str(package)], capture_output=True, text=True)
        if test.returncode == 0:
            raise SystemExit(f"{name}: survived native behaviour controls")
        if "expected true, got false" not in test.stdout and "contract violation" not in test.stdout.lower():
            raise SystemExit(f"{name}: failed without behavioural assertion evidence\n{test.stdout}\n{test.stderr}")
        results.append({"mutation": name, "compiled": True, "killed": True})
        print(f"KILLED {name}", flush=True)
print(json.dumps({"schema": "crew-mutations/1", "mutations": results, "total": len(results)}))
