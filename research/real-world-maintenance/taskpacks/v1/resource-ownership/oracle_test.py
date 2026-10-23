import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from oracle import validate


class OracleControls(unittest.TestCase):
    def test_corrupted_inline_is_rejected(self):
        request = {"schema": "maintenance.resource-ownership/1", "operations": [{"op": "extract", "doc": "a", "images": [{"name": "x", "bytes": "AA=="}], "cap": 1}]}
        output = {"schema": request["schema"], "results": [{"ok": True, "refs": [{"name": "x", "path": None, "bytes": "AQ=="}]}]}
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(AssertionError, "inline bytes"):
                validate(request, output, root, 0)

    def test_empty_valid_starter(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertGreater(validate({"schema": "maintenance.resource-ownership/1", "operations": []}, {"schema": "maintenance.resource-ownership/1", "results": []}, root, 0), 0)

    def test_weakened_oracle_cannot_qualify_mutant(self):
        # Qualification requires an actual assertion for every prescribed bad control.
        from qualify import require_semantic_rejection
        with self.assertRaisesRegex(AssertionError, "weakened oracle"):
            require_semantic_rejection(lambda: 1)
        self.assertTrue(require_semantic_rejection(lambda: (_ for _ in ()).throw(AssertionError("bytes changed"))))


    def test_actual_taskpack_refuses_weakened_oracle(self):
        # Run genuine compiled candidates with the semantic oracle disabled.
        # Expected-failure controls must prevent a family qualification claim.
        from qualify import qualify
        with patch("qualify.validate", return_value=1):
            with self.assertRaisesRegex(AssertionError, "weakened oracle"):
                qualify()


    def test_numeric_boolean_error_is_rejected(self):
        request={"schema":"maintenance.resource-ownership/1","operations":[{"op":"read","doc":"missing"}]}
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(AssertionError):
                validate(request,{"schema":request['schema'],"results":[{"ok":0,"error":"document_missing"}]},root,0)

    def test_qualification_refuses_existing_output_before_execution(self):
        import sys
        from qualify import main
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'existing.json';path.write_text('original')
            with patch.object(sys,'argv',['qualify','--output',str(path)]), patch('qualify.native_packages') as native:
                with self.assertRaises(FileExistsError):main()
                native.assert_not_called()
            self.assertEqual(path.read_text(),'original')

if __name__ == "__main__":
    unittest.main()
