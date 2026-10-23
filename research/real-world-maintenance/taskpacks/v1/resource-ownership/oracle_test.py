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


if __name__ == "__main__":
    unittest.main()
