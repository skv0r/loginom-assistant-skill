#!/usr/bin/env python3
"""
Build LOF package from LOF_template.lgp (Loginom 7.3.1 compatible).

Output: packages/lof/lof_package.lgp
"""
from __future__ import annotations

import re
import shutil
import uuid
import zipfile
from pathlib import Path

from lof_native_nodes import (
    calc_istest_from_sample_xml,
    calc_sample_xml,
    export_txt_node_xml,
    link_xml,
    partition_node_xml,
    public_passthrough_xml,
    replace_union_links,
    union_node_xml,
)

from paths import (
    ETL_REFERENCE_LGP,
    LIBS_REL_POSIX,
    LOF_DATA_REL,
    LOF_PACKAGE_LGP,
    LOF_PACKAGE_NAME,
    LOF_TEMPLATE_LGP,
    WORK_LOF_BUILD,
)

TEMPLATE = LOF_TEMPLATE_LGP
OUT_LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_BUILD
LR1_PACKET = ETL_REFERENCE_LGP

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}
# Regenerate unit workflow from XML (avoid stale .bin from template 7.3.2)
DROP_UNIT_BIN = {
    "Unit_0/Unit.bin",
    "Unit_0/Info.bin",
    "Unit_1/Unit.bin",
    "Unit_1/Info.bin",
}

IMPORT_TRAIN_GUID = "d713e1dc-3a94-48d7-a7ee-e8fe5f6f2c20"
IMPORT_TEST_GUID = "f526c35a-d747-43d4-a309-888fc7b4384a"
UNION_GUID = "8669e7c7-f285-486f-9731-1f92301ced06"
OBJECT_GUID = "2b3157aa-435e-46c6-9c8c-23e51408cecf"

PUBLIC_DATASET_GUID = "a8f3c2e1-4b5d-6a7c-8d9e-0f1a2b3c4d5e"
EXPORT_TXT_GUID = "11f9693f-a2d1-4b6f-ae57-e55fe4abb446"
FILTER_CLASS1_GUID = "61671885-e756-4aeb-b4f1-0967584a96ee"
PARTITION_70_GUID = "a1b2c3d4-1111-4222-8333-813d4af7c5f6"
PARTITION_50_GUID = "a2b3c4d5-2222-4333-9444-924e5bf8d6f7"
UNION_POOL_GUID = "b1c2d3e4-3333-4444-a555-b61627c8d9e0"
UNION_FINAL_GUID = "c1d2e3f4-4444-4555-b666-c72738d9e0f1"
UNION_FINAL2_GUID = "d1e2f3a4-5555-4666-c777-d83849e0f1a2"
CALC_TRAIN_SAMPLE_GUID = "e2f3a4b5-6666-4777-d888-e9495af0f2b3"
CALC_VALID_SAMPLE_GUID = "f3a4b5c6-7777-4888-e999-f05a6bf1f3c4"
CALC_TEST_SAMPLE_GUID = "a4b5c6d7-8888-4999-faaa-016b7cf2f4d5"
CALC_ISTEST_FINAL_GUID = "f5a6b7c8-9999-4aaa-bbbb-ccccddddeeee"
PORT_PART_TEACH = "51c20538-def7-374c-851c-a318298b9c80"
PORT_PART_TEST = "0b3d620f-18d5-38da-8d37-7159844f74d8"
PORT_FILTER_ELSE = "99559aff-aff4-3e08-8f1e-a290790bba03"
REF_DATASET_GUID = "c0f5e4d3-6b7c-8a9d-0e1f-2a3b4c5d6e7f"
PYTHON_LOF_GUID = "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5e"
REF_VENDOR = "f92b7fc7-d460-4881-9f20-fb75d6c8451f"
PORT_DS_IN = "9dc72a3f-56bf-3bfc-84ec-f979daf4da6b"
PORT_DS_OUT = "4ba0e2c2-69ad-3a32-bbdc-75714efe7a51"
PORT_DATASET_OUT = "58f7e6c3-511e-39d7-8853-036e0a1a7612"
PORT_UNION_TRAIN = "e028600d-9dca-3604-89ce-cd2fdadb4c1c"
PORT_UNION_TEST = "54ae772d-7bcb-36bb-88ac-976dcae031bc"
PORT_UNION_MAIN = PORT_UNION_TRAIN
PORT_UNION_JOIN = PORT_UNION_TEST

