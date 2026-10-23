import unittest
from main import render


class NativeReference(unittest.TestCase):
    def test_default_ascii_edges(self):
        request = dict(schema="cell.text/1", cell="A1", preserve=False, invalid=False, text=" \tA  B\r\n")
        self.assertEqual(render(request, 1, "")["text"], "A  B")

    def test_whole_cell_after_events(self):
        request = dict(schema="cell.events/2", cell="A1", preserve=False, invalid=False,
                       events=[dict(kind="text", value="A ", style=""), dict(kind="text", value=" B", style="")])
        self.assertEqual(render(request, 2, "")["text"], "A  B")


if __name__ == "__main__":
    unittest.main()
