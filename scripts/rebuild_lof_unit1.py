#!/usr/bin/env python3
"""Rebuild Unit_1: template LOF kits + metrics encoding + SAMPLE valid/test wiring."""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

from fix_lof_unit1_metrics import (
    DROP_UNIT_BIN,
    NODE_CLASS_BINARY,
    NODE_OUTLIER,
    SKIP_ROOT_BIN,
    fix_broken_items_wrappers,
    patch_class_binary,
    patch_outlier_binary,
)
from patch_lof_unit1_wiring import IS_TEST, patch as patch_wiring
from paths import LOF_DATA, LOF_PACKAGE_LGP, LOF_REFERENCE_LGP, WORK_LOF_NATIVE

SOURCE_UNIT1_LGP = LOF_REFERENCE_LGP
USER_LGP = LOF_PACKAGE_LGP
DATA_DIR = LOF_DATA
WORK = WORK_LOF_NATIVE

SOURCE_PUBLIC = "87bb77fc-47a5-469a-93e0-9fe42c943710"
USER_PUBLIC = "a8f3c2e1-4b5d-6a7c-8d9e-0f1a2b3c4d5e"


def main() -> None:
    for d in (
        Path(r"C:\model\k15_c05"),
        Path(r"C:\model\k15_c02"),
        Path(r"C:\model\k20_c05"),
    ):
        d.mkdir(parents=True, exist_ok=True)

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    with zipfile.ZipFile(USER_LGP) as zf:
        zf.extractall(WORK)

    template_dir = WORK / "_template_source"
    with zipfile.ZipFile(SOURCE_UNIT1_LGP) as zf:
        zf.extractall(template_dir)

    unit1 = (template_dir / "Unit_1" / "Unit.xml").read_text(encoding="utf-8")
    unit1 = unit1.replace(SOURCE_PUBLIC, USER_PUBLIC)
    unit1 = unit1.replace("../../../8/model", r"C:\model")
    unit1 = re.sub(
        r'(__baseName="filepath">\s*<DefaultValue[^>]*Value=")[^"]+(")',
        lambda m: f'{m.group(1)}C:\\model{m.group(2)}',
        unit1,
    )

    unit1 = fix_broken_items_wrappers(unit1)
    for guid in NODE_CLASS_BINARY:
        unit1 = patch_class_binary(unit1, guid)
    for guid in NODE_OUTLIER:
        unit1 = patch_outlier_binary(unit1, guid)
    unit1, _ = re.subn(
        r'(__baseName="beta">\s*<DefaultValue[^>]*Value=")4(")',
        r"\g<1>2\2",
        unit1,
    )
    unit1 = unit1.replace(r"C:\model", r"C:\model\k15_c05")
    unit1 = unit1.replace("../../../8/model", r"C:\model\k15_c05")
    unit1 = re.sub(
        r'(__baseName="params">\s*<DefaultValue[^>]*Value=")[^"]+(")',
        r"\g<1>n_neighbors=15,contamination=0.05\2",
        unit1,
        count=1,
    )
    unit1 = patch_wiring(unit1)

    (WORK / "Unit_1" / "Unit.xml").write_text(unit1, encoding="utf-8")

    bak = USER_LGP.with_suffix(".lgp.bak_native")
    shutil.copy2(USER_LGP, bak)
    try:
        USER_LGP.unlink()
    except OSError as exc:
        raise SystemExit(f"Close Loginom and unlock {USER_LGP}: {exc}") from exc

    with zipfile.ZipFile(USER_LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file() or "_template_source" in f.parts:
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)

    print(f"Native Unit_1 rebuilt in {USER_LGP}")
    print(f"  Backup: {bak}")
    print("  Kits: LOF + meta-scaling + classification metrics")
    print("  Wiring: meta-scaled ALL -> is_valid/is_test -> fitter scoring ports")
    print("  Encoding: CLASS 0/1, outlier_label 0/1, beta=2, k=15 c=0.05")


if __name__ == "__main__":
    main()
