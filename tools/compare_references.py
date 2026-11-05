#!/usr/bin/env python3
"""Compare Photonics 0.2.5 / 1.20.1 to 0.3.4 / 1.21.11 audits.

Counts are a starting point for porting, not proof of binary compatibility.
"""
import argparse
import json
from pathlib import Path


def compare(old, new):
    old_mixins = set(old.get("mixin_entries", []))
    new_mixins = set(new.get("mixin_entries", []))
    packages = sorted(set(old["external_classes"]) | set(new["external_classes"]))
    return {
        "legacy_version": old["mod_version"],
        "new_version": new["mod_version"],
        "legacy_class_count": old["class_count"],
        "new_class_count": new["class_count"],
        "legacy_java_classfile_versions": old["classfile_major_versions"],
        "new_java_classfile_versions": new["classfile_major_versions"],
        "mixins_shared": sorted(old_mixins & new_mixins),
        "mixins_only_in_legacy": sorted(old_mixins - new_mixins),
        "mixins_only_in_new": sorted(new_mixins - old_mixins),
        "package_changes": {
            package: {
                "legacy_reference_count": len(old["external_classes"].get(package, [])),
                "new_reference_count": len(new["external_classes"].get(package, [])),
                "only_in_new": sorted(set(new["external_classes"].get(package, [])) -
                                       set(old["external_classes"].get(package, []))),
                "only_in_legacy": sorted(set(old["external_classes"].get(package, [])) -
                                          set(new["external_classes"].get(package, [])))
            }
            for package in packages
        },
        "warning": "A name-level binary diff is not a runtime-compatible 0.3.4 port.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old_json", type=Path)
    parser.add_argument("new_json", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(
        json.loads(args.old_json.read_text(encoding="utf8")),
        json.loads(args.new_json.read_text(encoding="utf8"))
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print("Generated comparison:", args.output)
    print("Old mixins:", len(result["mixins_shared"]) + len(result["mixins_only_in_legacy"]))
    print("New mixins:", len(result["mixins_shared"]) + len(result["mixins_only_in_new"]))


if __name__ == "__main__":
    main()
