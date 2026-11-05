# Staged Photonics 0.3.4 backport status

The full **Photonics 0.3.4 → Minecraft 1.20.1 / Iris 1.7.6** backport is not yet compiled.

## Distinct tracks

1. **Experimental compatibility candidate:** Photonics **0.2.5** with Iris's *metadata requirement only* adjusted from 1.7.5 to 1.7.6. GitHub Actions has successfully packaged and byte-for-byte verified preservation of all original classes/assets. It may still fail at launch. Not a port of 0.3.4.
2. **Actual 0.3.4 source reconstruction:** The `partial-java17-port.yml` workflow downloads the original 0.3.4 release into CI, decompiles with Vineflower, and tries rebuilding the self-contained MagicaVox parser classes for Java 17. This is a genuine source-level step, but only a subset—not a runnable Minecraft mod.
3. **Full renderer:** Remapping the new Sodium 0.8/Iris 1.10 renderer and mixin injection targets to Sodium 0.5/Iris 1.7.6 remains open.

## Release gates

The full port cannot be called working until its Java17 classes compile, mixins apply, Iris sees the expected shader hooks, and Minecraft 1.20.1 boots in a disposable copy of Homestead. The original Homestead profile remains unmodified.
