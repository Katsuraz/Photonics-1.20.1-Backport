import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from patch_legacy_iris import patch_legacy, TARGET_IRIS


class LegacyPatcherTests(unittest.TestCase):
    def _make_jar(self, path, iris="1.7.5+1.20.1"):
        meta = {
            "id": "photonics",
            "version": "0.2.5",
            "depends": {"minecraft": "1.20.1", "iris": iris, "java": ">=22"}
        }
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("fabric.mod.json", json.dumps(meta))
            z.writestr("at/redi2go/photonics/client/Photonics.class", b"test-bytecode")
            z.writestr("assets/photonics/shaders/basic/lighting.fsh", b"original-shader")

    def test_changes_only_fabric_metadata(self):
        with tempfile.TemporaryDirectory() as t:
            original = Path(t) / "original.jar"
            patched = Path(t) / "patched.jar"
            self._make_jar(original)
            patch_legacy(original, patched)
            with zipfile.ZipFile(original) as a, zipfile.ZipFile(patched) as b:
                changed = [n for n in a.namelist() if a.read(n) != b.read(n)]
                self.assertEqual(changed, ["fabric.mod.json"])
                data = json.loads(b.read("fabric.mod.json"))
                self.assertEqual(data["depends"]["iris"], TARGET_IRIS)
                self.assertEqual(data["depends"]["java"], ">=22")

    def test_rejects_other_iris_versions(self):
        with tempfile.TemporaryDirectory() as t:
            original = Path(t) / "original.jar"
            patched = Path(t) / "patched.jar"
            self._make_jar(original, iris="1.7.3+1.20.1")
            with self.assertRaises(ValueError):
                patch_legacy(original, patched)

    def test_protects_original_file(self):
        with tempfile.TemporaryDirectory() as t:
            original = Path(t) / "original.jar"
            self._make_jar(original)
            with self.assertRaises(ValueError):
                patch_legacy(original, original)


if __name__ == "__main__":
    unittest.main()
