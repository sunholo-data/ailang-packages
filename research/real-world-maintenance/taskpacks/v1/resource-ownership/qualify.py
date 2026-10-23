"""Offline control runner; candidate compilation/launch failures never count as oracle kills."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from oracle import validate
from public_check import passes as public_check

HERE = Path(__file__).resolve().parent
AILANG = os.environ.get("AILANG_BIN", "ailang")


def require_semantic_rejection(check):
    try:
        check()
    except AssertionError as error:
        return str(error)
    raise AssertionError("weakened oracle accepted prescribed negative control")


def run_checked(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f"infrastructure failure: {command}: {result.stdout}\n{result.stderr}")
    return result.stdout


def digest_tree(path):
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file() and '__pycache__' not in p.parts and '.ailang' not in p.parts and p.suffix != '.pyc':
            h.update(str(p.relative_to(path)).encode()); h.update(p.read_bytes())
    return h.hexdigest()


def run_candidate(source, language, stage, fixture, negative=False, mutation=None):
    overall_start = time.monotonic()
    source_digest = digest_tree(source)
    with tempfile.TemporaryDirectory(prefix=f"f1-{language}-s{stage}-") as temp:
        temp = Path(temp)
        program = temp / 'program'; shutil.copytree(source, program, ignore=shutil.ignore_patterns('.ailang', '__pycache__', '*.pyc'))
        resources = temp / 'resources'; resources.mkdir()
        if mutation:
            filename, before, after = mutation
            p = program / filename
            text = p.read_text()
            assert before in text, f"mutant anchor absent: {before}"
            p.write_text(text.replace(before, after))
        effective_digest = digest_tree(program)
        command = [sys.executable, str(program / 'main.py')] if language == 'python' else [AILANG, 'run', '--verify-contracts', '--caps', 'IO,FS,Env', '--entry', 'main', str(program / 'main.ail')]
        compile_start = time.monotonic()
        if language == 'ailang':
            run_checked([AILANG, 'check', '--package', '.'], program)
        else:
            run_checked([sys.executable, '-m', 'py_compile', 'main.py'], program)
        compile_seconds = time.monotonic() - compile_start
        public_start = time.monotonic()
        public_root = temp / 'public-resources'; public_root.mkdir()
        visible = public_check(json.loads(run_checked(command + [str(HERE / 'fixtures/public.json'), str(public_root)], program)))
        public_seconds = time.monotonic() - public_start
        if not negative:
            assert visible, 'public check failed for reference'
        start = time.monotonic()
        raw = run_checked(command + [str(fixture), str(resources)], program)
        elapsed = time.monotonic() - start
        response = json.loads(raw)
        request = json.loads(fixture.read_text())
        oracle_start = time.monotonic()
        if negative:
            failure_reason = require_semantic_rejection(lambda: validate(request, response, resources, stage))
            assertions = None
        else:
            assertions = validate(request, response, resources, stage)
            failure_reason = None
        return {"language": language, "stage": stage, "source": str(source.relative_to(HERE)), "compiled": True, "exitCode": 0, "oracleFailure": failure_reason, "sourceDigest": effective_digest, "baseSourceDigest": source_digest, "fixtureDigest": hashlib.sha256(fixture.read_bytes()).hexdigest(), "visibleCheckPassed": visible, "mutation": {"file": mutation[0], "before": mutation[1], "after": mutation[2]} if mutation else None, "control": mutation[0] if mutation else ('no-op' if negative else 'reference'), "expected": "semantic_rejection" if negative else "pass", "actual": "semantic_rejection" if negative else "pass", "assertions": assertions, "elapsedSeconds": elapsed, "compileSeconds": compile_seconds, "publicCheckSeconds": public_seconds, "oracleSeconds": time.monotonic() - oracle_start, "wallSeconds": time.monotonic() - overall_start, "peakMemoryBytes": None, "peakMemoryStatus": "not_collected_per_process"}



def mutations(language):
    if language == 'python':
        return [
            (0, ('main.py', 'base64.b64encode(payload).decode()', 'base64.b64encode(b"corrupt").decode()')),
            (1, ('main.py', 'hashlib.sha256(doc.encode()).hexdigest()', '"global"')),
            (2, ('main.py', 'if sum(map(len, payloads)) > op["cap"]:', 'if False:')),
            (3, ('main.py', 'del active[op["doc"]]', 'active.clear()')),
        ]
    return [
        (0, ('engine.ail', 'data: im.data', 'data: "Y29ycnVwdA=="')),
        (1, ('engine.ail', '${sha256Hex(doc)}', 'global')),
        (2, ('engine.ail', 'not withinCap(total, limit)', 'false')),
        (3, ('engine.ail', 'filter(\\id. id != doc, state.active)', '[]')),
    ]


def qualify():
    # References and mutations populated only after the frozen protocol/fixtures/oracle.
    records = []
    for language in ('ailang', 'python'):
        for stage in range(4):
            source = HERE / ('starter' if stage == 0 else f'references/s{stage}') / language
            for order in ('normal', 'reordered'):
                records.append(run_candidate(source, language, stage, HERE / f'fixtures/s{stage}-{order}.json'))
        for target in (1, 2, 3):
            prior = HERE / ('starter' if target == 1 else f'references/s{target-1}') / language
            records.append(run_candidate(prior, language, target, HERE / f'fixtures/s{target}-normal.json', negative=True))
        for stage, mutation in mutations(language):
            source = HERE / ('starter' if stage == 0 else f'references/s{stage}') / language
            records.append(run_candidate(source, language, stage, HERE / f'fixtures/s{stage}-normal.json', negative=True, mutation=mutation))
    return records



def native_packages():
    evidence = []
    for stage in range(4):
        source = HERE / ('starter' if stage == 0 else f'references/s{stage}') / 'ailang'
        run_checked([AILANG, 'lock', '--check'], source)
        run_checked([AILANG, 'fmt', '--check', *[str(p) for p in sorted(source.rglob('*.ail'))]], source)
        run_checked([AILANG, 'check', '--package', '.'], source)
        tests = json.loads(run_checked([AILANG, 'test', '--package', '.', '--json'], source))
        assert tests['passed_tests'] >= 3 and tests['failed_tests'] == 0 and tests['skipped_tests'] == 0
        smoke = run_checked([AILANG, 'run', '--caps', 'IO', '--entry', 'main', '_smoke.ail'], source)
        proof = json.loads(run_checked([AILANG, 'verify', '--json', '--timeout', '2s', 'engine.ail'], source))
        assert proof['counterexample'] == 0 and proof['errors'] == 0
        evidence.append({'stage': stage, 'sourceDigest': digest_tree(source), 'namedTestsPassed': tests['passed_tests'], 'namedTestsFailed': tests['failed_tests'], 'smokePassed': True, 'smokeOutput': smoke, 'smtVerified': proof['verified'], 'smtCounterexamples': proof['counterexample'], 'smtSkipped': proof['skipped'], 'smtErrors': proof['errors'], 'qualityStatus': 'separate-check-not-run-by-offline-qualifier'})
    return evidence


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path); args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError(f"qualification output exists: {args.output}")
    native = native_packages()
    records = qualify()
    result = {"schema": "maintenance.task-qualification/1", "family": "resource-ownership", "role": "development-qualification", "protocolDigest": hashlib.sha256((HERE/'protocol.json').read_bytes()).hexdigest(), "oracleDigest": hashlib.sha256((HERE/'oracle.py').read_bytes()).hexdigest(), "qualifierDigest": hashlib.sha256((HERE/'qualify.py').read_bytes()).hexdigest(), "publicCheckDigest": hashlib.sha256((HERE/'public_check.py').read_bytes()).hexdigest(), "runtime": run_checked([AILANG, 'version'], HERE).strip(), "runtimeBinarySHA256": hashlib.sha256(Path(shutil.which(AILANG)).resolve().read_bytes()).hexdigest(), "python": sys.version.split()[0], "nativePackages": native, "records": records, "positiveRuns": sum(r["actual"] == "pass" for r in records), "negativeControlsKilled": sum(r["actual"] == "semantic_rejection" for r in records), "qualified": True}
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as output:
            output.write(text)
    else:
        print(text, end='')


if __name__ == '__main__': main()
