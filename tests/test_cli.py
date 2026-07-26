import os
import tempfile
import unittest

from dupefinder_cli.cli import main


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name, content):
        path = os.path.join(self.tmp, name)
        with open(path, "w") as fh:
            fh.write(content)
        return path

    def test_missing_directory_returns_2(self):
        self.assertEqual(main(["/nonexistent/dir"]), 2)

    def test_runs_clean_on_no_duplicates(self):
        self._write("a.txt", "x")
        self.assertEqual(main([self.tmp]), 0)

    def test_dry_run_delete_does_not_remove(self):
        a = self._write("a.txt", "dup")
        b = self._write("b.txt", "dup")
        main([self.tmp, "--delete", "--dry-run"])
        self.assertTrue(os.path.exists(a))
        self.assertTrue(os.path.exists(b))

    def test_delete_removes_all_but_one(self):
        a = self._write("a.txt", "dup")
        b = self._write("b.txt", "dup")
        main([self.tmp, "--delete"])
        remaining = [p for p in (a, b) if os.path.exists(p)]
        self.assertEqual(len(remaining), 1)


if __name__ == "__main__":
    unittest.main()
