#!/usr/bin/env python3
"""Controller-only bridge from arbitrary retained native source to frozen oracles.

No metrics or provider parsing live here. The caller MUST withhold this report
from the model. A trusted wrapper is required unless development-unconfined is
explicit: supplying a prefix/digest is not itself containment qualification.
"""
import argparse
import hashlib
import types
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

IGNORED = {'.git', '.ailang', '__pycache__'}
RESOURCE_ASSERTIONS = {1: 87, 2: 123, 3: 152}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_files(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('candidate root must be a regular directory')
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'candidate symlink refused: {path.relative_to(root)}')
        if any(part in IGNORED for part in path.relative_to(root).parts):
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError('candidate non-regular file refused')
        if path.suffix not in ('.pyc', '.pyo'):
            files.append(path)
    return files


def canonical(value):
    """Match Go encoding/json.Marshal, including HTML and JS line separators."""
    text = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    for char, escaped in [('&', r'\u0026'), ('<', r'\u003c'), ('>', r'\u003e'),
                          ('\u2028', r'\u2028'), ('\u2029', r'\u2029')]:
        text = text.replace(char, escaped)
    return text.encode()


def source_digest(root):
    root = Path(root)
    rows = [dict(path=p.relative_to(root).as_posix(), sha256=digest(p),
                 executable=bool(p.stat().st_mode & 0o111)) for p in source_files(root)]
    return hashlib.sha256(canonical(rows)).hexdigest()


def load_module(path, name):
    # Compile exactly the digest-bound trusted source; ignore stale bytecode caches.
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class CandidateOutputError(Exception):
    pass


def candidate_json(text):
    try:
        return strict_json(text)
    except (ValueError, TypeError) as error:
        raise CandidateOutputError(str(error)) from error


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('non-finite JSON')))


def run_command(args, cwd, prefix, timeout):
    """Prefix convention: trusted-wrapper [policy args] -- executable argv..."""
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONSTARTUP')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    resolved_prefix = [part.replace('{runtimeRoot}', str(Path(cwd).parent)) for part in prefix]
    argv = resolved_prefix + ['--'] + args if prefix else args
    process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=os.name == 'posix')
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    finally:
        if os.name == 'posix':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.kill()
        if process.poll() is None:
            process.communicate()


def trusted_inventory(root, stage):
    if root.name == 'resource-ownership':
        paths = [root/'protocol.json', root/'oracle.py', root/'public_check.py', root/'fixtures/public.json']
        paths += [root/f'fixtures/s{stage}-{order}.json' for order in ('normal', 'reordered')]
    elif root.name == 'text-fidelity':
        paths = [root/'stages/contract.md', root/'qualify.py', root/f'fixtures/s{stage}.input.json',
                 root/f'fixtures/s{stage}.expected.json']
    else:
        raise ValueError('unknown native task family')
    paths += [root/'grade_candidate.py', Path(__file__).resolve()]
    for p in paths:
        if p.is_symlink() or not p.is_file():
            raise ValueError(f'missing or non-regular trusted input: {p}')
    return {str(p): digest(p) for p in paths}


def family_oracle(root):
    if root.name == 'resource-ownership':
        oracle = load_module(root/'oracle.py', 'maintenance_resource_oracle')
        public = load_module(root/'public_check.py', 'maintenance_resource_public')
        # An independently malformed schema must fail even with an empty schedule.
        with tempfile.TemporaryDirectory() as empty:
            try:
                oracle.validate({'schema': 'required', 'operations': []},
                                {'schema': 'altered', 'results': []}, Path(empty), 1)
            except AssertionError:
                return oracle, public
        raise ValueError('oracle weakening control accepted changed schema')
    oracle = load_module(root/'qualify.py', 'maintenance_text_oracle')
    if not oracle.oracle_canary() or oracle.oracle_canary(weak=True):
        raise ValueError('oracle weakening control failed')
    return oracle, None


def case_specs(root, stage, oracle):
    if root.name == 'resource-ownership':
        return [(f's{stage}-{order}', root/f'fixtures/s{stage}-{order}.json', None,
                 RESOURCE_ASSERTIONS[stage]) for order in ('normal', 'reordered')]
    expected_path = root/f'fixtures/s{stage}.expected.json'
    expected = strict_json(expected_path.read_text())
    if type(expected) is not list or len(expected) != {1: 8, 2: 15, 3: 21}[stage]:
        raise ValueError('trusted expected assertion inventory changed')
    return [(f's{stage}', root/f'fixtures/s{stage}.input.json', expected_path, len(expected))]