PYTHON_SPLIT_CODE = r'''import builtin_data
from builtin_data import InputTable, OutputTable
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split

def _load_canonical_from_files():
    train_path = test_path = None
    for rel in (f"{LOF_DATA_REL}/ecg_train.txt", "ecg_train.txt"):
        if os.path.isfile(rel):
            train_path = rel
            break
    for rel in (f"{LOF_DATA_REL}/ecg_test.txt", "ecg_test.txt"):
        if os.path.isfile(rel):
            test_path = rel
            break
    if not train_path or not test_path:
        return None
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    train = train[train["CLASS"] != 2].copy()
    test = test[test["CLASS"] != 2].copy()
    return pd.concat([train, test], ignore_index=True)


df = to_data_frame(InputTable).copy()
canonical = _load_canonical_from_files()
if canonical is not None and len(canonical) > 0:
    df = canonical
else:
    if "CLASS" in df.columns:
        df = df[df["CLASS"] != 2].copy()
    if "IsTestSet" in df.columns:
        flag = df["IsTestSet"]
        if flag.dtype == object:
            flag = flag.astype(str).str.lower().isin(["true", "1", "yes"])
        else:
            flag = flag.astype(bool)
        df = pd.concat(
            [df[~flag].reset_index(drop=True), df[flag].reset_index(drop=True)],
            ignore_index=True,
        )

df["OBJECT"] = [f"obj{i + 1}" for i in range(len(df))]


def _load_sample_labels():
    cwd = os.getcwd()
    tried = []
    candidates = []
    for rel in (
        "sample_by_object.tsv",
        os.path.join(LOF_DATA_REL, "sample_by_object.tsv"),
        os.path.join("..", LOF_DATA_REL, "sample_by_object.tsv"),
    ):
        candidates.append(os.path.abspath(os.path.join(cwd, rel)))
    seen = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        tried.append(path)
        if not os.path.isfile(path):
            continue
        try:
            lab = pd.read_csv(path, sep="\t", encoding="utf-8-sig")
        except Exception:
            try:
                lab = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
            except Exception:
                continue
        lab.columns = [str(c).strip().lstrip("\ufeff") for c in lab.columns]
        if "OBJECT" not in lab.columns or "SAMPLE" not in lab.columns:
            continue
        if "IsTestSet" not in lab.columns:
            lab["IsTestSet"] = lab["SAMPLE"].astype(str) != "train"
        else:
            ist = lab["IsTestSet"]
            if ist.dtype == object:
                lab["IsTestSet"] = ist.astype(str).str.lower().isin(["true", "1", "yes"])
            else:
                lab["IsTestSet"] = ist.astype(bool)
        return lab[["OBJECT", "SAMPLE", "IsTestSet"]].copy(), tried
    return None, tried


labels, _tried_paths = _load_sample_labels()

if labels is not None:
    out = df.drop(columns=["SAMPLE", "IsTestSet"], errors="ignore").merge(
        labels, on="OBJECT", how="left"
    )
    if out["SAMPLE"].isna().any():
        missing = int(out["SAMPLE"].isna().sum())
        raise ValueError(
            "sample_by_object.tsv: no SAMPLE for " + str(missing) + " OBJECT ids"
        )
else:
    rng = np.random.RandomState(42)
    norm = df[df["CLASS"] == 1].copy()
    anom = df[df["CLASS"] != 1].copy()
    perm = rng.permutation(len(norm))
    n_train = int(round(0.7 * len(norm)))
    train = norm.iloc[perm[:n_train]].copy()
    rest_norm = norm.iloc[perm[n_train:]].copy()
    rest = pd.concat([rest_norm, anom], ignore_index=True)
    valid, test = train_test_split(
        rest, test_size=0.5, random_state=42, stratify=rest["CLASS"]
    )
    train["SAMPLE"] = "train"
    valid["SAMPLE"] = "valid"
    test["SAMPLE"] = "test"
    out = pd.concat([train, valid, test], ignore_index=True)
    out["IsTestSet"] = out["SAMPLE"] != "train"

if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, out, with_index=False)
fill_table(OutputTable, out, with_index=False)
'''

