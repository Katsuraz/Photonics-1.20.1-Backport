"""No external dependencies or Minecraft installation required."""
import json
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inspect_compatibility import audit, parse_class


def fake_class():
    names = [b"net/irisshaders/iris/pipeline/IrisPipeline", b"Lnet/minecraft/class_2960;"]
    constant_pool = (
        b"\x01" + struct.pack(">H", len(names[0])) + names[0]
        + b"\x07\x00\x01"
        + b"\x01" + struct.pack(">H", len(names[1])) + names[1]
    )
    return b"\xca\xfe\xba\xbe" + struct.pack(">HHH", 0, 65, 4) + constant_pool


class BinaryInspectorTests(unittest.TestCase):
    def test_classfile_magic(self):
        with self.assertRaises(ValueError):
            parse_class(b"not a Java class")

    def test_constant_pool_references(self):
        major, references = parse_class(fake_class())
        self.assertEqual(major, 65)
        self.assertIn("net/irisshaders/iris/pipeline/IrisPipeline", references)
        self.assertIn("net/minecraft/class_2960", references)

    def test_fabric_jar_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "test.jar"
            with zipfile.ZipFile(archive_path, "w") as z:
                z.writestr("fabric.mod.json", json.dumps({
                    "id": "photonics", "version": "0.3.4",
                    "mixins": ["photonics.mixins.json"],
                    "depends": {"minecraft": "~1.21.11", "iris": ">=1.10.5"}
                }))
                z.writestr("photonics.mixins.json", json.dumps({
                    "mixins": ["RendererMixin"], "client": ["PipelineMixin"]
                }))
                z.writestr("test/Renderer.class", fake_class())
            result = audit(archive_path)
            self.assertEqual(result["class_count"], 1)
            self.assertEqual(result["classfile_major_versions"], {"65": 1})
            self.assertEqual(result["mixin_count"], 2)
            self.assertEqual(result["mod_id"], "photonics")


if __name__ == "__main__":
    unittest.main()
