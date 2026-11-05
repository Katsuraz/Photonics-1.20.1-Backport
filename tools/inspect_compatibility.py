#!/usr/bin/env python3
"""Read-only binary compatibility analysis for Photonics JARs.

Usage: python tools/inspect_compatibility.py Photonics-0.3.4.jar --output audit.json
       python tools/inspect_compatibility.py Photonics-0.3.4.jar --mods-folder /safe/copy/mods

This does NOT backport Java bytecode or validate mixin injection targets.
"""
import argparse
import collections
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

PKG_PREFIXES = (
    "net/minecraft/",
    "net/irisshaders/iris/",
    "net/caffeinemc/mods/sodium/",
    "me/jellysquid/mods/sodium/",
)


def parse_class(data):
    if len(data) < 10 or data[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("Not a JVM .class file")
    major, count = struct.unpack_from(">HH", data, 6)
    cp = [None] * count
    offset, idx = 10, 1
    while idx < count:
        tag = data[offset]
        offset += 1
        if tag == 1:
            size = struct.unpack_from(">H", data, offset)[0]
            offset += 2
            cp[idx] = ("utf8", data[offset:offset + size].decode("utf8", "replace"))
            offset += size
        elif tag in (3, 4):
            offset += 4
        elif tag in (5, 6):
            offset += 8
            idx += 1
        elif tag in (7, 8, 16, 19, 20):
            if tag == 7:
                cp[idx] = ("ref", struct.unpack_from(">H", data, offset)[0])
            offset += 2
        elif tag in (9, 10, 11, 12, 17, 18):
            offset += 4
        elif tag == 15:
            offset += 3
        else:
            raise ValueError(f"Unknown constant-pool tag: {tag}")
        idx += 1
    names = set()
    for entry in cp:
        if entry and entry[0] == "ref":
            pointed = cp[entry[1]]
            if pointed and pointed[0] == "utf8":
                value = pointed[1]
                if value.startswith("["):
                    names.update(re.findall(r"L([\w/$]+);", value))
                else:
                    names.add(value)
        elif entry and entry[0] == "utf8":
            names.update(re.findall(r"L([\w/$]+);", entry[1]))
    return major, names


def audit(jar, mods_folder=None):
    jar = Path(jar)
    by_package = collections.defaultdict(set)
    majors = collections.Counter()
    with zipfile.ZipFile(jar) as archive:
        entries = [n for n in archive.namelist() if n.endswith(".class")]
        metadata = json.loads(archive.read("fabric.mod.json"))
        config_entry = metadata["mixins"][0]
        config_file = config_entry if isinstance(config_entry, str) else config_entry["config"]
        mixin_config = json.loads(archive.read(config_file))
        for entry in entries:
            major, references = parse_class(archive.read(entry))
            majors[str(major)] += 1
            for name in references:
                if name.startswith(PKG_PREFIXES):
                    by_package[name].add(entry)
    mixins = mixin_config.get("mixins", []) + mixin_config.get("client", [])
    result = {
        "source_file": jar.name,
        "sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
        "mod_id": metadata["id"],
        "mod_version": metadata["version"],
        "required_versions": metadata.get("depends", {}),
        "class_count": len(entries),
        "classfile_major_versions": dict(majors),
        "mixin_count": len(mixins),
        "mixin_entries": mixins,
        "mixin_duplicates": sorted(k for k, count in collections.Counter(mixins).items() if count > 1),
        "external_classes": {
            prefix: sorted(name for name in by_package if name.startswith(prefix))
            for prefix in PKG_PREFIXES
        },
        "limitations": "Type-only audit: not a source port, not mixin/ABI signature validation, not a runtime test.",
    }
    if mods_folder:
        defined = set()
        mods = sorted(Path(mods_folder).glob("*.jar"))
        for dependency in mods:
            try:
                with zipfile.ZipFile(dependency) as archive:
                    defined.update(n[:-6] for n in archive.namelist() if n.endswith(".class"))
            except (OSError, zipfile.BadZipFile):
                continue
        result["target_mods_jars_scanned"] = len(mods)
        result["missing_in_target_mods_folder"] = {
            prefix: sorted(n for n in result["external_classes"][prefix] if n not in defined)
            for prefix in PKG_PREFIXES[1:]
        }
        result["target_note"] = "Minecraft itself is not present in a mods folder; missing type checks apply to mod APIs only."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jar", type=Path)
    parser.add_argument("--mods-folder", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit(args.jar, args.mods_folder)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf8")
    print("Photonics", result["mod_version"], "Java major", result["classfile_major_versions"],
          "classes", result["class_count"], "mixins", result["mixin_count"])
    for package, names in result["external_classes"].items():
        print(package, len(names))
    if args.output:
        print("Audit written:", args.output)
    else:
        print(rendered)


if __name__ == "__main__":
    main()
