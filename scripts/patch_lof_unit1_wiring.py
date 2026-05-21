#!/usr/bin/env python3
"""Fix Unit_1 links: SAMPLE=valid/test -> model.fitter scoring port."""
from __future__ import annotations

import re
import uuid
import zipfile
from pathlib import Path

from paths import LOF_PACKAGE_LGP, WORK_LOF_NATIVE_WIRING

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_NATIVE_WIRING

META = "8a85064b-d064-47f3-9341-0c2d4cac30f6"
PORT_META_ALL = "a98c9da3-c96e-44b7-9344-c92a8d5bdcb8"
PORT_META_TRAIN = "b7f3e617-b622-4c5f-8e3d-285269ccf4c3"
IS_VALID = "e2a95e1d-aa96-4a92-8a0b-3aa28127b4a7"
IS_TEST = "f7a8b9c0-d1e2-4345-a678-901234567abc"
FITTER_VALID = "e9f6e143-ca72-47ed-aa6a-e3f90790a876"
FITTER_TEST = "36e30bc4-f1d9-441e-bbc0-855e7c21b6b9"
PORT_DS_IN = "9dc72a3f-56bf-3bfc-84ec-f979daf4da6b"
PORT_DS_OUT = "4ba0e2c2-69ad-3a32-bbdc-75714efe7a51"
PORT_SCORE = "dd84ef4f-2b30-4c67-bd29-2a5304b8fc58"
VENDOR_FILTER = "a0e49d86-6fe3-43fc-8046-29d1ce92c03d"

REMOVE_LINKS = {
    "1681a9c2-fb9a-44a8-85ae-6148b67a09f2",
    "839a1dfb-5e33-4c89-98a7-5e8a562326f2",
    "4f1c15a7-adcc-48e7-af75-dd38036ac07f",
    "6b00b699-1120-4ba7-9c72-c2d8e38337b0",
    "4c741b26-f066-4eb0-b052-da905c7f5334",
}


def sample_filter_node(guid: str, display: str, sample: str, left: int, top: int) -> str:
    filt_guid = str(uuid.uuid4())
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{display}" VendorGuid="{VENDOR_FILTER}" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Соответствуют условию"/>
\t\t\t\t\t<Item Guid="99559aff-aff4-3e08-8f1e-a290790bba03" Name="DataSourceElse" DisplayName="Не соответствуют условию"/>
\t\t\t\t</OutputPorts>
\t\t\t\t<ServiceInputPorts>
\t\t\t\t\t<Item Guid="00bd0b43-e4b5-3ac1-b95a-ac1bee14f858" Name="SynchronizationInputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="455b65c3-0587-3a9c-b47e-9b0d285bff3c" Name="ControlVariables" DisplayName="Управляющие переменные"/>
\t\t\t\t</ServiceInputPorts>
\t\t\t\t<ServiceOutputPorts>
\t\t\t\t\t<Item Guid="ca080ff0-2342-32b0-b480-586f9747bace" Name="SynchronizationOutputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="e98be5ba-c627-3a55-af82-a399dd13c73b" Name="ComponentOutputPort" DisplayName="Компонент"/>
\t\t\t\t\t<Item Guid="58922a98-d1ea-36de-9099-3ce26fe160e2" Name="DependentNodeOutputPort" DisplayName="Зависимые узлы"/>
\t\t\t\t</ServiceOutputPorts>
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs>
\t\t\t\t\t\t\t\t\t\t<Item Name="SAMPLE" DataType="dtString" DataKind="dkDiscrete" UsageType="utActive" InputColumnInfoName="SAMPLE"/>
\t\t\t\t\t\t\t\t\t</ColumnDefs>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Соответствуют условию">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="99559aff-aff4-3e08-8f1e-a290790bba03" Name="DataSourceElse" DisplayName="Не соответствуют условию">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGFilterDataEngine">
\t\t\t\t\t\t<Filter UseGlobalCaseSensitive="false">
\t\t\t\t\t\t\t<Item Guid="{filt_guid}" Name="SAMPLE" ConcatenationType="ctAnd" DataType="dtString" RelationType="frtIn">
\t\t\t\t\t\t\t\t<CompareValueList Count="1">
\t\t\t\t\t\t\t\t\t<I VarType="vrtString">{sample}</I>
\t\t\t\t\t\t\t\t</CompareValueList>
\t\t\t\t\t\t\t</Item>
\t\t\t\t\t\t</Filter>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def link_xml(link_guid: str, src: str, src_port: str, tgt: str, tgt_port: str) -> str:
    return f"""
\t\t\t<Item Guid="{link_guid}">
\t\t\t\t<SourcePort NodeGuid="{src}" PortGuid="{src_port}"/>
\t\t\t\t<TargetPort NodeGuid="{tgt}" PortGuid="{tgt_port}"/>
\t\t\t</Item>"""


def remove_links(text: str, guids: set[str]) -> str:
    for g in guids:
        text = re.sub(
            rf"\s*<Item Guid=\"{re.escape(g)}\"[^>]*>.*?</Item>\s*",
            "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
    return text


def patch(text: str) -> str:
    if IS_TEST not in text:
        insert_at = text.find(f'<Item Guid="{IS_VALID}"')
        if insert_at < 0:
            raise RuntimeError("is_valid node not found")
        text = (
            text[:insert_at]
            + sample_filter_node(IS_TEST, "is_test", "test", 1024, 448)
            + "\n"
            + text[insert_at:]
        )

    text = remove_links(text, REMOVE_LINKS)

    new_links = (
        link_xml(str(uuid.uuid4()), META, PORT_META_ALL, IS_VALID, PORT_DS_IN)
        + link_xml(str(uuid.uuid4()), IS_VALID, PORT_DS_OUT, FITTER_VALID, PORT_SCORE)
        + link_xml(str(uuid.uuid4()), META, PORT_META_TRAIN, FITTER_VALID, PORT_DS_IN)
        + link_xml(str(uuid.uuid4()), META, PORT_META_ALL, IS_TEST, PORT_DS_IN)
        + link_xml(str(uuid.uuid4()), IS_TEST, PORT_DS_OUT, FITTER_TEST, PORT_SCORE)
        + link_xml(str(uuid.uuid4()), META, PORT_META_TRAIN, FITTER_TEST, PORT_DS_IN)
    )
    text = text.replace("\t\t</Links>", new_links + "\t\t</Links>", 1)
    return text


def main() -> None:
    import shutil

    if WORK.exists():
        import shutil as sh

        sh.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    path = WORK / "Unit_1" / "Unit.xml"
    text = patch(path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")

    from fix_lof_unit1_metrics import DROP_UNIT_BIN, SKIP_ROOT_BIN

    bak = LGP.with_suffix(".lgp.bak_native")
    shutil.copy2(LGP, bak)
    LGP.unlink()
    with zipfile.ZipFile(LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)
    print(f"Wiring patched in {LGP}")


if __name__ == "__main__":
    main()
