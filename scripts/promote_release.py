#!/usr/bin/env python3
"""Promote a QA release to production.

Usage: python3 scripts/promote_release.py <version>   (e.g. 1.10.2)

Steps:
  1. Copy qa-releases/v<version>/ -> releases/v<version>/
  2. Rebuild latest.json from qa_latest.json (notes, pub_date, urls pointing to releases/)
  3. Prepend the version entry to versions.json (same pattern as existing entries)
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fail(msg: str) -> None:
    print(f"❌ {msg}")
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("uso: promote_release.py <version>  (ex: 1.10.2)")

    version = sys.argv[1].lstrip("v")
    qa_dir = ROOT / "qa-releases" / f"v{version}"
    release_dir = ROOT / "releases" / f"v{version}"
    qa_latest_path = ROOT / "qa_latest.json"
    latest_path = ROOT / "latest.json"
    versions_path = ROOT / "versions.json"

    # --- validations -------------------------------------------------------
    if not qa_dir.is_dir():
        fail(f"pasta {qa_dir.relative_to(ROOT)} não existe")

    qa_latest = json.loads(qa_latest_path.read_text())
    if qa_latest.get("version") != version:
        fail(
            f"qa_latest.json está na versão {qa_latest.get('version')!r}, "
            f"mas você pediu {version!r} — aborting"
        )

    # --- 1. copy binaries --------------------------------------------------
    if release_dir.exists():
        print(f"⚠️  {release_dir.relative_to(ROOT)} já existe — sobrescrevendo")
        shutil.rmtree(release_dir)
    shutil.copytree(qa_dir, release_dir)
    print(f"✅ copiado qa-releases/v{version}/ -> releases/v{version}/")

    # --- 2. latest.json ----------------------------------------------------
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest = {
        "version": version,
        "notes": f"Langflow Desktop {version}",
        "pub_date": now,
        "platforms": {},
    }
    for platform, info in qa_latest["platforms"].items():
        latest["platforms"][platform] = {
            "signature": info["signature"],
            "url": info["url"].replace("/qa-releases/", "/releases/"),
        }
    latest_path.write_text(json.dumps(latest, indent="\t") + "\n")
    print(f"✅ latest.json atualizado (version={version}, pub_date={now})")

    # --- 3. versions.json --------------------------------------------------
    versions = json.loads(versions_path.read_text())
    if any(v.get("name") == version for v in versions["versions"]):
        print(f"⚠️  versão {version} já está no versions.json — mantendo como está")
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
        print(f"✅ versions.json atualizado (entrada {version} adicionada no topo)")

    print(f"\n🎉 release {version} promovida para produção. Revise com 'git diff' e commite.")


if __name__ == "__main__":
    main()