PYTHON_LOF_CODE = r'''import builtin_data
from builtin_data import InputTable, OutputTable
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
import pandas as pd
import numpy as np
from sklearn.metrics import fbeta_score, precision_recall_fscore_support
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

FEATURES = [f"VAR{i}" for i in range(2, 142)]

df = to_data_frame(InputTable).copy()
train_df = df[(df["SAMPLE"] == "train") & (df["CLASS"] == 1)]

rows = []
grid = [(15, 0.02), (15, 0.05), (20, 0.02), (20, 0.05), (25, 0.02), (25, 0.05)]
for k, c in grid:
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train_df[FEATURES])
    for sample in ("valid", "test"):
        scoring = df[df["SAMPLE"] == sample]
        x_score = scaler.transform(scoring[FEATURES])
        model = LocalOutlierFactor(
            n_neighbors=k, contamination=c, novelty=True, n_jobs=-1
        )
        model.fit(x_train)
        pred = model.predict(x_score)
        yt = np.where(scoring["CLASS"].values == 1, 0, 1)
        yp = np.where(pred == -1, 1, 0)
        p, r, f1, _ = precision_recall_fscore_support(
            yt, yp, average="binary", pos_label=1, zero_division=0
        )
        fb = fbeta_score(yt, yp, beta=2, pos_label=1, zero_division=0)
        rows.append(
            {
                "k": k,
                "c": c,
                "SAMPLE": sample,
                "precision": float(p),
                "recall": float(r),
                "f1": float(f1),
                "fbeta": float(fb),
            }
        )

out = pd.DataFrame(rows)
valid = out[out["SAMPLE"] == "valid"].copy()
best_idx = valid["fbeta"].idxmax()
best_k = int(valid.loc[best_idx, "k"])
best_c = float(valid.loc[best_idx, "c"])
if (valid["fbeta"] == valid.loc[best_idx, "fbeta"]).sum() > 1:
    tie = valid[valid["fbeta"] == valid.loc[best_idx, "fbeta"]]
    best_k = int(tie["k"].min())

out["selected_model"] = (out["k"] == best_k) & (out["c"] == best_c)

if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, out, with_index=False)
fill_table(OutputTable, out, with_index=False)
'''


def new_guid() -> str:
    return str(uuid.uuid4())


def xml_escape_code(code: str) -> str:
    return (
        code.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\n", "&#10;")
    )


def calc_node_xml(guid: str, display: str, left: int, top: int, expr: str) -> str:
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{display}" VendorGuid="c7b69712-557f-4e51-bba5-db9cc2659e7a" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t\t<Item Guid="d252e390-f72d-36c4-97fc-60d86186c3c6" Name="Variables" DisplayName="Входные переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных"/>
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
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDerivedDataSourceOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGCalcData">
\t\t\t\t\t\t<Expressions>
\t\t\t\t\t\t\t<Item Name="IsTestSet" DataType="dtBoolean" Expression="{expr}"/>
\t\t\t\t\t\t</Expressions>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def write_package_index(work: Path) -> None:
    (work / "PackageIndex.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<PackageIndex>
\t<PackageInfo XMLFile="\\PackageInfo.xml"/>
\t<References XMLFile="\\References.xml"/>
\t<Reports XMLFile="\\Reports.xml"/>
\t<Variables XMLFile="\\Variables.xml"/>
\t<Units>
\t\t<Item BasePath="\\Unit_0">
\t\t\t<Info XMLFile="\\Unit_0\\Info.xml"/>
\t\t\t<Unit XMLFile="\\Unit_0\\Unit.xml"/>
\t\t</Item>
\t\t<Item BasePath="\\Unit_1">
\t\t\t<Info XMLFile="\\Unit_1\\Info.xml"/>
\t\t\t<Unit XMLFile="\\Unit_1\\Unit.xml"/>
\t\t</Item>
\t</Units>
</PackageIndex>
""",
        encoding="utf-8",
    )


def copy_minimal_root_from_packet1(work: Path) -> None:
    with zipfile.ZipFile(LR1_PACKET) as zf:
        for name in (
            "References.bin",
            "Variables.xml",
            "Variables.bin",
            "Reports.xml",
            "Reports.bin",
        ):
            (work / name).write_bytes(zf.read(name))


def patch_references(work: Path) -> None:
    libs = LIBS_REL_POSIX
    (work / "References.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<References>
\t<Item Guid="22fe6b1c-b3f0-4415-a83f-b32315f00cf3" HintPath="../{libs}/silver_kit/silver_kit/loginom_silver_kit.lgp">
\t\t<Name Guid="f343d16a-62c2-4d3c-a925-e2c2fbed245e" Name="loginom_silver_kit" VersionMask="^3.1.6"/>
\t</Item>
\t<Item Guid="7f239426-d1b4-4236-af18-b8e9fc3f3988" HintPath="../{libs}/python_kits/python_kits/loginom_sklearn_meta.lgp">
\t\t<Name Guid="29e80fae-7e4d-421c-9680-45a797e58ab2" Name="loginom_sklearn_meta" VersionMask="^3.3.1"/>
\t</Item>
\t<Item Guid="af1bdedf-7447-4d10-bda7-436d2157666d" HintPath="../{libs}/python_kits/python_kits/loginom_sklearn_kit.lgp">
\t\t<Name Guid="7fb77bb3-1ebb-44a8-8092-efa3c951300c" Name="loginom_sklearn_kit" VersionMask="^3.3.1"/>
\t</Item>
</References>
""",
        encoding="utf-8",
    )


