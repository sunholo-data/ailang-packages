#!/usr/bin/env python3
"""Freeze existing public task assets for no-model adapter development.

This only reads files and writes new execution documents. It does not invoke a
model, resolve credentials, execute a toolchain, or qualify containment. Version
files must be independently collected, and remain declarations until launch.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[4]
PACKAGE_REVISION = "a4163559a2e20dddc1a1bb0869a06e42372994a1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def ref(path):
    path = path.resolve(strict=True)
    return {"path": str(path.relative_to(REPOSITORY)), "sha256": sha(path.read_bytes())}


def relative_ref(path):
    import os
    value = ref(path)
    value["path"] = os.path.relpath(path, HERE)
    return value


def canonical(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()


def write_new(path, value):
    raw = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with path.open("x") as output:
        output.write(raw)


def build(ailang_evidence, python_evidence):
    evidence = {"ailang": ailang_evidence, "python": python_evidence}
    tools = []
    for language, path in evidence.items():
        value = json.loads(path.read_text())
        if not value.get("version") or not value.get("command"):
            raise ValueError("toolchain evidence requires version and command")
        tools.append({"language": language, "command": value["command"],
                      "version": value["version"], "evidence": relative_ref(path)})
    settings = HERE / "development.settings.json"
    settings_ref = relative_ref(settings)
    plan = {"schema": "maintenance.trajectory/2", "protocolId": "maintenance-development-adapter-v1",
            "role": "instrument_control", "model": "scripted-control", "harness": "scripted",
            "settingsDigest": settings_ref["sha256"], "retention": "fresh-session-owned-artifacts",
            "treatment": "native-tools", "leftLanguage": "ailang", "rightLanguage": "python",
            "trajectories": []}
    bindings = []
    for family in ("resource-ownership", "text-fidelity"):
        source = HERE.parent / family
        request_names = (["1-file-backing.md", "2-batch-cap.md", "3-release.md"]
                         if family == "resource-ownership" else ["s1.md", "s2.md", "s3.md"])
        grader = source / "grade_candidate.py"
        trusted = [grader, HERE.parent / "candidate_grade.py"] + [source / name for name in
                               (["oracle.py", "public_check.py", "protocol.json"]
                                if family == "resource-ownership" else ["qualify.py", "taskpack.json"])]
        trusted += sorted((source / "fixtures").glob("*.json"))
        oracle_files = [relative_ref(p) for p in trusted]
        for repeat in (1, 2):
            for language in ("ailang", "python"):
                starter = source / "starter" / language
                assets = []
                for path in sorted(starter.rglob("*")):
                    if not path.is_file() or any(part in (".ailang", "__pycache__") for part in path.parts):
                        continue
                    if path.is_symlink():
                        raise ValueError(f"symlink starter: {path}")
                    item = relative_ref(path)
                    assets.append({"path": item["path"], "destination": path.relative_to(starter).as_posix(),
                                   "sha256": item["sha256"], "executable": bool(path.stat().st_mode & 0o111)})
                checkpoint = [{"path": a["destination"], "sha256": a["sha256"], "executable": a["executable"]}
                              for a in sorted(assets, key=lambda a: a["destination"])]
                ident = f"{family}-{repeat}-{language}"
                stages = []
                stage_bindings = []
                for number, request_name in enumerate(request_names, 1):
                    request = relative_ref(source / "stages" / request_name)
                    stage = f"S{number}"
                    stages.append({"id": stage, "requirementDigest": request["sha256"],
                                   "oracleDigest": oracle_files[0]["sha256"]})
                    command = ["python3", str(grader.relative_to(REPOSITORY)), "--candidate", "{candidate}",
                               "--language", language, "--stage", str(number), "--output", "{output}",
                               "--expected-source-digest", "{candidateDigest}", "--command-prefix-json",
                               "{commandPrefixJSON}", "--containment-qualified", "{containmentDigest}"]
                    # Resolve argv[1] via Files[0] at the trusted host bridge;
                    # no controller path or oracle output is sent to the model.
                    binding = {"command": command, "files": oracle_files}
                    stage_bindings.append({"id": stage, "request": request,
                                           "publicCheck": binding, "oracle": binding})
                tool = next(t for t in tools if t["language"] == language)
                plan["trajectories"].append({"id": ident, "family": family, "variant": "public-development-v1",
                                             "repeat": repeat, "language": language,
                                             "starterDigest": sha(canonical(checkpoint)),
                                             "nativeToolDigest": tool["evidence"]["sha256"], "stages": stages})
                bindings.append({"id": ident, "starter": assets,
                                 "carryFiles": [a["destination"] for a in assets] + ["HANDOVER.md"],
                                 "stages": stage_bindings})
    return plan, {"schema": "maintenance.execution/1", "packageSourceRevision": PACKAGE_REVISION,
                  "packageRoot": "../../../../../packages/maintenance-bench", "settings": settings_ref,
                  "analysis": relative_ref(REPOSITORY / "packages/maintenance-bench/ledger_report.ail"),
                  "toolchains": tools, "trajectories": bindings, "protectedRoots": ["../../../../.."],
                  "limits": {"maxTrajectories": 8, "maxStages": 24, "maxStageSeconds": 120,
                             "maxCampaignSeconds": 3600, "maxRequests": 240, "maxTokens": 240000},
                  "isolation": {"backend": "pi", "status": "unqualified",
                                "policyDigest": sha(b"unqualified-development-control-policy-v1")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ailang-evidence", type=Path, required=True)
    parser.add_argument("--python-evidence", type=Path, required=True)
    args = parser.parse_args()
    plan, manifest = build(args.ailang_evidence, args.python_evidence)
    plan_path = HERE / "development.plan.json"
    write_new(plan_path, plan)
    manifest["plan"] = relative_ref(plan_path)
    write_new(HERE / "development.example.json", manifest)


if __name__ == "__main__":
    main()
