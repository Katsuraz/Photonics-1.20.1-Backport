#!/usr/bin/env python3
"""Fetch a public upstream Photonics release for temporary CI analysis only.

Not for redistribution. The downloaded JAR is gitignored and is NOT
included in artifacts; only generated audit summaries are retained.
"""
import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.modrinth.com/v2/project/MNlxJdtO/version"
ALLOWED_HOSTS = ("cdn.modrinth.com",)


def request_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "PhotonicsBackportAudit/0.1 (GitHub Actions)"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def fetch(version, minecraft, output):
    candidates = request_json(API)
    candidates = [v for v in candidates
                  if v["version_number"] == version
                  and minecraft in v["game_versions"]
                  and "fabric" in v["loaders"]]
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one Photonics version {version!r} for {minecraft}, got {len(candidates)}")
    files = candidates[0]["files"]
    file_info = next((f for f in files if f.get("primary")), files[0])
    url = file_info["url"]
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise RuntimeError(f"Untrusted Modrinth download host: {parsed.hostname}")
    expected_sha256 = file_info.get("hashes", {}).get("sha256")
    request = urllib.request.Request(url, headers={"User-Agent": "PhotonicsBackportAudit/0.1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read(20 * 1024 * 1024 + 1)
    if len(payload) > 20 * 1024 * 1024:
        raise RuntimeError("Reference mod download unexpectedly large")
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if expected_sha256 and actual_sha256 != expected_sha256:
        raise RuntimeError("Modrinth SHA-256 verification failed")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    print(f"Verified Photonics {version} ({minecraft}), SHA-256 {actual_sha256}, {len(payload)} bytes")
    print("Only metadata audit reports will be saved as workflow artifacts.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--minecraft", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fetch(args.version, args.minecraft, args.output)


if __name__ == "__main__":
    main()
