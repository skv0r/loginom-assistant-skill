#!/usr/bin/env python3
"""Merge Unit_1 from template .lgp (LOF kit chain) into user package; wire public dataset reference."""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

from paths import LOF_DATA, LOF_PACKAGE_LGP, LOF_REFERENCE_LGP, WORK_LOF_MERGE

SOURCE_UNIT1_LGP = LOF_REFERENCE_LGP
USER_LGP = LOF_PACKAGE_LGP
DATA_DIR = LOF_DATA
WORK = WORK_LOF_MERGE

SOURCE_PUBLIC = "87bb77fc-47a5-469a-93e0-9fe42c943710"
USER_PUBLIC = "a8f3c2e1-4b5d-6a7c-8d9e-0f1a2b3c4d5e"

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}
DROP_UNIT_BIN = {
    "Unit_0/Unit.bin",
    "Unit_0/Info.bin",
    "Unit_1/Unit.bin",
    "Unit_1/Info.bin",
}


def extract(lgp: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(lgp) as zf:
        zf.extractall(dest)


def pack(work: Path, out_lgp: Path) -> None:
    bak = out_lgp.with_suffix(".lgp.bak")
    if out_lgp.exists():
        shutil.copy2(out_lgp, bak)
        out_lgp.unlink()
    with zipfile.ZipFile(out_lgp, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(work.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(work).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)


def main() -> None:
    if not SOURCE_UNIT1_LGP.is_file():
        raise FileNotFoundError(SOURCE_UNIT1_LGP)
    if not USER_LGP.is_file():
        raise FileNotFoundError(USER_LGP)

    template_dir = WORK / "template"
    user_dir = WORK / "user"
    extract(SOURCE_UNIT1_LGP, template_dir)
    extract(USER_LGP, user_dir)

    unit1 = (template_dir / "Unit_1" / "Unit.xml").read_text(encoding="utf-8")
    if SOURCE_PUBLIC not in unit1:
        raise RuntimeError(f"Template public GUID {SOURCE_PUBLIC} not found in Unit_1")
    unit1 = unit1.replace(SOURCE_PUBLIC, USER_PUBLIC)
    unit1 = unit1.replace("../../../8/model", r"C:\model")
    unit1 = re.sub(
        r'(__baseName="filepath">\s*<DefaultValue[^>]*Value=")[^"]+(")',
        lambda m: f'{m.group(1)}C:\\model{m.group(2)}',
        unit1,
    )
    count = unit1.count(USER_PUBLIC)
    if count < 2:
        raise RuntimeError(f"Expected >=2 references to public node, got {count}")

    (DATA_DIR / "model").mkdir(parents=True, exist_ok=True)

    out_dir = WORK / "out"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(user_dir, out_dir)

    (out_dir / "Unit_1" / "Unit.xml").write_text(unit1, encoding="utf-8")

    pack(out_dir, USER_LGP)
    print(f"Patched {USER_LGP}")
    print(f"  Unit_1 from template; public dataset link -> {USER_PUBLIC}")
    print("  Unit_0 unchanged (your layout)")


if __name__ == "__main__":
    main()
