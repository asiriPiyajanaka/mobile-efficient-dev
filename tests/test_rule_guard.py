import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rule_guard  # noqa: E402


class RuleGuardTests(unittest.TestCase):
    def _repo(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        p = root / "lib" / "screen.dart"
        p.parent.mkdir(parents=True)
        p.write_text("ElevatedButton(onPressed: () {})\nfinal title = 'old';\n")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True)
        return td, root, p

    def _rule(self, scope="changed_lines"):
        return {
            "id": "UI-001",
            "description": "No raw ElevatedButton",
            "severity": "error",
            "scope": scope,
            "paths": ["lib/**/*.dart"],
            "forbid_regex": [r"\bElevatedButton\s*\("],
        }

    def test_changed_lines_ignores_legacy_violation(self):
        td, root, p = self._repo()
        try:
            p.write_text("ElevatedButton(onPressed: () {})\nfinal title = 'new';\n")
            code = rule_guard.check_rules([self._rule()], root, ["lib/screen.dart"], 20)
            self.assertEqual(code, 0)
        finally:
            td.cleanup()

    def test_file_scope_flags_legacy_violation(self):
        td, root, p = self._repo()
        try:
            p.write_text("ElevatedButton(onPressed: () {})\nfinal title = 'new';\n")
            code = rule_guard.check_rules([self._rule("file")], root, ["lib/screen.dart"], 20)
            self.assertEqual(code, 1)
        finally:
            td.cleanup()

    def test_changed_lines_flags_new_violation(self):
        td, root, p = self._repo()
        try:
            p.write_text(
                "ElevatedButton(onPressed: () {})\n"
                "final title = 'old';\n"
                "ElevatedButton(onPressed: () {})\n"
            )
            code = rule_guard.check_rules([self._rule()], root, ["lib/screen.dart"], 20)
            self.assertEqual(code, 1)
        finally:
            td.cleanup()

    def test_brace_glob(self):
        self.assertTrue(rule_guard.path_matches("src/a/Button.tsx", ["src/**/*.{ts,tsx,js,jsx}"]))
        self.assertTrue(rule_guard.path_matches("src/Button.tsx", ["src/**/*.{ts,tsx,js,jsx}"]))


if __name__ == "__main__":
    unittest.main()
