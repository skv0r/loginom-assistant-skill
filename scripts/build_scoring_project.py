#!/usr/bin/env python3
"""
Build OTP scoring package (methodology-aligned) from scoring reference template.

- Package name scoring_otp_package
- Data paths: data/scoring/otp_train.lgd, otp_test.lgd
- Adds train import; training branch uses otp_train (not test)
"""
from __future__ import annotations

import re
import shutil
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from paths import (
    SCORING_DATA_REL,
    SCORING_OUT_LGP,
    SCORING_PACKAGE_NAME,
    SCORING_TEMPLATE_LGP,
    WORK_SCORING_BUILD,
)

TEMPLATE_LGP = SCORING_TEMPLATE_LGP
OUT_LGP = SCORING_OUT_LGP
WORK = WORK_SCORING_BUILD

TRAIN_IMPORT_GUID = "b8f4e2a1-3c5d-4e6f-9a0b-1c2d3e4f5a6b"
TEST_IMPORT_GUID = "52ef0a63-9e72-435e-922b-826021d4a983"
# Link: import -> missing values (training pipeline)
TRAIN_TO_MISSING_LINK = "7193f707-3b63-41b7-9658-55ff45bfa5b6"


def new_guid() -> str:
    return str(uuid.uuid4())


def patch_package(work: Path) -> None:
    pkg_info = work / "PackageInfo.xml"
    text = pkg_info.read_text(encoding="utf-8")
    text = re.sub(r'Guid="[^"]+"', f'Guid="{new_guid()}"', text, count=1)
    text = re.sub(r'Name="[^"]+"', f'Name="{SCORING_PACKAGE_NAME}"', text, count=1)
    pkg_info.write_text(text, encoding="utf-8")

    (work / "References.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<References>
\t<Item Guid="f89a06b2-01e3-4ea2-a8fb-83a0fa559e5d" HintPath="loginom_silver_kit.lgp">
\t\t<Name Guid="f343d16a-62c2-4d3c-a925-e2c2fbed245e" Name="loginom_silver_kit" VersionMask="^3.1.1"/>
\t</Item>
\t<Item Guid="074d4004-3482-469c-81c0-08ca3cdeab59" HintPath="loginom_category_kit.lgp">
\t\t<Name Guid="474e0c86-7b8d-437e-a765-cbe4e89f743b" Name="loginom_category_kit" VersionMask="^3.1.0"/>
\t</Item>
</References>
""",
        encoding="utf-8",
    )

    unit_xml = work / "Unit_0" / "Unit.xml"
    if not unit_xml.exists():
        raise FileNotFoundError(unit_xml)

    ux = unit_xml.read_text(encoding="utf-8")

    # Fix test import path and display name
    ux = ux.replace(
        f'Guid="{TEST_IMPORT_GUID}" DisplayName="otp_test.lgd"',
        f'Guid="{TEST_IMPORT_GUID}" DisplayName="[Тест] otp_test.lgd"',
    )
    ux = ux.replace(
        'FileName="otp_test.lgd"',
        f'FileName="{SCORING_DATA_REL}/otp_test.lgd"',
    )

    # Insert train import after test import block (before WOE_ENCODER)
    train_block = f"""\
\t\t\t<Item Guid="{TRAIN_IMPORT_GUID}" DisplayName="[Обучение] otp_train.lgd" VendorGuid="35a6e054-ee0c-42f6-bda6-af10b57a36aa">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="78ce58f4-e818-3754-bc2e-6af868677420" Name="Connection" DisplayName="Подключение"/>
\t\t\t\t\t<Item Guid="455b65c3-0587-3a9c-b47e-9b0d285bff3c" Name="ControlVariables" DisplayName="Управляющие переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="58f7e6c3-511e-39d7-8853-036e0a1a7612" Name="DataSet" DisplayName="Набор данных"/>
\t\t\t\t</OutputPorts>
\t\t\t\t<ServiceInputPorts>
\t\t\t\t\t<Item Guid="00bd0b43-e4b5-3ac1-b95a-ac1bee14f858" Name="SynchronizationInputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t</ServiceInputPorts>
\t\t\t\t<ServiceOutputPorts>
\t\t\t\t\t<Item Guid="ca080ff0-2342-32b0-b480-586f9747bace" Name="SynchronizationOutputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="e98be5ba-c627-3a55-af82-a399dd13c73b" Name="ComponentOutputPort" DisplayName="Компонент"/>
\t\t\t\t\t<Item Guid="58922a98-d1ea-36de-9099-3ce26fe160e2" Name="DependentNodeOutputPort" DisplayName="Зависимые узлы"/>
\t\t\t\t</ServiceOutputPorts>
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="78ce58f4-e818-3754-bc2e-6af868677420" Name="Connection" DisplayName="Подключение">
\t\t\t\t\t\t\t<Socket xsi:type="TBGConnectionInputSocket" Virgin="true">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="455b65c3-0587-3a9c-b47e-9b0d285bff3c" Name="ControlVariables" DisplayName="Управляющие переменные">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneVariablesSocket" Virgin="true">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<Variables SyncThroughVariables="true">
\t\t\t\t\t\t\t\t\t<Elements/>
\t\t\t\t\t\t\t\t</Variables>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="58f7e6c3-511e-39d7-8853-036e0a1a7612" Name="DataSet" DisplayName="Набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDataSetOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGImportNative" FileName="{SCORING_DATA_REL}/otp_train.lgd"/>
\t\t\t\t</Component>
\t\t\t\t<Position Left="88" Top="200"/>
\t\t\t</Item>
"""

    marker = f'<Item Guid="e7c7eb46-0fc5-40da-9933-675ebd890c04" DisplayName="WOE_ENCODER-1"'
    if TRAIN_IMPORT_GUID not in ux:
        if marker not in ux:
            raise RuntimeError("Cannot find insertion point for train import")
        ux = ux.replace(marker, train_block + "\n\t\t\t" + marker, 1)

    # Training branch: train -> missing values (was incorrectly test -> missing)
    ux = re.sub(
        rf'(<Item Guid="{TRAIN_TO_MISSING_LINK}">.*?'
        rf'<SourcePort NodeGuid="){TEST_IMPORT_GUID}(")',
        rf"\1{TRAIN_IMPORT_GUID}\2",
        ux,
        count=1,
        flags=re.DOTALL,
    )

    unit_xml.write_text(ux, encoding="utf-8")

    for info in work.glob("Unit_*/Info.xml"):
        t = info.read_text(encoding="utf-8")
        t = re.sub(r'Name="[^"]*"', 'Name="Скоринг ОТП"', t, count=1)
        info.write_text(t, encoding="utf-8")


def verify_xml(work: Path) -> None:
    unit_xml = work / "Unit_0" / "Unit.xml"
    ET.parse(unit_xml)
    text = unit_xml.read_text(encoding="utf-8")
    assert f"{SCORING_DATA_REL}/otp_train.lgd" in text
    assert f"{SCORING_DATA_REL}/otp_test.lgd" in text
    assert TRAIN_IMPORT_GUID in text
    assert f'SourcePort NodeGuid="{TRAIN_IMPORT_GUID}"' in text


def pack(work: Path, out_lgp: Path) -> None:
    if out_lgp.exists():
        shutil.copy2(out_lgp, out_lgp.with_suffix(".lgp.bak"))
        out_lgp.unlink()
    with zipfile.ZipFile(out_lgp, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(work.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(work).as_posix())


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    with zipfile.ZipFile(TEMPLATE_LGP) as zf:
        zf.extractall(WORK)

    patch_package(WORK)
    verify_xml(WORK)
    pack(WORK, OUT_LGP)
    print(f"Created: {OUT_LGP}")
    print(f"Size: {OUT_LGP.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
