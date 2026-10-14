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
    ("confidence-bypass", "packages/crew-core/actor_policy.ail", [("gate(ChoiceA(c), threshold)", "gate(ChoiceA(c), 0.0)")]),
    ("consent-guard-bypass", "packages/crew-core/session.ail", [('s.command == "consent" && not agreed', 'false')]),
    ("other-actor-delegation", "packages/crew-core/session.ail", [('b.worker != actor', 'false'), ('r.actor != b.worker', 'false')]),
    ("revision-rebase", "packages/crew-core/session.ail", [('r.revision != s.state.revision', 'false')]),
    ("clock-rebase", "packages/crew-core/session.ail", [('r.tick != s.state.tick', 'false'), ('s.state.tick >= r.expires', 'false')]),
    ("duplicate-resource-charge", "packages/crew-core/session.ail", [('then Ok(output(s, [])) else Err(HostFailure("altered/cancelled retry"))', 'then Ok(output({s | state: {s.state | resources: map(\\r. {r | available: r.available - 1, consumed: r.consumed + 1}, s.state.resources)}}, [])) else Err(HostFailure("altered/cancelled retry"))')]),
    ("unseen-evidence-context", "packages/crew-core/session.ail", [('perception(context, task, b.recipe)', 'perception({context | visible: s.state.evidence}, task, b.recipe)')]),
    ("trust-without-receipt", "packages/crew-core/session.ail", [('state: received.state }, events ++ step.events ++ received.events)', 'state: {received.state | relationships: map(\\r. if r.from != b.worker then {r | value: r.value - 8} else r, received.state.relationships)} }, events ++ step.events ++ received.events)')]),
]
results = []
for name, filename, edits in mutants:
    with tempfile.TemporaryDirectory(prefix="crew-mutant-") as temporary:
        workspace = Path(temporary)
        package = workspace / "examples/crew-lab"
        shutil.copytree(root / "examples/crew-lab", package)
        shutil.copytree(root / "packages/social-dynamics", workspace / "packages/social-dynamics")
        shutil.copytree(root / "packages/content-library", workspace / "packages/content-library")
        shutil.copytree(root / "packages/terminal-ui", workspace / "packages/terminal-ui")
        shutil.copytree(root / "packages/crew-core", workspace / "packages/crew-core")
        core = workspace / "packages/crew-core"
        # No mutant touches cohorts.ail; its 48 tests run in core-tests, not once per mutant.
        # The slow auto-run concerns tests (about a minute) also run once, in core-tests;
        # every mutant here is killed without them.
        (core / "cohorts_test.ail").unlink()
        (core / "concerns_test.ail").unlink()
        source = workspace / filename
        original = source.read_text()
        changed = original
        for old, new in edits:
            if changed.count(old) != 1:
                raise SystemExit(f"{name}: expected one mutation site, found {changed.count(old)}")
            changed = changed.replace(old, new, 1)
        source.write_text(changed)
        # crew_core holds the host invariants; the app's suite runs only if a mutant survives it.
        outputs = []
        for target in (core, package):
            check = subprocess.run([ailang, "check", "--package", str(target)], capture_output=True, text=True)
            if check.returncode:
                raise SystemExit(f"{name}: did not compile in {target.name}\n{check.stdout}\n{check.stderr}")
            outputs.append(subprocess.run([ailang, "test", "--package", ".", "--allow-skips"], cwd=target, capture_output=True, text=True))
            if outputs[-1].returncode:
                break
        if all(t.returncode == 0 for t in outputs):
            raise SystemExit(f"{name}: survived native behaviour controls")
        if not any(t.returncode and ("expected true, got false" in t.stdout or "contract violation" in t.stdout.lower()) for t in outputs):
            raise SystemExit(f"{name}: failed without behavioural assertion evidence\n" + "\n".join(t.stdout for t in outputs))
        results.append({"mutation": name, "compiled": True, "killed": True})
        print(f"KILLED {name}", flush=True)
print(json.dumps({"schema": "crew-mutations/1", "mutations": results, "total": len(results)}))