def patch_package_info(work: Path) -> None:
    text = (work / "PackageInfo.xml").read_text(encoding="utf-8")
    text = re.sub(r'Guid="[^"]+"', f'Guid="{new_guid()}"', text, count=1)
    text = re.sub(r'Name="[^"]+"', f'Name="{LOF_PACKAGE_NAME}"', text, count=1)
    text = re.sub(
        r'ApplicationVersion="[^"]+"',
        'ApplicationVersion="7.3.1"',
        text,
        count=1,
    )
    (work / "PackageInfo.xml").write_text(text, encoding="utf-8")


def patch_unit0(unit_xml: str) -> str:
    unit_xml = unit_xml.replace(
        'FileName="data/ecg_train.txt"',
        f'FileName="{LOF_DATA_REL}/ecg_train.txt"',
    )
    unit_xml = unit_xml.replace(
        'FileName="data/ecg_test.txt"',
        f'FileName="{LOF_DATA_REL}/ecg_test.txt"',
    )

    # Drop link OBJECT -> CLASS=1 (not used for export dataset)
    unit_xml = unit_xml.replace(
        """\t\t\t<Item Guid="92459dee-8435-409b-a143-dbe419522dcc">
\t\t\t\t<SourcePort NodeGuid="2b3157aa-435e-46c6-9c8c-23e51408cecf" PortGuid="4ba0e2c2-69ad-3a32-bbdc-75714efe7a51"/>
\t\t\t\t<TargetPort NodeGuid="61671885-e756-4aeb-b4f1-0967584a96ee" PortGuid="9dc72a3f-56bf-3bfc-84ec-f979daf4da6b"/>
\t\t\t</Item>""",
        "",
    )

    extra_nodes = (
        partition_node_xml(
            PARTITION_70_GUID,
            "Разбиение 70/30 (нормальные)",
            720,
            200,
            70,
            30,
            "smSequence",
            2919,
        )
        + partition_node_xml(
            PARTITION_50_GUID,
            "Разбиение 50/50 (valid/test)",
            960,
            360,
            50,
            50,
            "smStratified",
            1190,
            stratify_class=True,
        )
        + union_node_xml(
            UNION_POOL_GUID,
            "Остаток нормальных + аномалии",
            840,
            320,
            link_sample=False,
            link_object=True,
        )
        + union_node_xml(
            UNION_FINAL_GUID,
            "Объединение train+valid",
            1200,
            240,
            link_sample=True,
            link_object=True,
        )
        + union_node_xml(
            UNION_FINAL2_GUID,
            "Итоговый датасет",
            1360,
            312,
            link_sample=True,
            link_object=True,
        )
        + calc_sample_xml(CALC_TRAIN_SAMPLE_GUID, "SAMPLE train", 880, 120, "train")
        + calc_sample_xml(CALC_VALID_SAMPLE_GUID, "SAMPLE valid", 1120, 400, "valid")
        + calc_sample_xml(CALC_TEST_SAMPLE_GUID, "SAMPLE test", 1120, 520, "test")
        + calc_istest_from_sample_xml(CALC_ISTEST_FINAL_GUID, 1480, 312)
        + public_passthrough_xml(PUBLIC_DATASET_GUID, 1640, 312)
        + export_txt_node_xml(EXPORT_TXT_GUID, "Выход-скрипта.txt", 1680, 312)
    )

    unit_xml = unit_xml.replace("\t\t</Nodes>", extra_nodes + "\n\t\t</Nodes>", 1)

    # Import union: CLASS + VAR* only (IsTestSet once after final SAMPLE merge)
    unit_xml = replace_union_links(unit_xml, UNION_GUID, link_sample=False, link_object=False)

    unit_xml = unit_xml.replace(
        f"""\t\t\t<Item Guid="d0f71851-e9b0-4a14-8059-24b2976b47e1">
\t\t\t\t<SourcePort NodeGuid="{UNION_GUID}" PortGuid="{PORT_DS_OUT}"/>
\t\t\t\t<TargetPort NodeGuid="{OBJECT_GUID}" PortGuid="{PORT_DS_IN}"/>
\t\t\t</Item>""",
        link_xml(UNION_GUID, PORT_DS_OUT, OBJECT_GUID, PORT_DS_IN)
        + link_xml(OBJECT_GUID, PORT_DS_OUT, FILTER_CLASS1_GUID, PORT_DS_IN)
        + link_xml(FILTER_CLASS1_GUID, PORT_DS_OUT, PARTITION_70_GUID, PORT_DS_IN)
        + link_xml(FILTER_CLASS1_GUID, PORT_FILTER_ELSE, UNION_POOL_GUID, PORT_UNION_JOIN)
        + link_xml(PARTITION_70_GUID, PORT_PART_TEST, UNION_POOL_GUID, PORT_UNION_MAIN)
        + link_xml(PARTITION_70_GUID, PORT_PART_TEACH, CALC_TRAIN_SAMPLE_GUID, PORT_DS_IN)
        + link_xml(UNION_POOL_GUID, PORT_DS_OUT, PARTITION_50_GUID, PORT_DS_IN)
        + link_xml(PARTITION_50_GUID, PORT_PART_TEACH, CALC_VALID_SAMPLE_GUID, PORT_DS_IN)
        + link_xml(PARTITION_50_GUID, PORT_PART_TEST, CALC_TEST_SAMPLE_GUID, PORT_DS_IN)
        + link_xml(CALC_TRAIN_SAMPLE_GUID, PORT_DS_OUT, UNION_FINAL_GUID, PORT_UNION_MAIN)
        + link_xml(CALC_VALID_SAMPLE_GUID, PORT_DS_OUT, UNION_FINAL_GUID, PORT_UNION_JOIN)
        + link_xml(UNION_FINAL_GUID, PORT_DS_OUT, UNION_FINAL2_GUID, PORT_UNION_MAIN)
        + link_xml(CALC_TEST_SAMPLE_GUID, PORT_DS_OUT, UNION_FINAL2_GUID, PORT_UNION_JOIN)
        + link_xml(UNION_FINAL2_GUID, PORT_DS_OUT, CALC_ISTEST_FINAL_GUID, PORT_DS_IN)
        + link_xml(CALC_ISTEST_FINAL_GUID, PORT_DS_OUT, PUBLIC_DATASET_GUID, PORT_DS_IN)
        + link_xml(PUBLIC_DATASET_GUID, PORT_DS_OUT, EXPORT_TXT_GUID, PORT_DS_IN),
    )

    return unit_xml


