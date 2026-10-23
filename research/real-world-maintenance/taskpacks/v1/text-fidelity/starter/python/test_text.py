import unittest
from main import render


class NativeBaseline(unittest.TestCase):
    def test_preserves_logical_text(self):
        for text in ("日期 时间", " \tA  B\r\n", " x ", ""):
            request = dict(schema="cell.text/1", cell="A1", preserve=False, invalid=False, text=text)
            self.assertEqual(render(request)["text"], text)

    def test_error_is_not_empty(self):
        request = dict(schema="cell.text/1", cell="A1", preserve=False, invalid=True, text="")
        self.assertFalse(render(request)["ok"])
        self.assertIsNone(render(request)["text"])


if __name__ == "__main__":
    unittest.main()
