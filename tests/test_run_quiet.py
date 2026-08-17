import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_quiet.py"


class RunQuietTests(unittest.TestCase):
    def test_success_is_concise(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--label", "ok", "--cwd", td, "--", sys.executable, "-c", "print('lots of output')"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("CHECK ok PASS", proc.stdout)
            self.assertNotIn("lots of output", proc.stdout)
            self.assertNotIn(" log=", proc.stdout)

    def test_failure_shows_actionable_excerpt(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--label", "bad", "--cwd", td, "--", sys.executable, "-c", "print('ERROR useful detail'); raise SystemExit(3)"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(proc.returncode, 3)
            self.assertIn("CHECK bad FAIL", proc.stdout)
            self.assertIn("ERROR useful detail", proc.stdout)
            self.assertIn(" log=", proc.stdout)

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--label", "slow", "--timeout", "0.05", "--cwd", td, "--", sys.executable, "-c", "import time; time.sleep(1)"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(proc.returncode, 124)
            self.assertIn("TIMEOUT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
