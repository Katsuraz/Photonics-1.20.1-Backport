# Photonics 0.3.4 → Minecraft 1.20.1 (research/backport)

**Status: under development — there is NO installable Photonics port yet.**

Goal: reconstruct and adapt the original Photonics 0.3.4 Fabric client mod for **Minecraft 1.20.1**, **Iris 1.7.6**, and **Java 17**, without modifying the user's Homestead modpack, worlds, or existing dependency versions.

## Rules

- Work exclusively in a development environment, not the Homestead installation.
- **Do not change Homestead's Iris, Sodium, Fabric API, configs, or other mods.**
- Do not call an empty Fabric template, patched `fabric.mod.json`, or Java version-header rewrite a functional port.
- A release is blocked until the real renderer is ported, integration mixins are verified, and a separate client smoke test succeeds.

## Why this requires source reconstruction

The supplied `Photonics-0.3.4.jar` is built for Minecraft 1.21.11, Iris 1.10.5+, and Java 21. Its renderer and mixins reference APIs that do not exist in the 1.20.1 / Iris 1.7.6 environment. The JAR contains 186 classes and 41 mixin entries.

The developer's distributed mod lists **All Rights Reserved**. The user's supplied JAR is retained locally; this **public repository does not contain** the binary or extracted proprietary code/assets. The user reports having obtained porting permission.

## Current contents

- `tools/audit_photonics.py` — inspect classfile versions, version requirements, and mixin names; optionally compare against copies of target mod jars.
- `tests/` — tests for the auditor.
- `.github/workflows/audit.yml` — runs the auditor's tests and accepts optional reference JARs from a local checkout.
- `PORTING.md` — concrete work outstanding.

## Current stage

1. ✅ Original binary analyzed.
2. ✅ Dedicated GitHub project and repeatable compatibility audit setup.
3. ☐ Compare against *exact* Homestead Sodium and Iris artifacts.
4. ☐ Reconstruct and compile the actual Photonics renderer against Minecraft 1.20.1.
5. ☐ Pass client launch, mixin, raytracing/shader, and world-render tests.

**There is intentionally no release/JAR download until it actually works.**
