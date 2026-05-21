"""XML builders for LOF Unit_0 native Loginom prep chain."""
from __future__ import annotations

import re
import uuid

VENDOR_CALC = "c7b69712-557f-4e51-bba5-db9cc2659e7a"
VENDOR_FILTER = "a0e49d86-6fe3-43fc-8046-29d1ce92c03d"
VENDOR_PARTITION = "b2161dca-d25a-440e-8833-813d4af7c5f6"
VENDOR_UNION = "f5aa91d2-9fe5-439d-9f7f-1e17996da272"

PORT_DS_IN = "9dc72a3f-56bf-3bfc-84ec-f979daf4da6b"
PORT_DS_OUT = "4ba0e2c2-69ad-3a32-bbdc-75714efe7a51"
PORT_FILTER_ELSE = "99559aff-aff4-3e08-8f1e-a290790bba03"
PORT_PART_TEACH = "51c20538-def7-374c-851c-a318298b9c80"
PORT_PART_TEST = "0b3d620f-18d5-38da-8d37-7159844f74d8"
PORT_UNION_MAIN = "e028600d-9dca-3604-89ce-cd2fdadb4c1c"
PORT_UNION_JOIN = "54ae772d-7bcb-36bb-88ac-976dcae031bc"
PORT_VARS = "d252e390-f72d-36c4-97fc-60d86186c3c6"
PORT_SYNC_IN = "00bd0b43-e4b5-3ac1-b95a-ac1bee14f858"
PORT_CTRL = "455b65c3-0587-3a9c-b47e-9b0d285bff3c"
PORT_SYNC_OUT = "ca080ff0-2342-32b0-b480-586f9747bace"
PORT_COMP_OUT = "e98be5ba-c627-3a55-af82-a399dd13c73b"
PORT_DEP_OUT = "58922a98-d1ea-36de-9099-3ce26fe160e2"


def new_guid() -> str:
    return str(uuid.uuid4())


def union_links_xml(*, link_sample: bool, link_object: bool = False) -> str:
    """Column mapping for vertical union — CLASS, optional OBJECT/SAMPLE, VAR* (not IsTestSet)."""
    names = ["CLASS"]
    if link_object:
        names.append("OBJECT")
    if link_sample:
        names.append("SAMPLE")
    names.extend(f"VAR{i}" for i in range(2, 142))
    items = []
    for name in names:
        items.append(
            f"""
\t\t\t\t\t\t\t<Item Guid="{new_guid()}">
\t\t\t\t\t\t\t\t<Link Guid="{PORT_UNION_MAIN}" Name="{name}"/>
\t\t\t\t\t\t\t\t<Link Guid="{PORT_UNION_JOIN}" Name="{name}"/>
\t\t\t\t\t\t\t</Item>"""
        )
    return "\n".join(items)


def replace_union_links(
    xml: str, node_guid: str, *, link_sample: bool, link_object: bool = False
) -> str:
    links = union_links_xml(link_sample=link_sample, link_object=link_object)
    pattern = (
        rf'(<Item Guid="{re.escape(node_guid)}"[^>]*>.*?'
        rf'<Engine xsi:type="TBGUnionDataEngine"[^>]*>\s*)'
        rf"<Links>.*?</Links>"
    )
    repl = rf"\1<Links>{links}\n\t\t\t\t\t\t</Links>"
    new_xml, n = re.subn(pattern, repl, xml, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"Union {node_guid}: replaced {n} blocks (expected 1)")
    return new_xml


def link_xml(src_node: str, src_port: str, tgt_node: str, tgt_port: str) -> str:
    return f"""
\t\t\t<Item Guid="{new_guid()}">
\t\t\t\t<SourcePort NodeGuid="{src_node}" PortGuid="{src_port}"/>
\t\t\t\t<TargetPort NodeGuid="{tgt_node}" PortGuid="{tgt_port}"/>
\t\t\t</Item>"""