def evaluate_case(root, oracle, stage, spec, output, resources):
    name, input_path, expected_path, count = spec
    actual = candidate_json(output)
    row = dict(id=name, inputDigest=digest(input_path), expectedAssertions=count,
               outputDigest=hashlib.sha256(output.encode()).hexdigest(), mismatchIds=[],
               assertions=None, passed=False)
    if expected_path:
        row['expectedDigest'] = digest(expected_path)
        expected = strict_json(expected_path.read_text())
        try:
            row['mismatchIds'] = oracle.mismatches(actual, expected)
        except AssertionError as error:
            row['mismatchIds'] = ['result_shape']
            row['failure'] = str(error)
        row['assertions'] = count
        row['passed'] = not row['mismatchIds']
    else:
        try:
            row['assertions'] = oracle.validate(strict_json(input_path.read_text()), actual, resources, stage)
            if row['assertions'] != count:
                raise ValueError('oracle skipped or altered assertion inventory')
            row['passed'] = True
        except AssertionError as error:
            # Existing oracle stops at the first failure; unknown remaining count is explicit.
            row['mismatchIds'] = [name]
            row['failure'] = str(error)
    return row


def grade_candidate(root, source, language, stage, *, expected_source_digest,
                    command_prefix=None, containment_qualified=None,
                    development_unconfined=False, ailang_bin=None, timeout=30):
    root, source = Path(root).resolve(), Path(source)
    prefix = command_prefix or []
    report = dict(schema='maintenance.candidate-grade/1', family=root.name, language=language,
                  stage=stage, status='invalid_setup', compiled=False, cases=[],
                  publicCheckPassed=None, sourceDigest=None, candidateDigestAfter=None,
                  containment=dict(mode='development_unconfined' if development_unconfined else 'controller_wrapper',
                                   qualified=False, qualificationDigest=containment_qualified),
                  modelRun=False)
    inventory, source_hash, runtime_inputs = None, None, []
    work = None
    try:
        if language not in ('ailang', 'python') or type(stage) is not int or stage not in (1, 2, 3):
            raise ValueError('language and stage must name a native frozen task')
        if type(timeout) not in (int, float) or not 0 < timeout <= 30:
            raise ValueError('subprocess timeout must be in (0,30] seconds')
        if development_unconfined and (prefix or containment_qualified):
            raise ValueError('unconfined development and protected wrapper modes conflict')
        if not development_unconfined:
            if (type(prefix) is not list or not prefix or
                not all(type(s) is str and s for s in prefix) or
                not isinstance(containment_qualified, str) or len(containment_qualified) != 64 or
                any(c not in '0123456789abcdef' for c in containment_qualified)):
                raise ValueError('qualified trusted command prefix and digest required')
            if not Path(prefix[0]).is_absolute() or not Path(prefix[0]).is_file():
                raise ValueError('trusted wrapper must be an absolute existing executable')
            report['containment']['wrapperDigest'] = digest(prefix[0])
            report['containment']['qualificationStatus'] = 'external_controller_assertion_not_self_attested'
        inventory = trusted_inventory(root, stage)
        report['trustedInputs'] = inventory
        report['oracleDigest'] = digest(root/('oracle.py' if root.name == 'resource-ownership' else 'qualify.py'))
        report['protocolDigest'] = digest(root/('protocol.json' if root.name == 'resource-ownership' else 'stages/contract.md'))
        source_hash = source_digest(source)
        report['sourceDigest'] = source_hash
        if source_hash != expected_source_digest:
            raise ValueError('candidate source digest does not match retained checkpoint')
        binary = (ailang_bin or os.environ.get('AILANG_BIN', 'ailang')) if language == 'ailang' else sys.executable
        executable = shutil.which(binary)
        if not executable:
            raise ValueError(f'missing trusted runtime: {binary}')
        report['runtimeDigest'] = digest(executable)
        report['runtimePath'] = executable
        oracle, public = family_oracle(root)
        specs = case_specs(root, stage, oracle)
        with tempfile.TemporaryDirectory(prefix='maintenance-candidate-grade-') as temporary:
            work = Path(temporary)/'candidate'
            work.mkdir()
            for original in source_files(source):
                target = work/original.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
            if source_digest(work) != source_hash:
                raise ValueError('copied checkpoint digest mismatch')
            entry = 'main.ail' if language == 'ailang' else 'main.py'
            if not (work/entry).is_file():
                report.update(status='artifact_failure', failure='candidate entry missing')
                return report
            compile_args = [executable, 'check', '--package', '.'] if language == 'ailang' else [executable, '-m', 'py_compile', entry]
            code, _, error = run_command(compile_args, work, prefix, timeout)
            if code:
                report.update(status='artifact_failure', failure='native_compile_failed', processExit=code,
                              diagnosticDigest=hashlib.sha256(error.encode()).hexdigest())
                return report
            report['compiled'] = True
            base = [executable, 'run', '--verify-contracts', '--caps', 'IO,FS,Env', '--entry', 'main', entry] if language == 'ailang' else [executable, entry]
            if root.name == 'text-fidelity':
                base += [f's{stage}']
            if public:
                resources = Path(temporary)/'public-resources'; resources.mkdir()
                public_input = Path(temporary)/'public-input.json'
                shutil.copyfile(root/'fixtures/public.json', public_input)
                runtime_inputs.append((public_input, digest(public_input)))
                code, output, _ = run_command(base+[str(public_input), str(resources)], work, prefix, timeout)
                if code:
                    report.update(status='artifact_failure', failure='public_process_failed', processExit=code)
                    return report
                report['publicCheckPassed'] = bool(public.passes(candidate_json(output)))
            for spec in specs:
                resources = Path(temporary)/('resources-'+spec[0]); resources.mkdir()
                input_copy = Path(temporary)/(spec[0]+'-input.json')
                shutil.copyfile(spec[1], input_copy)
                runtime_inputs.append((input_copy, digest(input_copy)))
                args = base + [str(input_copy)] + ([str(resources)] if public else [])
                code, output, error = run_command(args, work, prefix, timeout)
                if code:
                    report.update(status='artifact_failure', failure='candidate_process_failed', processExit=code,
                                  diagnosticDigest=hashlib.sha256(error.encode()).hexdigest())
                    return report
                if any(p.is_symlink() for p in resources.rglob('*')):
                    raise CandidateOutputError('candidate resource symlink refused')
                report['cases'].append(evaluate_case(root, oracle, stage, spec, output, resources))
            for input_path, input_hash in runtime_inputs:
                if input_path.is_symlink() or digest(input_path) != input_hash:
                    raise ValueError('runtime input changed during grading')
            report['candidateDigestAfter'] = source_digest(work)
            if report['candidateDigestAfter'] != source_hash or source_digest(source) != source_hash:
                raise ValueError('candidate source changed during grading')
            if trusted_inventory(root, stage) != inventory:
                raise ValueError('trusted oracle/check/input source changed during grading')
            report['status'] = 'passed' if all(r['passed'] for r in report['cases']) and report['publicCheckPassed'] is not False else 'semantic_failure'
    except (OSError, ValueError, ImportError) as error:
        report.update(status='invalid_setup', failure=str(error))
    except (CandidateOutputError, TypeError, KeyError, AssertionError) as error:
        report.update(status='artifact_failure', failure=f'invalid_candidate_output: {error}')
    except subprocess.TimeoutExpired:
        report.update(status='artifact_failure', failure='candidate_timeout')
    finally:
        try:
            if inventory is not None and trusted_inventory(root, stage) != inventory:
                raise ValueError('trusted oracle/check/input source changed during grading')
            if source_hash is not None and source_digest(source) != source_hash:
                raise ValueError('original retained source changed during grading')
            for path, expected in runtime_inputs:
                if path.exists() and (path.is_symlink() or digest(path) != expected):
                    raise ValueError('runtime input changed during grading')
        except (OSError, ValueError) as error:
            report.update(status='invalid_setup', failure=str(error))
    return report


def main(family_root=None):
    parser = argparse.ArgumentParser(description=__doc__)
    if family_root is None:
        parser.add_argument('--family-root', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--language', choices=('ailang', 'python'), required=True)
    parser.add_argument('--stage', choices=(1, 2, 3), type=int, required=True)
    parser.add_argument('--expected-source-digest', required=True)
    parser.add_argument('--command-prefix-json', type=str, default='[]')
    parser.add_argument('--containment-qualified')
    parser.add_argument('--development-unconfined', action='store_true')
    parser.add_argument('--output', required=True, type=Path, help='new controller-owned output path')
    options = parser.parse_args()
    if options.output.exists():
        parser.error('grade output already exists')
    try:
        prefix = strict_json(options.command_prefix_json)
        report = grade_candidate(family_root or options.family_root, options.candidate,
            options.language, options.stage, expected_source_digest=options.expected_source_digest,
            command_prefix=prefix, containment_qualified=options.containment_qualified,
            development_unconfined=options.development_unconfined)
        # Create-only output: no check-then-truncate race or replacement.
        with options.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 2 if report['status'] == 'invalid_setup' else 0


if __name__ == '__main__':
    sys.exit(main())
