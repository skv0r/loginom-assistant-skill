#!/usr/bin/env python3
"""
Unpack / pack Loginom .lgp project files (ZIP archives).

Tested on Loginom 7.3.x projects in this repository.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


def unpack_lgp(lgp_path: Path, out_dir: Path) -> None:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    with zipfile.ZipFile(lgp_path) as zf:
        zf.extractall(out_dir)
    print(f"extracted {lgp_path.name} -> {out_dir}")


def pack_lgp(src_dir: Path, lgp_path: Path) -> None:
    """Repack directory into .lgp (ZIP_DEFLATED). Validates XML before write."""
    xml_files = list(src_dir.rglob("*.xml"))
    for xf in xml_files:
        try:
            ET.parse(xf)
        except ET.ParseError as exc:
            raise SystemExit(f"Invalid XML: {xf}: {exc}") from exc

    if lgp_path.exists():
        backup = lgp_path.with_suffix(lgp_path.suffix + ".bak")
        shutil.copy2(lgp_path, backup)
        print(f"backup: {backup}")

    if lgp_path.exists():
        lgp_path.unlink()

    with zipfile.ZipFile(lgp_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(src_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(src_dir).as_posix()
                zf.write(file_path, arcname)
    print(f"packed {src_dir} -> {lgp_path}")


def verify_lgp(lgp_path: Path) -> bool:
    required_suffixes = ("PackageInfo.xml",)
    with zipfile.ZipFile(lgp_path) as zf:
        names = zf.namelist()
        if not any(n.endswith("PackageInfo.xml") for n in names):
            print("missing PackageInfo.xml")
            return False
        units = [n for n in names if n.endswith("Unit.xml")]
        if not units:
            print("warning: no Unit.xml found")
        for u in units:
            ET.fromstring(zf.read(u))
    print(f"OK: {len(names)} entries, {len(units)} unit(s)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Loginom .lgp unpack/pack/verify")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_unpack = sub.add_parser("unpack", help="Extract .lgp to folder")
    p_unpack.add_argument("lgp", type=Path)
    p_unpack.add_argument("out_dir", type=Path)

    p_pack = sub.add_parser("pack", help="Create .lgp from folder")
    p_pack.add_argument("src_dir", type=Path)
    p_pack.add_argument("lgp", type=Path)

    p_verify = sub.add_parser("verify", help="Validate .lgp structure and XML")
    p_verify.add_argument("lgp", type=Path)

    args = parser.parse_args()
    if args.cmd == "unpack":
        unpack_lgp(args.lgp, args.out_dir)
    elif args.cmd == "pack":
        pack_lgp(args.src_dir, args.lgp)
    elif args.cmd == "verify":
        return 0 if verify_lgp(args.lgp) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
