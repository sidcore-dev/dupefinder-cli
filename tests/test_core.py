import os
import tempfile
import unittest

from dupefinder_cli.core import find_duplicates, wasted_bytes


class TestFindDuplicates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, content):
        path = os.path.join(self.tmp, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(content)
        return path

    def test_no_duplicates(self):
        self._write("a.txt", "hello")
        self._write("b.txt", "world")
        self.assertEqual(find_duplicates(self.tmp), {})

    def test_simple_duplicate(self):
        self._write("a.txt", "same content")
        self._write("sub/b.txt", "same content")
        dupes = find_duplicates(self.tmp)
        self.assertEqual(len(dupes), 1)
        (paths,) = dupes.values()
        self.assertEqual(len(paths), 2)

    def test_different_size_not_duplicate(self):
        self._write("a.txt", "short")
        self._write("b.txt", "a bit longer text")
        self.assertEqual(find_duplicates(self.tmp), {})

    def test_min_size_filter(self):
        self._write("a.txt", "x")
        self._write("b.txt", "x")
        self.assertEqual(find_duplicates(self.tmp, min_size=10), {})

    def test_three_way_duplicate(self):
        self._write("a.txt", "triplet")
        self._write("b.txt", "triplet")
        self._write("c.txt", "triplet")
        dupes = find_duplicates(self.tmp)
        (paths,) = dupes.values()
        self.assertEqual(len(paths), 3)

    def test_wasted_bytes(self):
        self._write("a.txt", "12345")
        self._write("b.txt", "12345")
        dupes = find_duplicates(self.tmp)
        self.assertEqual(wasted_bytes(dupes), 5)


if __name__ == "__main__":
    unittest.main()
