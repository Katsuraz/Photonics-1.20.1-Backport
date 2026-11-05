#!/usr/bin/env python3
"""EXPERIMENTAL: relax ONE dependency in the old official 0.2.5 release.

This patches the pre-existing 1.20.1 release for *Iris 1.7.6* so that Fabric's
metadata check can proceed. This is NOT the Photonics 0.3.4 backport and it
does not establish binary ABI or runtime compatibility.

No mods in the target Homestead instance are modified by this script.
"""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

EXPECTED_OLD_ID = "photonics"
EXPECTED_OLD_VERSION = "0.2.5"
EXPECTED_MINECRAFT = "1.20.1"
TARGET_IRIS = "1.7.6+mc1.20.1"


def patch_legacy(input_jar: Path, output_jar: Path):
    if input_jar.resolve() == output_jar.resolve():
        raise ValueError("Do not overwrite the official input release")
    if not zipfile.is_zipfile(input_jar):
        raise ValueError("Invalid input: not a JAR/ZIP")

    with zipfile.ZipFile(input_jar, "r") as src:
        metadata = json.loads(src.read("fabric.mod.json"))
        if metadata.get("id") != EXPECTED_OLD_ID:
            raise ValueError("Not Photonics")
        if not str(metadata.get("version", "")).startswith(EXPECTED_OLD_VERSION):
            raise ValueError("Input is not the 0.2.5 release")
        minecraft_req = str(metadata.get("depends", {}).get("minecraft", ""))
        if EXPECTED_MINECRAFT not in minecraft_req:
            raise ValueError(f"Input is not a 1.20.1 build: {minecraft_req}")
        old_iris = str(metadata["depends"].get("iris", ""))
        if old_iris != "1.7.5+1.20.1":
            raise ValueError(f"Unexpected Iris requirement {old_iris!r}; manual inspection required")

        target_meta = json.loads(json.dumps(metadata))
        target_meta["version"] = "0.2.5+iris.1.7.6.experimental"
        target_meta["depends"]["iris"] = TARGET_IRIS
        # Preserve the JVM requirement and all binary classes without edits.
        notes = (
            "UNTESTED EXPERIMENTAL COMPATIBILITY BUILD\\n"
            "Based on official Photonics 0.2.5 for Minecraft 1.20.1.\\n"
            "Changes: Fabric metadata iris requirement 1.7.5+1.20.1 -> 1.7.6+mc1.20.1.\\n"
            "No Java classes, renderer, shader assets, or other mod requirements were changed.\\n"
            "NOT a port of Photonics 0.3.4. This can still crash if API methods changed.\\n"
            "Test in a COPIED Minecraft instance. Do not replace original Homestead files.\\n"
        )
        output_jar.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_jar, "w") as dst:
            for info in src.infolist():
                payload = (json.dumps(target_meta, indent=2) + "\n").encode("utf-8") if info.filename == "fabric.mod.json" else src.read(info)
                dst.writestr(info, payload)
            dst.writestr("META-INF/PHOTONICS-EXPERIMENTAL-COMPATIBILITY.txt", notes)
    with zipfile.ZipFile(output_jar, "r") as patched:
        if patched.testzip() is not None:
            raise ValueError("Generated JAR is corrupt")
        actual = json.loads(patched.read("fabric.mod.json"))
        if actual["depends"]["iris"] != TARGET_IRIS:
            raise ValueError("Patched dependency incorrect")
        if actual["depends"].get("java") != metadata["depends"].get("java"):
            raise ValueError("Java requirement must be preserved")
        assert set(src_name for src_name in zipfile.ZipFile(input_jar).namelist() if src_name.endswith(".class")) == set(
            n for n in patched.namelist() if n.endswith(".class"))
    print("Experimental compatibility artifact generated:", output_jar)
    print("Iris requirement:", old_iris, "->", TARGET_IRIS)
    print("Java requirement preserved:", metadata["depends"].get("java"))
    print("SHA256:", hashlib.sha256(output_jar.read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    patch_legacy(args.input, args.output)


if __name__ == "__main__":
    main()
