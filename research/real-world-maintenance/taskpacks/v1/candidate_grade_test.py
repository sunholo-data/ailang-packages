"""Retained-candidate bridge controls; no model or provider calls."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('candidate_grade', ROOT / 'candidate_grade.py')
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)


class CandidateBridge(unittest.TestCase):
    def run_grade(self, family='text-fidelity', language='python', stage=1, source=None, **kwargs):
        source = source or (ROOT / family / ('reference' if family == 'text-fidelity' else f'references/s{stage}') / language)
        return grade.grade_candidate(ROOT / family, source, language, stage,
                                     expected_source_digest=grade.source_digest(source),
                                     development_unconfined=True, **kwargs)

    def test_native_reference_is_not_replaced(self):
        report = self.run_grade()
        self.assertEqual(report['status'], 'passed')
        self.assertEqual(report['sourceDigest'], report['candidateDigestAfter'])
        self.assertEqual(report['cases'][0]['assertions'], 8)
        self.assertEqual(report['cases'][0]['mismatchIds'], [])
        self.assertEqual(report['containment']['mode'], 'development_unconfined')
        self.assertFalse(report['containment']['qualified'])

    def test_actual_mutation_is_semantic_failure(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/'candidate'
            shutil.copytree(ROOT/'text-fidelity/reference/python', target)
            p=target/'main.py'; p.write_text(p.read_text().replace('value.strip(ASCII_EDGE) if stage > 0', 'value.replace(" ", "") if stage > 0'))
            report=self.run_grade(source=target)
            self.assertEqual(report['status'], 'semantic_failure')
            self.assertIn('B1', report['cases'][0]['mismatchIds'])
            self.assertTrue(report['compiled'])

    def test_syntax_failure_is_not_semantic_mutant(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d);(target/'main.py').write_text('def broken(:\n')
            report=self.run_grade(source=target)
            self.assertEqual(report['status'],'artifact_failure')
            self.assertFalse(report['compiled'])
            self.assertEqual(report['cases'],[])

    def test_missing_entry_is_artifact_failure(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_grade(source=Path(d))['status'],'artifact_failure')

    def test_missing_trusted_fixture_is_invalid_setup(self):
        with tempfile.TemporaryDirectory() as d:
            family=Path(d)/'text-fidelity';shutil.copytree(ROOT/'text-fidelity', family)
            (family/'fixtures/s1.expected.json').unlink()
            report=grade.grade_candidate(family,family/'reference/python','python',1,
                expected_source_digest=grade.source_digest(family/'reference/python'), development_unconfined=True)
            self.assertEqual(report['status'],'invalid_setup')
            self.assertFalse(report['compiled'])

    def test_changed_source_identity_is_invalid_setup(self):
        source=ROOT/'text-fidelity/reference/python'
        report=grade.grade_candidate(ROOT/'text-fidelity',source,'python',1,
            expected_source_digest='0'*64, development_unconfined=True)
        self.assertEqual(report['status'],'invalid_setup')

    def test_protected_mode_requires_wrapper_and_qualification(self):
        source=ROOT/'text-fidelity/reference/python'
        report=grade.grade_candidate(ROOT/'text-fidelity',source,'python',1,
            expected_source_digest=grade.source_digest(source))
        self.assertEqual(report['status'],'invalid_setup')
        self.assertFalse(report['compiled'])

    def test_symlink_candidate_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d);(target/'main.py').symlink_to(ROOT/'text-fidelity/reference/python/main.py')
            with self.assertRaises(ValueError): grade.source_digest(target)

    def test_resource_stage_retains_all_current_obligations(self):
        report=self.run_grade(family='resource-ownership',stage=3)
        self.assertEqual(report['status'],'passed')
        self.assertEqual(len(report['cases']),2)
        self.assertTrue(report['publicCheckPassed'])
        self.assertTrue(all(row['assertions'] > 30 for row in report['cases']))

    def test_source_changes_during_grade_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'candidate';shutil.copytree(ROOT/'text-fidelity/reference/python',target)
            p=target/'main.py';p.write_text(p.read_text().replace('import json','import json\nfrom pathlib import Path\nPath(__file__).write_text("changed")'))
            self.assertEqual(self.run_grade(source=target)['status'],'invalid_setup')

    def test_typed_malformed_output_is_artifact_failure(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d);(target/'main.py').write_text('print("not json")')
            self.assertEqual(self.run_grade(source=target)['status'],'artifact_failure')

    def test_missing_runtime_is_invalid_setup(self):
        report=self.run_grade(ailang_bin='/missing/ailang',language='ailang')
        self.assertEqual(report['status'],'invalid_setup')

    def test_all_native_reference_stages(self):
        if not shutil.which('ailang'):
            self.skipTest('AILANG not installed; native integration requires it')
        for family in ('resource-ownership','text-fidelity'):
            for language in ('ailang','python'):
                for stage in (1,2,3):
                    with self.subTest(family=family,language=language,stage=stage):
                        report=self.run_grade(family=family,language=language,stage=stage)
                        self.assertEqual(report['status'],'passed',report)
                        self.assertTrue(report['compiled'])
                        self.assertTrue(all(row['assertions']==row['expectedAssertions'] for row in report['cases']))

    def test_weakened_oracle_is_invalid_setup(self):
        with tempfile.TemporaryDirectory() as d:
            family=Path(d)/'resource-ownership';shutil.copytree(ROOT/'resource-ownership',family)
            (family/'oracle.py').write_text('def validate(*args): return 87\n')
            source=family/'references/s1/python'
            report=grade.grade_candidate(family,source,'python',1,
                expected_source_digest=grade.source_digest(source),development_unconfined=True)
            self.assertEqual(report['status'],'invalid_setup')
            self.assertIn('weakening',report['failure'])

    def test_skipped_assertions_are_invalid_setup(self):
        with tempfile.TemporaryDirectory() as d:
            family=Path(d)/'resource-ownership';shutil.copytree(ROOT/'resource-ownership',family)
            p=family/'oracle.py';p.write_text(p.read_text().replace('return count','return 1'))
            source=family/'references/s1/python'
            report=grade.grade_candidate(family,source,'python',1,
                expected_source_digest=grade.source_digest(source),development_unconfined=True)
            self.assertEqual(report['status'],'invalid_setup')
            self.assertIn('assertion inventory',report['failure'])

    def test_source_digest_includes_executable_bit(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'main.py';p.write_text('print(1)');p.chmod(0o644)
            before=grade.source_digest(root);p.chmod(0o755)
            self.assertNotEqual(before,grade.source_digest(root))

    def test_duplicate_output_keys_are_artifact_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'main.py').write_text("print('[{\"cell\":1,\"cell\":2}]')")
            self.assertEqual(self.run_grade(source=root)['status'],'artifact_failure')

    def test_mutated_runtime_input_is_invalid_setup(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(ROOT/'text-fidelity/reference/python',root/'candidate')
            p=root/'candidate/main.py';p.write_text(p.read_text().replace('requests = json.load(stream)', 'requests = json.load(stream)\n        open(sys.argv[2], "w").write("[]")'))
            self.assertEqual(self.run_grade(source=root/'candidate')['status'],'invalid_setup')

    def test_trusted_oracle_overwrite_is_invalid_setup(self):
        with tempfile.TemporaryDirectory() as d:
            family=Path(d)/'text-fidelity';shutil.copytree(ROOT/'text-fidelity',family)
            source=family/'reference/python';p=source/'main.py'
            attack=f"import json\nfrom pathlib import Path\nPath({str(family/'qualify.py')!r}).write_text('altered')"
            p.write_text(p.read_text().replace('import json',attack))
            report=grade.grade_candidate(family,source,'python',1,
                expected_source_digest=grade.source_digest(source),development_unconfined=True)
            self.assertEqual(report['status'],'invalid_setup')
            self.assertIn('trusted',report['failure'])

    def test_timeout_is_artifact_failure_not_semantic_failure(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d);(source/'main.py').write_text('while True: pass')
            report=self.run_grade(source=source,timeout=0.1)
            self.assertEqual(report['status'],'artifact_failure')
            self.assertEqual(report['failure'],'candidate_timeout')

    def test_prefix_forwarding_requires_double_dash(self):
        if __import__('os').name != 'posix':
            self.skipTest('POSIX wrapper example; Windows uses its own qualified wrapper')
        with tempfile.TemporaryDirectory() as d:
            wrapper=Path(d)/'wrapper';wrapper.write_text('#!/bin/sh\n[ "$1" = "--" ] || exit 99\nshift\nexec "$@"\n');wrapper.chmod(0o755)
            source=ROOT/'text-fidelity/reference/python'
            report=grade.grade_candidate(ROOT/'text-fidelity',source,'python',1,
                expected_source_digest=grade.source_digest(source),command_prefix=[str(wrapper)],
                containment_qualified='a'*64)
            self.assertEqual(report['status'],'passed',report)
            self.assertFalse(report['containment']['qualified'])
            self.assertEqual(report['containment']['wrapperDigest'],grade.digest(wrapper))

    def test_cli_evidence_is_create_only(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory() as d:
            source=ROOT/'text-fidelity/reference/python';out=Path(d)/'grade.json'
            args=[sys.executable,str(ROOT/'text-fidelity/grade_candidate.py'),
                  '--candidate',str(source),'--language','python','--stage','1',
                  '--expected-source-digest',grade.source_digest(source),'--output',str(out),
                  '--development-unconfined']
            self.assertEqual(subprocess.run(args,capture_output=True).returncode,0)
            before=out.read_bytes();self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)
            self.assertEqual(before,out.read_bytes())

    def test_canonical_matches_go_html_unicode_escaping(self):
        wanted = ('"' + r'\u0026\u003c\u003e' + '🍉' + r'\u2028\u2029' + '"').encode()
        self.assertEqual(grade.canonical('&<>🍉  '),wanted)

    def test_wrapper_initialization_failure_is_invalid_setup(self):
        if __import__('os').name != 'posix':
            self.skipTest('POSIX wrapper control')
        with tempfile.TemporaryDirectory() as d:
            wrapper=Path(d)/'wrapper';wrapper.write_text('#!/bin/sh\nexit 125\n');wrapper.chmod(0o755)
            source=ROOT/'text-fidelity/reference/python'
            report=grade.grade_candidate(ROOT/'text-fidelity',source,'python',1,
                expected_source_digest=grade.source_digest(source),command_prefix=[str(wrapper)],containment_qualified='a'*64)
            self.assertEqual(report['status'],'invalid_setup')
            self.assertFalse(report['compiled'])

    def test_ailang_compiled_semantic_mutation_is_not_compile_failure(self):
        if not shutil.which('ailang'):
            self.skipTest('AILANG native control requires installed runtime')
        with tempfile.TemporaryDirectory() as d:
            candidate=Path(d)/'candidate';shutil.copytree(ROOT/'text-fidelity/reference/ailang',candidate)
            p=candidate/'main.ail';before=p.read_text();anchor='["s1", file] => run(1, "", file)'
            self.assertIn(anchor,before)
            p.write_text(before.replace(anchor,'["s1", file] => run(1, "internal_drop", file)'))
            report=self.run_grade(language='ailang',source=candidate)
            self.assertTrue(report['compiled'],report)
            self.assertEqual(report['status'],'semantic_failure',report)
            self.assertEqual(report['cases'][0]['mismatchIds'],['B1','B2','B4','B5','B6','B8'])


if __name__ == '__main__': unittest.main()
