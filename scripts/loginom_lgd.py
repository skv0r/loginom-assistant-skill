#!/usr/bin/env python3
"""
Inspect Loginom .lgd storage files.

Verified (repository samples, Loginom 7.3.x):
- .lgp  -> standard ZIP (PK header at offset 0)
- .lgd  -> proprietary BGDATA container; NOT a ZIP after rename

Header: ASCII 'BGDATA' + binary metadata; no reliable embedded ZIP archive.
For .lgd content, use Loginom UI (import/export .lgd) or work with exported CSV/TXT.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def inspect_lgd(path: Path) -> dict:
    data = path.read_bytes()
    info = {
        "path": str(path),
        "size": len(data),
        "magic": data[:6].decode("ascii", errors="replace"),
        "is_zip": data[:2] == b"PK",
        "has_pk03": b"PK\x03\x04" in data,
    }
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Loginom .lgd files")
    parser.add_argument("lgd", type=Path, nargs="+")
    args = parser.parse_args()

    for p in args.lgd:
        if not p.exists():
            print(f"MISSING: {p}", file=sys.stderr)
            continue
        info = inspect_lgd(p)
        print(f"{p.name}: magic={info['magic']} size={info['size']} zip={info['is_zip']}")
        if info["magic"].startswith("BGDA") and not info["has_pk03"]:
            print("  -> BGDATA format; use Loginom to read/write, not zip rename")

    return 0


if __name__ == "__main__":
    sys.exit(main())
