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
    source = vox.read_text(encoding="utf8")
    # Decompiled readContent() was a bytecode-comment dump. Reconstruct the
    # original JVM tableswitch and body instructions (verified with javap -c).
    method = re.search(r"private static Object readContent\\([^)]*\\)\\s*\\{", source)
    next_method = re.search(r"private static String readString\\(", source)
    if not method or not next_method or method.start() >= next_method.start():
        raise RuntimeError("Could not locate source-level VOX readContent/readString boundaries")
    java = """private static Object readContent(MagicaVox.Chunk parent, String id, InputBuffer buffer) {
      switch (id) {
         case "MAIN":
            return "MAIN";
         case "SIZE": {
            MagicaVox.Size size = new MagicaVox.Size();
            size.width = buffer.getInt();
            size.depth = buffer.getInt();
            size.height = buffer.getInt();
            return size;
         }
         case "XYZI": {
            MagicaVox.Voxels voxels = new MagicaVox.Voxels();
            java.util.List<?> sizes = (java.util.List<?>) parent.children.get(MagicaVox.Size.class);
            MagicaVox.Chunk sizeChunk = (MagicaVox.Chunk) sizes.get(0);
            voxels.size = (MagicaVox.Size) sizeChunk.content;
            voxels.voxels = new byte[voxels.size.width * voxels.size.height * voxels.size.depth];
            int count = buffer.getInt();
            for (int i = 0; i < count; i++) {
               byte x = buffer.get();
               byte y = buffer.get();
               byte z = buffer.get();
               byte index = (byte) (buffer.get() & 255);
               voxels.set(x, z, y, index);
            }
            if (buffer.isAvailable()) throw new IllegalStateException("Unread VOX voxel data");
            return voxels;
         }
         case "RGBA": {
            MagicaVox.Palette palette = new MagicaVox.Palette();
            palette.colors = new int[buffer.available() >> 2];
            buffer.getInt(palette.colors);
            return palette;
         }
         case "nTRN":
         case "nGRP":
         case "nSHP":
         case "LAYR":
         case "MATL":
         case "rOBJ":
         case "rCAM":
         case "NOTE":
            return null;
         default:
            throw new IllegalStateException("Unsupported VOX chunk type: " + id);
      }
   }

   """
    source = source[:method.start()] + java + source[next_method.start():]
    vox.write_text(source, encoding="utf8")
    print("Reconstructed VOX chunk parser from original bytecode")

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