def _service_ports() -> str:
    return f"""
\t\t\t\t<ServiceInputPorts>
\t\t\t\t\t<Item Guid="{PORT_SYNC_IN}" Name="SynchronizationInputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="{PORT_CTRL}" Name="ControlVariables" DisplayName="Управляющие переменные"/>
\t\t\t\t</ServiceInputPorts>
\t\t\t\t<ServiceOutputPorts>
\t\t\t\t\t<Item Guid="{PORT_SYNC_OUT}" Name="SynchronizationOutputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="{PORT_COMP_OUT}" Name="ComponentOutputPort" DisplayName="Компонент"/>
\t\t\t\t\t<Item Guid="{PORT_DEP_OUT}" Name="DependentNodeOutputPort" DisplayName="Зависимые узлы"/>
\t\t\t\t</ServiceOutputPorts>"""


def partition_node_xml(
    guid: str,
    display: str,
    left: int,
    top: int,
    teach_pct: int,
    test_pct: int,
    method: str,
    row_count: int,
    *,
    stratify_class: bool = False,
) -> str:
    if stratify_class:
        input_ds = """
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs>
\t\t\t\t\t\t\t\t\t\t<Item Name="CLASS" DataType="dtInteger" DataKind="dkDiscrete" UsageType="utActive" InputColumnInfoName="CLASS"/>
\t\t\t\t\t\t\t\t\t</ColumnDefs>
\t\t\t\t\t\t\t\t\t<Statistics RowCount="0">
\t\t\t\t\t\t\t\t\t\t<StatInfos>
\t\t\t\t\t\t\t\t\t\t\t<Item Name="CLASS" DataType="dtInteger" DataKind="dkDiscrete" UsageType="utActive"/>
\t\t\t\t\t\t\t\t\t\t</StatInfos>
\t\t\t\t\t\t\t\t\t</Statistics>
\t\t\t\t\t\t\t\t</DataSource>"""
    else:
        input_ds = """
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t\t<Statistics RowCount="0">
\t\t\t\t\t\t\t\t\t\t<StatInfos/>
\t\t\t\t\t\t\t\t\t</Statistics>
\t\t\t\t\t\t\t\t</DataSource>"""
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{display}" VendorGuid="{VENDOR_PARTITION}" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="289668ce-a35b-36f7-a4c7-7e9819fb3fc8" Name="OutDataSetCommon" DisplayName="Общий выходной набор"/>
\t\t\t\t\t<Item Guid="{PORT_PART_TEACH}" Name="OutDataSetTeach" DisplayName="Обучающий выходной набор"/>
\t\t\t\t\t<Item Guid="{PORT_PART_TEST}" Name="OutDataSetTest" DisplayName="Тестовый выходной набор"/>
\t\t\t\t</OutputPorts>
\t\t\t\t{_service_ports()}
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>{input_ds}
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="{PORT_CTRL}" Name="ControlVariables" DisplayName="Управляющие переменные">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneVariablesSocket" Virgin="true">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<Variables SyncThroughVariables="true">
\t\t\t\t\t\t\t\t\t<Elements/>
\t\t\t\t\t\t\t\t</Variables>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="289668ce-a35b-36f7-a4c7-7e9819fb3fc8" Name="OutDataSetCommon" DisplayName="Общий выходной набор">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="{PORT_PART_TEACH}" Name="OutDataSetTeach" DisplayName="Обучающий выходной набор">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="{PORT_PART_TEST}" Name="OutDataSetTest" DisplayName="Тестовый выходной набор">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGPartitionEngine">
\t\t\t\t\t\t<Random RandSeed="42"/>
\t\t\t\t\t\t<Partition TestPriority="false" PartitionMethod="{method}" RowCount="{row_count}">
\t\t\t\t\t\t\t<SamplingType/>
\t\t\t\t\t\t\t<SamplingRecordCount Teach="{teach_pct}" Test="{test_pct}"/>
\t\t\t\t\t\t</Partition>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def union_node_xml(
    guid: str,
    display: str,
    left: int,
    top: int,
    *,
    link_sample: bool = False,
    link_object: bool = False,
) -> str:
    links = union_links_xml(link_sample=link_sample, link_object=link_object)
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{display}" VendorGuid="{VENDOR_UNION}" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_UNION_MAIN}" Name="MainDataSource" DisplayName="Главная таблица"/>
\t\t\t\t\t<Item Guid="{PORT_UNION_JOIN}" Name="JoinedDataSource" DisplayName="Присоединяемая таблица"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных"/>
\t\t\t\t</OutputPorts>
\t\t\t\t{_service_ports()}
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_UNION_MAIN}" Name="MainDataSource" DisplayName="Главная таблица">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="{PORT_UNION_JOIN}" Name="JoinedDataSource" DisplayName="Присоединяемая таблица">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGUnionDataEngine" LinksBackwardCompatibility="true" DisplayNamePrefix="Объединение">
\t\t\t\t\t\t<Links>{links}
\t\t\t\t\t\t</Links>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def calc_sample_xml(guid: str, display: str, left: int, top: int, sample: str) -> str:
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{display}" VendorGuid="{VENDOR_CALC}" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t\t<Item Guid="{PORT_VARS}" Name="Variables" DisplayName="Входные переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных"/>
\t\t\t\t</OutputPorts>
\t\t\t\t{_service_ports()}
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGCalcData">
\t\t\t\t\t\t<Expressions>
\t\t\t\t\t\t\t<Item Name="SAMPLE" DataType="dtString" Expression="&quot;{sample}&quot;"/>
\t\t\t\t\t\t</Expressions>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def calc_istest_from_sample_xml(guid: str, left: int, top: int) -> str:
    """Single IsTestSet column after all branches merged."""
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="IsTestSet (из SAMPLE)" VendorGuid="{VENDOR_CALC}" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t\t<Item Guid="{PORT_VARS}" Name="Variables" DisplayName="Входные переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных"/>
\t\t\t\t</OutputPorts>
\t\t\t\t{_service_ports()}
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGCalcData">
\t\t\t\t\t\t<Expressions>
\t\t\t\t\t\t\t<Item Name="IsTestSet" DataType="dtBoolean" Expression="SAMPLE&lt;&gt;&quot;train&quot;"/>
\t\t\t\t\t\t</Expressions>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def public_passthrough_xml(guid: str, left: int, top: int) -> str:
    """Public node marker for cross-scenario reference (no extra columns)."""
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="Датасет ECG (публичный)" VendorGuid="{VENDOR_CALC}" Visibility="mvPublic" GlobalNodeID="{guid}" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t\t<Item Guid="{PORT_VARS}" Name="Variables" DisplayName="Входные переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных"/>
\t\t\t\t</OutputPorts>
\t\t\t\t{_service_ports()}
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true"><ColumnDefs/></DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGCalcData">
\t\t\t\t\t\t<Expressions/>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def export_txt_node_xml(guid: str, filename: str, left: int, top: int) -> str:
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{filename}" VendorGuid="767b14f8-3852-4463-9ede-7345c4ddb183">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="78ce58f4-e818-3754-bc2e-6af868677420" Name="Connection" DisplayName="Подключение"/>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Источник данных"/>
\t\t\t\t\t<Item Guid="{PORT_CTRL}" Name="ControlVariables" DisplayName="Управляющие переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts/>
\t\t\t\t<ServiceInputPorts>
\t\t\t\t\t<Item Guid="{PORT_SYNC_IN}" Name="SynchronizationInputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t</ServiceInputPorts>
\t\t\t\t<ServiceOutputPorts>
\t\t\t\t\t<Item Guid="{PORT_SYNC_OUT}" Name="SynchronizationOutputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="{PORT_COMP_OUT}" Name="ComponentOutputPort" DisplayName="Компонент"/>
\t\t\t\t\t<Item Guid="{PORT_DEP_OUT}" Name="DependentNodeOutputPort" DisplayName="Зависимые узлы"/>
\t\t\t\t</ServiceOutputPorts>
\t\t\t\t<Component>
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="78ce58f4-e818-3754-bc2e-6af868677420" Name="Connection" DisplayName="Подключение">
\t\t\t\t\t\t\t<Socket xsi:type="TBGConnectionInputSocket" Virgin="true">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Источник данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneDataSourceSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t\t<Item Guid="{PORT_CTRL}" Name="ControlVariables" DisplayName="Управляющие переменные">
\t\t\t\t\t\t\t<Socket xsi:type="TBGTuneVariablesSocket" Virgin="true">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t\t<Variables SyncThroughVariables="true">
\t\t\t\t\t\t\t\t\t<Elements/>
\t\t\t\t\t\t\t\t</Variables>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<Engine xsi:type="TBGExportTextFile" FileName="{filename}" CodePage="65001" LineEnding="leCRLF"/>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""
