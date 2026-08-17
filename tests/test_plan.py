import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import plan  # noqa: E402


class PlanTests(unittest.TestCase):
    def test_levels(self):
        self.assertEqual(plan.classify_files(["README.md"])["level"], "V0")
        self.assertEqual(plan.classify_files(["assets/kid.png"])["level"], "V1")
        self.assertEqual(plan.classify_files(["lib/features/home/widgets/card.dart"])["level"], "V2")
        self.assertEqual(plan.classify_files(["lib/features/login/bloc/login_cubit.dart"])["level"], "V3")
        self.assertEqual(plan.classify_files(["android/app/src/main/AndroidManifest.xml"])["level"], "V4")
        self.assertEqual(
            plan.classify_files(["lib/profile.dart"], "request camera permission")["level"],
            "V5",
        )

    def test_generic_ts_is_not_assumed_react_native(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text(json.dumps({"dependencies": {"react": "latest"}}))
            self.assertEqual(plan.detect_platform(root, ["src/app.tsx"]), "unknown")

    def test_nested_react_native_manifest_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            app = root / "apps" / "mobile"
            app.mkdir(parents=True)
            (app / "package.json").write_text(json.dumps({"dependencies": {"react-native": "0.82.0"}}))
            self.assertEqual(
                plan.detect_platform(root, ["apps/mobile/src/App.tsx"]),
                "react-native",
            )

    def test_nested_flutter_manifest_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            app = root / "apps" / "mobile"
            app.mkdir(parents=True)
            (app / "pubspec.yaml").write_text("dependencies:\n  flutter:\n    sdk: flutter\n")
            self.assertEqual(
                plan.detect_platform(root, ["apps/mobile/lib/main.dart"]),
                "flutter",
            )

    def test_changed_files_includes_deletion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            f = root / "lib" / "old.dart"
            f.parent.mkdir(parents=True)
            f.write_text("void main() {}\n")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True)
            f.unlink()
            self.assertIn("lib/old.dart", plan.changed_files(root))


if __name__ == "__main__":
    unittest.main()
