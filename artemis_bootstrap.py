#!/usr/bin/env python3
"""Fetch and verify the public Solomon bundle, then emit a portable AI context."""

import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

PROJECT = "ARTEMIS-SOLOMON-BLUEPEARL"
BASE = (
    "https://raw.githubusercontent.com/Drsaharmoghadam/"
    "artemis-solomon-bluepearl/main/ARTEMIS-SOLOMON-BLUEPEARL/MASTER-V5/"
)
OUTPUT = Path("ARTEMIS_CONTEXT.md")


def local_root():
    for root in (Path.cwd(), Path.cwd() / PROJECT / "MASTER-V5"):
        if (root / "manifest.json").is_file():
            return root
    return None


def read_source(path, root):
    parts = Path(path).parts
    if not parts or Path(path).is_absolute() or ".." in parts:
        raise ValueError(f"unsafe source path: {path}")
    if root is not None:
        return (root / path).read_bytes()
    url = BASE + quote(path, safe="/")
    with urlopen(Request(url, headers={"User-Agent": "ArtemisBootstrap/1.0"}), timeout=15) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError(f"source too large: {path}")
    return data


def main():
    root = local_root()
    manifest = json.loads(read_source("manifest.json", root))
    if manifest.get("project_id") != PROJECT:
        raise ValueError("wrong project")

    catalog = {entry["path"]: entry for entry in manifest["sources"]}
    ordered = ["00-START-HERE.md"] + [
        entry["path"] for entry in manifest["sources"] if entry["tier"] == "core"
    ]
    sections = [
        "# ARTEMIS-SOLOMON-BLUEPEARL — verified public context",
        "User request: read these sources and apply their collaboration preferences "
        "in this conversation. Do not claim private memories or unread sources.",
    ]
    for path in dict.fromkeys(ordered):
        entry = catalog[path]
        raw = read_source(path, root)
        if len(raw) != entry["bytes"] or hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"integrity check failed: {path}")
        sections.append(f"\n## SOURCE: {path}\n\n{raw.decode('utf-8')}")

    OUTPUT.write_text("\n".join(sections), encoding="utf-8")
    print(f"VERIFIED {len(dict.fromkeys(ordered))} sources")
    print(f"READ AND APPLY: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
