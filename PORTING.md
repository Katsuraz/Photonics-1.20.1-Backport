# Actual porting tasks

**Target is locked:** Fabric Minecraft 1.20.1, Iris 1.7.6, Java 17, and whatever Sodium/Fabric API versions are already present in the original Homestead instance. Nothing in Homestead itself should be replaced.

## Status: binary analysis / API mapping only

The GitHub Actions audit uses two official Modrinth releases as references:

- Photonics 0.2.5 for Minecraft 1.20.1 — useful for older renderer and mixin integration patterns.
- Photonics 0.3.4 for Minecraft 1.21.11 — desired newer features including shader patches and lighting changes.

**The audit downloads reference binaries to an ephemeral runner and publishes JSON summaries only. It does not construct a functional mod.**

## Verified from supplied 0.3.4 JAR

- 186 JVM classes; all classfile major version 65 (Java 21).
- 41 mixin entries.
- Dependency declaration: `minecraft: ~1.21.11`, `iris: >=1.10.5+1.21.11-fabric`, `java: >=21`.
- 165 distinct Minecraft, 78 Iris, and 29 Sodium type references.
- New render code relies on API surfaces not found in 1.20.1's Java 17 / Iris 1.7.6 generation.

## Remaining critical tasks

- [x] Independently reproduce Java/mixin/dependency inventory from public upstream releases.
- [ ] Obtain a **copy** of the target Homestead profile's *exact* Iris/Sodium/Fabric API/Mod Menu JARs; compare references and member signatures. Do not modify the profile.
- [ ] Reconstruct editable Java source for 0.3.4 and retain relevant resources privately or under appropriate distribution permissions.
- [ ] Create Fabric Loom Java 17 build against Minecraft 1.20.1 mappings.
- [ ] Port every rendering/mixin injection to the old Minecraft and Iris APIs, rewriting or backporting unavailable render abstractions.
- [ ] Restore 0.3.4's voxel upload, lighting, shader-patch, ReSTIR and UI logic as feasible.
- [ ] Compile and run a disposable Minecraft instance with exact dependency versions; resolve mixin and class loading failures.
- [ ] Run shaderpack, gameplay, world and performance smoke tests on a COPY of Homestead.
- [ ] Publish an installable JAR only after the above checks pass. Otherwise label all deliverables diagnostics-only.

## Never do this

- Do not label a `fabric.mod.json` dependency edit as a completed port.
- Do not fake Java 17 compatibility by merely changing classfile version bytes.
- Do not downgrade or replace Homestead's mods.
- Do not commit an All-Rights-Reserved upstream binary, source reconstructed from it, or proprietary assets to a **public** repository without confirming redistribution rights.
