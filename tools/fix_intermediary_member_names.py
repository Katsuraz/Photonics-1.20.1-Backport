#!/usr/bin/env python3
"""Replace unresolved intermediary Minecraft method/field identifiers in decompiled Java.

TinyRemapper's CLI may rename class owners without all inherited member names
when no full Minecraft classpath is supplied. This is an interim source stage.
Only stable, unambiguous Yarn mapping entries are substituted, and a report
is produced. NOT a guarantee that the resulting Mixin injection points work.
"""
import argparse
import collections
import json
import re
from pathlib import Path

TOKEN = re.compile(r"\b(?:method|field)_\d+\b")


def read_map(mapping_file):
    counts = collections.defaultdict(set)
    header = None
    for row in mapping_file.read_text(encoding="utf8").splitlines():
        if row.startswith("tiny\t"):
            header = row.split("\t")
            continue
        parts = row.lstrip("\t").split("\t")
        if len(parts) >= 4 and parts[0] in ("m", "f"):
            _, descriptor, intermediary, named = parts[:4]
            if TOKEN.fullmatch(intermediary) and named:
                counts[intermediary].add(named)
    if not header or "intermediary" not in header or "named" not in header:
        raise ValueError("Expected Yarn TinyV2 mappings with intermediary/named columns")
    unambiguous = {key: next(iter(values)) for key, values in counts.items() if len(values) == 1}
    ambiguous = {key: sorted(values) for key, values in counts.items() if len(values) > 1}
    if len(unambiguous) < 2000:
        raise ValueError(f"Only {len(unambiguous)} mapped members found, mapping input likely broken")
    return unambiguous, ambiguous


def fix_java(root, mapping, ambiguous):
    updated = 0
    replacements = collections.Counter()
    leftovers = collections.Counter()
    for path in root.rglob("*.java"):
        before = path.read_text(encoding="utf8")
        def translate(m):
            value = m.group()
            if value in ambiguous or value not in mapping:
                leftovers[value] += 1
                return value
            target = mapping[value]
            replacements[value] += 1
            return target
        after = TOKEN.sub(translate, before)
        if after != before:
            updated += 1
            path.write_text(after, encoding="utf8")
    return {"source_files_updated": updated, "tokens_rewritten": sum(replacements.values()),
            "unique_tokens_rewritten": len(replacements),
            "still_unmapped": dict(leftovers.most_common(100)),
            "ambiguous_yarn_tokens": len(ambiguous)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mapping_file", type=Path)
    p.add_argument("source_root", type=Path)
    p.add_argument("--report", type=Path, default=None)
    args = p.parse_args()
    mapping, ambiguous = read_map(args.mapping_file)
    result = fix_java(args.source_root, mapping, ambiguous)
    print(json.dumps(result, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2), encoding="utf8")


if __name__ == "__main__":
    main()