def python_node_xml(guid: str, display: str, left: int, top: int, code: str) -> str:
    code_xml = xml_escape_code(code)
    return f"""
\t\t\t<Item Guid="{guid}" DisplayName="{display}" VendorGuid="70a6c99d-a725-4309-b05c-898c8072c3cd" GenerateNodeTitle="false">
\t\t\t\t<InputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_IN}" Name="DataSource" DisplayName="Входной источник данных"/>
\t\t\t\t\t<Item Guid="d252e390-f72d-36c4-97fc-60d86186c3c6" Name="Variables" DisplayName="Входные переменные"/>
\t\t\t\t</InputPorts>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DATASET_OUT}" Name="DataSet" DisplayName="Выходной набор данных"/>
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
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DATASET_OUT}" Name="DataSet" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGDataSetOutputSocket">
\t\t\t\t\t\t\t\t<DataSource SyncThroughColumns="true">
\t\t\t\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t\t\t\t</DataSource>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGPythonEngine" Code="{code_xml}" CodeConfigurableColumns="true">
\t\t\t\t\t\t<ColumnDefs/>
\t\t\t\t\t</Engine>
\t\t\t\t</Component>
\t\t\t\t<Position Left="{left}" Top="{top}"/>
\t\t\t</Item>"""


def reference_node_xml() -> str:
    return f"""
\t\t\t<Item Guid="{REF_DATASET_GUID}" DisplayName="Датасет из подготовки выборок" VendorGuid="{REF_VENDOR}" OriginalVendorGuid="{REF_VENDOR}" IsSealedVendor="true" GenerateNodeTitle="false">
\t\t\t\t<InputPorts/>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных"/>
\t\t\t\t</OutputPorts>
\t\t\t\t<ServiceInputPorts>
\t\t\t\t\t<Item Guid="00bd0b43-e4b5-3ac1-b95a-ac1bee14f858" Name="SynchronizationInputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="66c6387c-574a-3a7a-b4a2-8a711477953b" Name="NodeReference" DisplayName="Ссылка на узел"/>
\t\t\t\t</ServiceInputPorts>
\t\t\t\t<ServiceOutputPorts>
\t\t\t\t\t<Item Guid="ca080ff0-2342-32b0-b480-586f9747bace" Name="SynchronizationOutputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="e98be5ba-c627-3a55-af82-a399dd13c73b" Name="ComponentOutputPort" DisplayName="Компонент"/>
\t\t\t\t\t<Item Guid="58922a98-d1ea-36de-9099-3ce26fe160e2" Name="DependentNodeOutputPort" DisplayName="Зависимые узлы"/>
\t\t\t\t</ServiceOutputPorts>
\t\t\t\t<Component xsi:type="TBGReferenceNodeComponent">
\t\t\t\t\t<InputSockets>
\t\t\t\t\t\t<Item Guid="66c6387c-574a-3a7a-b4a2-8a711477953b" Name="NodeReference" DisplayName="Ссылка на узел">
\t\t\t\t\t\t\t<Socket xsi:type="TBGModelInputSocket">
\t\t\t\t\t\t\t\t<Constraints/>
\t\t\t\t\t\t\t</Socket>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</InputSockets>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="{PORT_DS_OUT}" Name="DataSource" DisplayName="Выходной набор данных">
\t\t\t\t\t\t\t<Socket xsi:type="TBGModelOutputSocket"/>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGReferenceNodeComponentEngine" GlobalNodeID="{PUBLIC_DATASET_GUID}"/>
\t\t\t\t</Component>
\t\t\t\t<Position Left="120" Top="280"/>
\t\t\t</Item>"""


