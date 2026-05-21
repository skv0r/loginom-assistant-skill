#!/usr/bin/env python3
"""
Build regression package (methodology + two Excel files only).

Loginom 7.3 reads PackageIndex.bin in preference to XML — stale .bin from the
multi-unit template caused reference errors. External kit .bin caused reference errors.
"""
from __future__ import annotations

import re
import shutil
import uuid
import zipfile
from pathlib import Path

from paths import (
    ETL_REFERENCE_LGP,
    REGRESSION_DATA_REL,
    REGRESSION_OUT_LGP,
    REGRESSION_PACKAGE_NAME,
    REGRESSION_REFERENCE_LGP,
    REGRESSION_TEMPLATE_LGP,
    WORK_REGRESSION_BUILD,
    WORK_REGRESSION_REF,
)

TEMPLATE_LGP = REGRESSION_TEMPLATE_LGP
OUT_LGP = REGRESSION_OUT_LGP
WORK = WORK_REGRESSION_BUILD
REF = WORK_REGRESSION_REF
LR1_PACKET = ETL_REFERENCE_LGP

XLS_CLINICS = "Число амбулаторно-поликлинических организаций.xlsx"
XLS_CLIENTS = "Клиенты торговой сети.xlsx"

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}


def new_guid() -> str:
    return str(uuid.uuid4())


def ensure_ref_extracted() -> None:
    if (REF / "Unit_0" / "Unit.xml").is_file():
        return
    REF.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(LR1_PACKET) as zf:
        zf.extractall(REF)


def patch_unit0(work: Path) -> None:
    unit0 = work / "Unit_0" / "Unit.xml"
    text = unit0.read_text(encoding="utf-8")
    for xls_name in (XLS_CLINICS, XLS_CLIENTS):
        text = text.replace(
            f'FileName="{xls_name}"',
            f'FileName="{REGRESSION_DATA_REL}/{xls_name}"',
        )
    unit0.write_text(text, encoding="utf-8")


def main() -> None:
    if not TEMPLATE_LGP.is_file():
        raise FileNotFoundError(TEMPLATE_LGP)
    ensure_ref_extracted()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(TEMPLATE_LGP) as zf:
        zf.extractall(WORK)
    patch_unit0(WORK)
    pkg = WORK / "PackageInfo.xml"
    text = pkg.read_text(encoding="utf-8")
    text = re.sub(r'Guid="[^"]+"', f'Guid="{new_guid()}"', text, count=1)
    text = re.sub(
        r'Name="[^"]+"',
        f'Name="{REGRESSION_PACKAGE_NAME}"',
        text,
        count=1,
    )
    pkg.write_text(text, encoding="utf-8")
    if OUT_LGP.exists():
        shutil.copy2(OUT_LGP, OUT_LGP.with_suffix(".lgp.bak"))
        OUT_LGP.unlink()
    OUT_LGP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT_LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN:
                continue
            zf.write(f, arc)
    print(f"Built {OUT_LGP}")


if __name__ == "__main__":
    main()
