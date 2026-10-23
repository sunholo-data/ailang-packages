"""Independent expectation and oracle mutation controls."""
import unittest
from qualify import mismatches, oracle_canary


class OracleControls(unittest.TestCase):
    def test_loss_is_detected(self):
        self.assertTrue(oracle_canary())

    def test_weakened_oracle_is_rejected(self):
        self.assertFalse(oracle_canary(weak=True))

    def test_record_field_loss_is_detected(self):
        self.assertEqual(mismatches([dict(ok=True, text="x", error=None)],
                                   [dict(cell="A1", ok=True, text="x", error=None)]), ["A1"])

    def test_missing_row_is_invalid(self):
        with self.assertRaises(AssertionError):
            mismatches([], [dict(cell="A1")])


if __name__ == "__main__":
    unittest.main()
