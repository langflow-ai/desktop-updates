#!/usr/bin/env python3
"""Promote a production build to the update feed.

Usage: python3 scripts/promote_release.py <version>   (e.g. 1.11.3)

Input: prod-release-binaries/, one folder per OS/arch, each holding the
binary plus its detached Tauri signature (<binary>.sig).

Steps:
  1. Copy each binary from prod-release-binaries/ -> releases/v<version>/
  2. Rebuild latest.json, reading each signature from the matching .sig file
  3. Prepend the version entry to versions.json (same pattern as existing entries)
"""

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "prod-release-binaries"

# Where each build lands in the feed. "universal" is the macOS build we ship as
# darwin-x86_64.
PLATFORMS = (
    # (latest.json key,   prod-release-binaries/ folder,        releases/ subfolder)
    ("darwin-aarch64", "langflow-macos-arm-updater", "macOS"),
    ("darwin-x86_64", "langflow-macos-universal-updater", "macOS-x86_64"),
    ("windows-x86_64", "langflow-windows-msi", "windows"),
)

# Binaries tracked by Git LFS (see .gitattributes). raw.githubusercontent.com
# serves the LFS *pointer* for these, not the payload, so the updater must use
# the media host instead.
LFS_SUFFIXES = (".msi", ".tar.gz")
RAW_HOST = "https://raw.githubusercontent.com/"
LFS_HOST = "https://media.githubusercontent.com/media/"
REPO_PATH = "langflow-ai/desktop-updates/RELEASE"

VERSION_IN_NAME = re.compile(r"[_-](\d+\.\d+\.\d+)[_-]")


def to_download_url(url: str) -> str:
    """Point LFS-tracked assets at the media host; leave everything else alone."""
    if url.endswith(LFS_SUFFIXES) and url.startswith(RAW_HOST):
        return LFS_HOST + url[len(RAW_HOST) :]
    return url


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)


def collect_build(folder: Path, version: str) -> tuple[Path, str]:
    """Return (binary path, signature) for one OS folder under prod-release-binaries/."""
    if not folder.is_dir():
        fail(f"folder {folder.relative_to(ROOT)} does not exist")

    binaries = [
        p
        for p in sorted(folder.iterdir())
        if p.is_file() and not p.name.endswith(".sig") and not p.name.startswith(".")
    ]
    if len(binaries) != 1:
        names = ", ".join(p.name for p in binaries) or "none"
        fail(
            f"{folder.relative_to(ROOT)} must hold exactly one binary, found {len(binaries)} ({names})"
        )

    binary = binaries[0]

    # Catch a stale binary left over from a previous release.
    match = VERSION_IN_NAME.search(binary.name)
    if match and match.group(1) != version:
        fail(
            f"{binary.relative_to(ROOT)} looks like version {match.group(1)}, "
            f"but you asked for {version} — aborting"
        )

    sig_path = binary.with_name(binary.name + ".sig")
    if not sig_path.is_file():
        fail(f"missing signature {sig_path.relative_to(ROOT)}")

    signature = sig_path.read_text().strip()
    if not signature:
        fail(f"signature {sig_path.relative_to(ROOT)} is empty")

    return binary, signature


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: promote_release.py <version>  (e.g. 1.11.3)")

    version = sys.argv[1].lstrip("v")
    release_dir = ROOT / "releases" / f"v{version}"
    latest_path = ROOT / "latest.json"
    versions_path = ROOT / "versions.json"

    # --- 1. read every build before touching anything ----------------------
    if not SOURCE_ROOT.is_dir():
        fail(f"folder {SOURCE_ROOT.relative_to(ROOT)} does not exist")

    builds = [
        (platform, dest, *collect_build(SOURCE_ROOT / source, version))
        for platform, source, dest in PLATFORMS
    ]

    # --- 2. copy binaries --------------------------------------------------
    if release_dir.exists():
        print(f"⚠️  {release_dir.relative_to(ROOT)} already exists — overwriting")
        shutil.rmtree(release_dir)

    for _platform, dest, binary, _signature in builds:
        target = release_dir / dest / binary.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(binary, target)
        print(f"✅ copied {binary.relative_to(ROOT)} -> {target.relative_to(ROOT)}")

    # --- 3. latest.json ----------------------------------------------------
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = {
        "version": version,
        "notes": f"Langflow Desktop {version}",
        "pub_date": now,
        "platforms": {
            platform: {
                "signature": signature,
                "url": to_download_url(
                    f"{RAW_HOST}{REPO_PATH}/releases/v{version}/{dest}/{binary.name}"
                ),
            }
            for platform, dest, binary, signature in builds
        },
    }
    latest_path.write_text(json.dumps(latest, indent="\t") + "\n")
    print(f"✅ latest.json updated (version={version}, pub_date={now})")

    # --- 4. versions.json --------------------------------------------------
    versions = json.loads(versions_path.read_text())
    if any(v.get("name") == version for v in versions["versions"]):
        print(f"⚠️  version {version} is already in versions.json — leaving it as is")
    else:
        versions["versions"].insert(
            0,
            {
                "name": version,
                "description": "",
                "url": f"https://github.com/langflow-ai/langflow-desktop/releases/tag/{version}",
                "date": datetime.now(timezone.utc).strftime("%Y/%m/%d"),
                "signature": "N/A",
            },
        )
        versions_path.write_text(json.dumps(versions, indent=2) + "\n")
        print(f"✅ versions.json updated ({version} entry added at the top)")

    print(f"\n🎉 release {version} promoted to production. Review with 'git diff' and commit.")


if __name__ == "__main__":
    main()
