#!/usr/bin/env python3
"""Stage Photonics 0.2.5 into an isolated Java 17 source rebuild environment.

Only for the ephemeral GitHub Actions workspace. Keep reconstructed source and
upstream assets out of the public git repository. This does not port 0.3.4.
"""
import argparse
import json
import shutil
import zipfile
from pathlib import Path


def stage(original_jar: Path, decompiled: Path, outdir: Path):
    sources = sorted(decompiled.rglob("*.java"))
    if len(sources) < 40:
        raise RuntimeError(f"Only {len(sources)} decompiled Java files; refusing incomplete source staging")
    java_root = outdir / "src/main/java"
    resources = outdir / "src/main/resources"
    source_prefix = "at/redi2go/photonic/"
    for source in sources:
        relative = source.relative_to(decompiled)
        # Vineflower may emit package directory or archive wrapper
        if not str(relative).replace("\\", "/").startswith(source_prefix):
            p = str(relative).replace("\\", "/")
            i = p.find(source_prefix)
            if i < 0:
                continue
            relative = Path(p[i:])
        target = java_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    with zipfile.ZipFile(original_jar) as z:
        meta = json.loads(z.read("fabric.mod.json"))
        if meta.get("id") != "photonics" or not str(meta.get("version")).startswith("0.2.5"):
            raise RuntimeError("Not the official legacy Photonics binary")
        meta["version"] = "0.2.5+iris176.java17.source-rebuild.unverified"
        meta["depends"]["iris"] = "1.7.6+mc1.20.1"
        meta["depends"]["java"] = ">=17"
        for entry in z.infolist():
            name = entry.filename
            if entry.is_dir() or name.endswith(".class") or name == "fabric.mod.json":
                continue
            if name.startswith("META-INF/") or name.endswith(".java"):
                continue
            target = resources / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(entry))
        resources.mkdir(parents=True, exist_ok=True)
        (resources / "fabric.mod.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf8")
    actual = list(java_root.rglob("*.java"))
    print(f"Prepared {len(actual)} reconstructed Java files and {len(list(resources.rglob('*')))} resource entries")
    if len(actual) < 35:
        raise RuntimeError("Missing reconstructed Java sources")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("original_jar", type=Path)
    parser.add_argument("decompiled_dir", type=Path)
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()
    stage(args.original_jar, args.decompiled_dir, args.project_dir)
