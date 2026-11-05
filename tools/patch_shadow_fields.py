#!/usr/bin/env python3
"""Repair two regression-mapped Fabric Mixin @Shadow field names.

The original Photonics 0.2.5 intermediary JAR uses class_785.field_4230
and class_761.field_4085 (ModelElement and WorldRenderer shadows).
Rebuilding from decompiled Yarn sources with annotation processing disabled
left those two shadows named 'faces' and 'world'. Mixin cannot attach them.

Patch only constant-pool UTF8 names inside the two designated Java17
classfiles. Preserve all original classes, graphics and refmaps byte-for-byte
otherwise. Output remains UNTESTED for Minecraft runtime compatibility.
"""
import argparse
import json
import struct
import zipfile
from pathlib import Path

SHADOWS = {
    "at/redi2go/photonic/client/mixin/ModelElementMixin.class": ("faces", "field_4230"),
    "at/redi2go/photonic/client/mixin/WorldRendererMixin.class": ("world", "field_4085"),
}
VERSION = "0.2.5+iris176.java17.shadowfix1.unverified"
CP_SIZES = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4,
            11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}


def patch_class(data, old, new):
    if data[:4] != b"\xca\xfe\xba\xbe" or struct.unpack_from(">H", data, 6)[0] != 61:
        raise ValueError("Not Java 17 compiled bytecode")
    count = struct.unpack_from(">H", data, 8)[0]
    parts = [data[:10]]
    pos, index, matches = 10, 1, 0
    while index < count:
        start = pos
        tag = data[pos]
        pos += 1
        if tag == 1:
            length = struct.unpack_from(">H", data, pos)[0]
            pos += 2
            value = data[pos:pos + length]
            pos += length
            if value == old.encode():
                replacement = new.encode()
                parts.append(bytes([1]) + struct.pack(">H", len(replacement)) + replacement)
                matches += 1
            else:
                parts.append(data[start:pos])
        else:
            if tag not in CP_SIZES:
                raise ValueError(f"Unknown constant pool tag {tag}")
            pos += CP_SIZES[tag]
            parts.append(data[start:pos])
            if tag in (5, 6):
                index += 1
        index += 1
    if matches != 1:
        raise ValueError(f"Expected one {old!r} field name in original classfile; got {matches}")
    return b"".join(parts) + data[pos:]


def patch_jar(source_file, output_file):
    if source_file.resolve() == output_file.resolve():
        raise ValueError("Refusing to overwrite original JAR")
    with zipfile.ZipFile(source_file) as source:
        if source.testzip() is not None:
            raise ValueError("Corrupt source JAR")
        meta = json.loads(source.read("fabric.mod.json"))
        if (meta.get("id") != "photonics" or
                not meta.get("version", "").startswith("0.2.5+iris176.java17.") or
                meta.get("depends", {}).get("iris") != "1.7.6+mc1.20.1" or
                meta.get("depends", {}).get("minecraft") != "1.20.1" or
                meta.get("depends", {}).get("java") != ">=17"):
            raise ValueError("Wrong Photonics build or dependency metadata")
        meta["version"] = VERSION
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_file, "w") as result:
            for entry in source.infolist():
                payload = source.read(entry.filename)
                if entry.filename in SHADOWS:
                    payload = patch_class(payload, *SHADOWS[entry.filename])
                if entry.filename == "fabric.mod.json":
                    payload = (json.dumps(meta, indent=2) + "\n").encode()
                result.writestr(entry, payload)

    with zipfile.ZipFile(source_file) as a, zipfile.ZipFile(output_file) as b:
        if b.testzip() or set(a.namelist()) != set(b.namelist()):
            raise AssertionError("Output archive corrupt / missing entries")
        changed = {name for name in a.namelist() if a.read(name) != b.read(name)}
        assert changed == set(SHADOWS) | {"fabric.mod.json"}, changed
        classes = [x for x in b.namelist() if x.endswith(".class")]
        assert len(classes) >= 110
        assert all(struct.unpack(">H", b.read(n)[6:8])[0] == 61 for n in classes)
    print(f"PASS: rebuilt {len(classes)} Java17 classes; exact shadow fields restored")
    print("PASS: no other bytecode, resource, or refmap contents changed")
    print("UNTESTED Minecraft runtime candidate:", output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    patch_jar(args.source, args.output)