def patch_unit1(unit_xml: str) -> str:
    # Reference node via XML crashes Loginom 7.3.1 — connect dataset in UI manually.
    nodes = python_node_xml(
        PYTHON_LOF_GUID,
        "LOF: метрики k,c (valid/test)",
        420,
        280,
        PYTHON_LOF_CODE,
    )
    unit_xml = unit_xml.replace("<Nodes/>", f"<Nodes>{nodes}\n\t\t</Nodes>", 1)
    return unit_xml


def pack(work: Path, out_lgp: Path) -> None:
    if out_lgp.exists():
        shutil.copy2(out_lgp, out_lgp.with_suffix(".lgp.bak"))
        out_lgp.unlink()
    with zipfile.ZipFile(out_lgp, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(work.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(work).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)


def build() -> None:
    if not TEMPLATE.exists():
        raise FileNotFoundError(TEMPLATE)

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    with zipfile.ZipFile(TEMPLATE) as zf:
        zf.extractall(WORK)

    patch_package_info(WORK)
    patch_references(WORK)
    write_package_index(WORK)
    copy_minimal_root_from_packet1(WORK)

    u0 = WORK / "Unit_0" / "Unit.xml"
    u0.write_text(patch_unit0(u0.read_text(encoding="utf-8")), encoding="utf-8")

    u1 = WORK / "Unit_1" / "Unit.xml"
    u1.write_text(patch_unit1(u1.read_text(encoding="utf-8")), encoding="utf-8")

    pack(WORK, OUT_LGP)
    print(f"Built {OUT_LGP} (ApplicationVersion=7.3.1)")


if __name__ == "__main__":
    build()
