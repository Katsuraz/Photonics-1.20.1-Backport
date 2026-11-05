# Photonics 1.20.1 backport workspace

**This repository contains development tooling and experimental builds. There is NO verified working Photonics 0.3.4 backport yet.**

**Target Homestead configuration (do not replace original mods):** Minecraft Fabric 1.20.1, Iris 1.7.6, Sodium 0.5.13, Java 17.

## Verified milestone: full Photonics 0.2.5 Java 17 source rebuild

**[Successful GitHub Actions run](https://github.com/Katsuraz/Photonics-1.20.1-Backport/actions/runs/42029966788)**

The `legacy-java17-source-rebuild.yml` workflow takes the official **Photonics 0.2.5** for Minecraft 1.20.1 and:

1. Downloads the original upstream JAR into a disposable GitHub Actions runner.
2. Remaps Fabric intermediary classes to the 1.20.1 Yarn namespace, then reconstructs 94 Java source files using Vineflower.
3. Repairs 460 unresolved Minecraft member-name references using the 1.20.1 Yarn mappings.
4. Repairs three decompiler defects, including VOX chunk parsing, without stubbing rendering logic.
5. Compiles the original renderer's **110 Java class files** for **Java 17 (classfile 61)** against **Iris 1.7.6**, **Sodium 0.5.13** and Minecraft 1.20.1.
6. Creates a Fabric JAR with the original Photonics resources.
7. Verifies 71 original graphics/mixin/refmap assets remain byte-for-byte unchanged.
8. Executes the reconstructed voxel parser under an **actual Java 17 JVM**. **PASS.**

**Artifact label:** `Photonics-0.2.5-Java17-Iris176-SOURCE-REBUILD-UNTESTED`

**WARNING:** This is a genuine source rebuild of the old 0.2.5 release, **not** the requested Photonics 0.3.4 port, and has not been tested launching Minecraft with Iris/Sodium or ray tracing. Original Mixin refmap preserved but not runtime-validated. The resulting JAR **may still crash**.

## Photonics 0.3.4

[Successful partial 0.3.4 Java17 code-rebuild run](https://github.com/Katsuraz/Photonics-1.20.1-Backport/actions/runs/42024497794)

The 1.21.11 version currently has 13 independently rebuilt Java17 helper classes with passing MagicaVoxel/position tests. It still needs its newer **renderer, shaders, and Iris/Sodium mixin integrations** adapted to Minecraft 1.20.1.

### Install safely

Never modify or downgrade the original Homestead mods. If trying experimental JARs, create a **separate copy** of your Minecraft instance first. Use only **one Photonics JAR** in that test copy. To revert, remove only the experimental JAR. Back up any world before launching; do not treat test builds as production-ready.

## Source and rights

The original upstream releases are marked All Rights Reserved. The user reports having the author's permission for porting. This public repository does **not** commit original JARs, shader assets, or decompiled source: CI downloads/extracts originals temporarily and publishes only a clearly marked experimental build artifact.

The GitHub Actions build result is evidence of compilation, not evidence of a successful Minecraft startup.
