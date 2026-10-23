#!/usr/bin/env python3
"""Offline external oracle over native outputs, not an implementation oracle.

Expected objects and mismatch identities were fixed before qualification runs.
A build/process failure is infrastructure failure and never satisfies a semantic
negative control. Every variant has its own copied source/build directory.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
# Independent expectation ledger: exact expected mismatches, never learned from runs.
CASES = [
    ("baseline", "starter", "baseline", "baseline", []),
    ("s1", "reference", "s1", "s1", []),
    ("s2", "reference", "s2", "s2", []),
    ("s3", "reference", "s3", "s3", []),
    ("noop_s1", "starter", "baseline", "s1", ["B1", "B3", "B4", "B5", "B8"]),
    ("noop_s2", "reference", "s1", "s2", ["C1", "C2", "C3", "C4", "C7", "E1", "E2", "E3", "E4", "E5", "E6", "E8"]),
    ("noop_s3", "reference", "s2", "s3", ["D1", "D2", "D3", "D4", "D5", "D6", "RC1", "RC2", "RC3", "RC4", "RC5", "RC6", "RC7", "RE1", "RE2", "RE3", "RE4", "RE5", "RE6", "RE7", "RE8"]),
    ("internal_drop", "reference", "internal_drop", "s1", ["B1", "B2", "B4", "B5", "B6", "B8"]),
    ("chunk_trim", "reference", "chunk_trim", "s2", ["C1", "C2", "C3", "C7", "E2"]),
    ("drop_cdata", "reference", "drop_cdata", "s3", ["D1", "D3"]),
    ("drop_field", "reference", "drop_field", "s3", ["D1", "D2", "D3", "D4", "D5", "D6", "RC1", "RC2", "RC3", "RC4", "RC5", "RC6", "RC7", "RE1", "RE2", "RE3", "RE4", "RE5", "RE6", "RE7", "RE8"]),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_digest(root):
    rows = [(str(p.relative_to(root)), digest(p)) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".ail", ".py", ".toml", ".lock")]
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def command(args, cwd):
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=30)
    if proc.returncode:
        raise RuntimeError(f"infrastructure command failed: {args!r}\n{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def mismatches(actual, expected, weak=False):
    if not isinstance(actual, list) or len(actual) != len(expected):
        raise AssertionError("oracle requires complete ordered result array")
    return [wanted["cell"] for got, wanted in zip(actual, expected) if not weak and got != wanted]


def oracle_canary(weak=False):
    expected = json.loads((ROOT / "fixtures/s1.expected.json").read_text())
    changed = copy.deepcopy(expected)
    changed[0]["text"] = "AB"  # Known loss of the required internal space.
    return mismatches(changed, expected, weak=weak) == ["B1"]


def qualify():
    ailang = os.environ.get("AILANG_BIN", "ailang")
    tool = shutil.which(ailang)
    if not tool:
        raise RuntimeError("AILANG runtime unavailable")
    runtime = command([ailang, "version"], ROOT).strip()
    rows = []
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="maintenance-text-fidelity-") as temporary:
        for language in ("ailang", "python"):
            for name, source, mode, fixture, wanted_mismatches in CASES:
                original = ROOT / source / language
                work = Path(temporary) / f"{language}-{name}"
                shutil.copytree(original, work, ignore=shutil.ignore_patterns("__pycache__"))
                if language == "ailang":
                    command([ailang, "lock", "--check"], work)
                    command([ailang, "check", "--package", "."], work)
                    args = [ailang, "run", "--verify-contracts", "--caps", "IO,FS,Env", "--entry", "main", "main.ail", mode]
                else:
                    command([sys.executable, "-m", "py_compile", "main.py"], work)
                    args = [sys.executable, "main.py", mode]
                output = command(args + [str(ROOT / f"fixtures/{fixture}.input.json")], work)
                actual = json.loads(output)
                expected = json.loads((ROOT / f"fixtures/{fixture}.expected.json").read_text())
                observed = mismatches(actual, expected)
                if observed != wanted_mismatches:
                    raise AssertionError(f"{language}/{name}: expected mismatches {wanted_mismatches}; observed {observed}")
                rows.append(dict(language=language, variant=name, stage=fixture, sourceDigest=source_digest(original),
                                 inputDigest=digest(ROOT / f"fixtures/{fixture}.input.json"),
                                 expectedDigest=digest(ROOT / f"fixtures/{fixture}.expected.json"),
                                 built=True, processExit=0, assertions=len(expected),
                                 expectedMismatchIds=wanted_mismatches, observedMismatchIds=observed,
                                 expectationSatisfied=True))
    if not oracle_canary() or oracle_canary(weak=True):
        raise AssertionError("independent oracle weakening canary failed")
    return dict(schema="maintenance.qualification/1", family="text-fidelity/v1", role="public_development_control",
                qualified=True, modelRun=False, protocolDigest=digest(ROOT / "stages/contract.md"),
                oracleDigest=digest(__file__), ailangVersion=runtime, ailangBinaryDigest=digest(tool),
                pythonVersion=sys.version.split()[0],
                referenceAssertions=sum(r["assertions"] for r in rows if not r["expectedMismatchIds"]),
                expectedSemanticFailures=sum(len(r["expectedMismatchIds"]) for r in rows),
                oracleWeakeningRejected=True, rows=rows,
                durationMs=round((time.perf_counter() - started) * 1000),
                limits="30 second subprocess cap; finite frozen fixtures; no model/network calls")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="new output path; default stdout")
    options = parser.parse_args()
    try:
        report = qualify()
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if options.output:
            with options.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        else:
            print(rendered, end="")
    except (AssertionError, RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f"F2 qualification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
