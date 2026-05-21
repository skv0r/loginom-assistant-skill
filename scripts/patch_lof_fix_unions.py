#!/usr/bin/env python3
"""Patch saved LOF package: fix union links, partition 50/50, public node."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

from lof_native_nodes import replace_union_links

from paths import LOF_PACKAGE_LGP, WORK_LOF_PATCH

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_PATCH

UNION_IMPORT = "8669e7c7-f285-486f-9731-1f92301ced06"
UNION_POOL = "b1c2d3e4-3333-4444-a555-b61627c8d9e0"
UNION_TV = "c1d2e3f4-4444-4555-b666-c72738d9e0f1"
UNION_FINAL = "d1e2f3a4-5555-4666-c777-d83849e0f1a2"
PARTITION_50 = "a2b3c4d5-2222-4333-9444-924e5bf8d6f7"
PUBLIC = "a8f3c2e1-4b5d-6a7c-8d9e-0f1a2b3c4d5e"


def patch_unit_xml(text: str) -> str:
    text = replace_union_links(text, UNION_IMPORT, link_sample=False, link_object=False)
    text = replace_union_links(text, UNION_POOL, link_sample=False, link_object=True)
    text = replace_union_links(text, UNION_TV, link_sample=True, link_object=True)
    text = replace_union_links(text, UNION_FINAL, link_sample=True, link_object=True)
    text = text.replace(
        f'<Item Guid="{PARTITION_50}"',
        f'<Item Guid="{PARTITION_50}"',
    )
    text = re.sub(
        rf'(<Item Guid="{re.escape(PARTITION_50)}"[\s\S]*?'
        rf"<Partition[^>]*PartitionMethod=\"smStratified\"[^>]*>\s*"
        rf"<SamplingType/>\s*)<SamplingRecordCount/>",
        r'\1<SamplingRecordCount Teach="50" Test="50"/>',
        text,
        count=1,
    )
    text = re.sub(
        rf'(<Item Guid="{re.escape(PUBLIC)}"[\s\S]*?<Engine xsi:type="TBGCalcData">\s*'
        rf"<Expressions>)[\s\S]*?(</Expressions>)",
        r"\1\2",
        text,
        count=1,
    )
    if "<Expressions/>" not in text and PUBLIC in text:
        text = text.replace(
            "<Expressions>\n\t\t\t\t\t\t</Expressions>",
            "<Expressions/>",
            1,
        )
    return text


def main() -> None:
    if not LGP.is_file():
        raise FileNotFoundError(LGP)

    if WORK.exists():
        import shutil

        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    unit = WORK / "Unit_0" / "Unit.xml"
    unit.write_text(patch_unit_xml(unit.read_text(encoding="utf-8")), encoding="utf-8")

    for bin_name in ("Unit_0/Unit.bin", "Unit_0/Info.bin"):
        p = WORK / bin_name
        if p.exists():
            p.unlink()

    with zipfile.ZipFile(LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(WORK).as_posix())

    print(f"Patched {LGP}")


if __name__ == "__main__":
    main()
