#!/usr/bin/env python3
"""Repair three specific Vineflower decompilation errors in Photonics 0.2.5.

Do not apply generic guesses. Fail hard if any expected surrounding text is
missing or already transformed. Used only for rebuilding actual source in CI.
"""
from pathlib import Path
import re


def replace_once(path: Path, before: str, after: str):
    content = path.read_text(encoding="utf8")
    count = content.count(before)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one match, found {count}: {before[:70]!r}")
    path.write_text(content.replace(before, after), encoding="utf8")
    print("Fixed:", path.name)


def main():
    root = Path("src/main/java/at/redi2go/photonic/client")
    vox = root / "magicavoxel/VoxReader.java"
    text = vox.read_text(encoding="utf8")
    signature = "private static String readString(InputBuffer buffer, int length)"
    if text.count(signature) != 1:
        raise RuntimeError("Expected exactly one VoxReader::readString")
    opening = text.index("{", text.index(signature))
    depth = 0
    closing = None
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                closing = index
                break
    if closing is None or "byte[] content = new byte[length]" not in text[opening:closing]:
        raise RuntimeError("VoxReader readString body did not match byte-buffer parser")
    text = text[:closing] + ("      return new String(content, java.nio.charset.StandardCharsets.UTF_8);" + chr(10) + "   ") + text[closing:]
    vox.write_text(text, encoding="utf8")
    print("Fixed missing UTF-8 VOX string return")

    ray = root / "Raytracer.java"
    replace_once(ray, "throw new RuntimeException(ex);", "throw new RuntimeException(e);")

    mixin = root / "mixin/ExtendedShaderMixin.java"
    replace_once(
        mixin,
        "((ExtendedShader)this).getName()",
        "((ExtendedShader)(Object)this).getName()"
    )


if __name__ == "__main__":
    main()
