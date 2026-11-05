# Photonics → Minecraft Fabric 1.20.1 (Homestead)

**Status: partial reconstruction only. A working Photonics 0.3.4 port does not exist yet.**

Goal: run the newest Photonics raytracing system with **Minecraft 1.20.1, Iris 1.7.6**, and the current Homestead modpack **without replacing any installed Homestead mods, worlds, or configuration files**.

## Verified deliverables (2026-11-05)

### Experimental compatibility JAR based on Photonics **0.2.5**

[Verified packaging workflow](https://github.com/Katsuraz/Photonics-1.20.1-Backport/actions/runs/42022913946)

- Download official Photonics 0.2.5 for 1.20.1 from Modrinth.
- Patch its Fabric Iris dependency from `1.7.5+1.20.1` to `1.7.6+mc1.20.1`.
- Preserve 110 compiled classes and all shader resources byte for byte.
- **Classfile major version 65 requires Java 21 or newer.** This release does *not* contain Java17 bytecode despite Minecraft 1.20.1 traditionally using Java17.
- **Not a port of 0.3.4. Not tested in Minecraft. Could still crash.**
- Test only in a separate copy of Homestead. Do not overwrite the original.

### Actual Photonics **0.3.4** Java17 source reconstruction (PARTIAL)

[Verified Java17 source port build](https://github.com/Katsuraz/Photonics-1.20.1-Backport/actions/runs/42024497794)

- Vineflower reconstructed 0.3.4 source from official JAR.
- Recompiled `MagicaVox`, `InputBuffer`, `OutputBuffer`, `PBlockPos`, `PChunkPos`, and `LightNodePos`.
- Verified **13 generated Java17 class files** (classfile major 61).
- Both the voxel byte-buffer smoke test and world-coordinate arithmetic smoke test passed on Java17.
- **This is a helper-library JAR, not an installable Fabric mod. It does not provide raytracing.**

## What remains

The work that makes this difficult is rewriting the render pipeline, shader integration and Fabric mixins for Iris **1.7.6 / Sodium 0.5.x** instead of Iris 1.10 / Sodium 0.8, plus Minecraft 1.20.1 shader API differences. The newer version contains 186 compiled classes and 41 mixin entries. Java17 recompilation of isolated helper code does not resolve those incompatibilities.

Before releasing any playable 0.3.4 port:

1. Reconstruct editable code and determine the exact target Homestead Sodium/Fabric versions.
2. Rebuild/replace old Iris & Sodium access and integrate shader pipeline for Minecraft 1.20.1.
3. Recompile all rendering/mixin dependencies.
4. Confirm client launch and actual raytracing in a disposable Homestead copy.

## Repo workflows

- `audit.yml`: produces version and rendering-reference reports.
- `experimental-iris176.yml`: creates the **untested 0.2.5** metadata-only compatibility candidate.
- `partial-java17-port.yml`: produces the **non-installable 0.3.4** Java17 helper-code library and runs smoke tests.

The repository does not commit the upstream ARR JAR or its reconstructed source. Reference files are downloaded only inside temporary GitHub Actions runners.

**Do not install the Java17 partial-code artifact in Minecraft or confuse the experimental 0.2.5 metadata patch with a verified 0.3.4 backport.**
