#!/usr/bin/env python3
"""
Replace Unit_1 (sklearn-kit chain) with a reliable Python LOF metrics flow.

Upper output node: valid metrics (SAMPLE=valid, k=15, c=0.05, beta=2)
Lower output node: test metrics (SAMPLE=test)
Keeps XML reference to public dataset from Unit_0 (works in Loginom 7.3.1).
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from build_lof_project import (
    DROP_UNIT_BIN,
    PORT_DS_IN,
    PORT_DS_OUT,
    SKIP_ROOT_BIN,
    link_xml,
    python_node_xml,
)

from paths import LOF_PACKAGE_LGP, WORK_LOF_UNIT1_PY

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_UNIT1_PY

PUBLIC_DATASET = "a8f3c2e1-4b5d-6a7c-8d9e-0f1a2b3c4d5e"
REF_NODE = "e4796837-1c62-43bd-9ef5-4ef59c13da33"
PY_VALID = "92caeb79-9c23-475e-80f9-285ff33943de"
PY_TEST = "40adf7a8-c6a5-4a6b-a64c-c1ceacb2dffb"
PY_GRID = "b1c2d3e4-f5a6-4b7c-8d9e-0f1a2b3c4d5f"
REF_VENDOR = "f92b7fc7-d460-4881-9f20-fb75d6c8451f"


def metrics_code(sample: str, k: int = 15, c: float = 0.05, beta: float = 2) -> str:
    title = "valid" if sample == "valid" else "test"
    return f'''import builtin_data
from builtin_data import InputTable, OutputTable
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, fbeta_score

FEATURES = [f"VAR{{i}}" for i in range(2, 142)]
K, C, BETA = {k}, {c}, {beta}
SAMPLE = "{sample}"

df = to_data_frame(InputTable).copy()
train_df = df[(df["SAMPLE"] == "train") & (df["CLASS"] == 1)]
scoring = df[df["SAMPLE"] == SAMPLE]
if len(scoring) == 0:
    raise ValueError(f"No rows for SAMPLE={{SAMPLE!r}}")

scaler = StandardScaler()
x_train = scaler.fit_transform(train_df[FEATURES])
x_score = scaler.transform(scoring[FEATURES])
model = LocalOutlierFactor(n_neighbors=K, contamination=C, novelty=True, n_jobs=-1)
model.fit(x_train)
pred = model.predict(x_score)

yt = np.where(scoring["CLASS"].values == 1, 0, 1).astype(int)
yp = np.where(pred == -1, 1, 0).astype(int)

tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
p, r, f1, _ = precision_recall_fscore_support(
    yt, yp, average="binary", pos_label=1, zero_division=0
)
fb = fbeta_score(yt, yp, beta=BETA, pos_label=1, zero_division=0)
acc = (tp + tn) / max(tp + tn + fp + fn, 1)

out = pd.DataFrame(
    [
        ("precision", float(p)),
        ("recall", float(r)),
        ("f1_score", float(f1)),
        ("fbeta_score", float(fb)),
        ("accuracy", float(acc)),
        ("tn", float(tn)),
        ("fp", float(fp)),
        ("fn", float(fn)),
        ("tp", float(tp)),
    ],
    columns=["Метрика", "Значение"],
)

if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, out, with_index=False)
fill_table(OutputTable, out, with_index=False)
'''


GRID_CODE = r'''import builtin_data
from builtin_data import InputTable, OutputTable
from builtin_pandas_utils import to_data_frame, prepare_compatible_table, fill_table
import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import fbeta_score, precision_recall_fscore_support

FEATURES = [f"VAR{i}" for i in range(2, 142)]
df = to_data_frame(InputTable).copy()
train_df = df[(df["SAMPLE"] == "train") & (df["CLASS"] == 1)]

rows = []
for k, c in [(15, 0.02), (15, 0.05), (20, 0.02), (20, 0.05), (25, 0.02), (25, 0.05)]:
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
            {"k": k, "c": c, "SAMPLE": sample, "precision": p, "recall": r, "f1": f1, "fbeta": fb}
        )

out = pd.DataFrame(rows)
if isinstance(OutputTable, builtin_data.ConfigurableOutputTableClass):
    prepare_compatible_table(OutputTable, out, with_index=False)
fill_table(OutputTable, out, with_index=False)
'''


def reference_node_xml() -> str:
    return f"""
\t\t\t<Item Guid="{REF_NODE}" DisplayName="Датасет ECG (ссылка)" VendorGuid="{REF_VENDOR}" OriginalVendorGuid="{REF_VENDOR}" IsSealedVendor="true" GenerateNodeTitle="false">
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
\t\t\t\t\t<Engine xsi:type="TBGReferenceNodeComponentEngine" GlobalNodeID="{PUBLIC_DATASET}"/>
\t\t\t\t\t<SocketTypes Count="1">
\t\t\t\t\t\t<I>09de0d3c-a7f0-4739-8ac0-5bb3ded15a2d</I>
\t\t\t\t\t</SocketTypes>
\t\t\t\t</Component>
\t\t\t\t<Position Left="128" Top="328"/>
\t\t\t</Item>"""


def service_tail_xml() -> str:
    return f"""
\t\t<ServiceNodes>
\t\t\t<Item Guid="6620f9de-e585-39c7-88a9-35255088ebb7" Name="VariablesNode" DisplayName="Переменные сценария" VendorGuid="af096bfc-0c02-4126-89f5-bc3a1b585321" OriginalVendorGuid="af096bfc-0c02-4126-89f5-bc3a1b585321" IsSealedVendor="true" GlobalNodeID="35905ad1-f7dc-4f27-9721-a202487d5473">
\t\t\t\t<InputPorts/>
\t\t\t\t<OutputPorts>
\t\t\t\t\t<Item Guid="b671426b-642b-3e7c-b9a9-9653573f3199" Name="Variables" DisplayName="Переменные"/>
\t\t\t\t</OutputPorts>
\t\t\t\t<ServiceInputPorts/>
\t\t\t\t<ServiceOutputPorts>
\t\t\t\t\t<Item Guid="ca080ff0-2342-32b0-b480-586f9747bace" Name="SynchronizationOutputPort" DisplayName="Порядок выполнения"/>
\t\t\t\t\t<Item Guid="e98be5ba-c627-3a55-af82-a399dd13c73b" Name="ComponentOutputPort" DisplayName="Компонент"/>
\t\t\t\t\t<Item Guid="58922a98-d1ea-36de-9099-3ce26fe160e2" Name="DependentNodeOutputPort" DisplayName="Зависимые узлы"/>
\t\t\t\t</ServiceOutputPorts>
\t\t\t\t<Component>
\t\t\t\t\t<OutputSockets>
\t\t\t\t\t\t<Item Guid="b671426b-642b-3e7c-b9a9-9653573f3199" Name="Variables" DisplayName="Переменные">
\t\t\t\t\t\t\t<Socket xsi:type="TBGModelVariablesOutputSocket"/>
\t\t\t\t\t\t</Item>
\t\t\t\t\t</OutputSockets>
\t\t\t\t\t<Engine xsi:type="TBGModelVariablesComponentEngine"/>
\t\t\t\t</Component>
\t\t\t</Item>
\t\t</ServiceNodes>
\t\t<ServiceLinks>
\t\t\t<Item Guid="fff6b7a9-949f-417b-9356-556c6aa4a766">
\t\t\t\t<SourcePort NodeGuid="{PUBLIC_DATASET}" PortGuid="e98be5ba-c627-3a55-af82-a399dd13c73b"/>
\t\t\t\t<TargetPort NodeGuid="{REF_NODE}" PortGuid="66c6387c-574a-3a7a-b4a2-8a711477953b"/>
\t\t\t</Item>
\t\t</ServiceLinks>
\t\t<Annotations>
\t\t\t<Item Guid="66288e98-7891-4952-9edb-960b2057a3e6" StyleNum="1" Text="LOF (sklearn), novelty=True, z-нормализация на train (только CLASS=1).&#10;Метрики: valid (верхний узел), test (нижний). k=15, c=0.05, Fbeta beta=2.&#10;Сетка k,c — узел «Сводка k,c».">
\t\t\t\t<Position Left="248" Top="144" Width="488" Height="720"/>
\t\t\t</Item>
\t\t\t<Item Guid="605608f2-4256-4b52-8fe2-51b667f5512a" StyleNum="2" Text="Ссылка на публичный датасет (сценарий 1)">
\t\t\t\t<Position Left="80" Top="216" Width="152" Height="240"/>
\t\t\t</Item>
\t\t\t<Item Guid="80e3a009-7f51-43f1-9c34-b96639bdbe7c" StyleNum="5" Text="Верх: valid. Низ: test. Ожидаемо fn≈0–5, recall≈0.9+ (k=15, c=0.05).">
\t\t\t\t<Position Left="1000" Top="152" Width="776" Height="400"/>
\t\t\t</Item>
\t\t</Annotations>"""


def build_unit1_xml() -> str:
    nodes = (
        reference_node_xml()
        + python_node_xml(
            PY_VALID,
            "Метрики LOF — valid (k=15, c=0.05)",
            1560,
            224,
            metrics_code("valid"),
        )
        + python_node_xml(
            PY_TEST,
            "Метрики LOF — test (k=15, c=0.05)",
            1560,
            384,
            metrics_code("test"),
        )
        + python_node_xml(
            PY_GRID,
            "Сводка Fbeta по k,c (valid/test)",
            900,
            520,
            GRID_CODE,
        )
    )
    links = (
        link_xml(REF_NODE, PORT_DS_OUT, PY_VALID, PORT_DS_IN)
        + link_xml(REF_NODE, PORT_DS_OUT, PY_TEST, PORT_DS_IN)
        + link_xml(REF_NODE, PORT_DS_OUT, PY_GRID, PORT_DS_IN)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Unit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
\t<WorkFlow xsi:type="TBGPackageModelWorkFlow">
\t\t<Nodes>
{nodes}
\t\t</Nodes>
\t\t<Links>
{links}
\t\t</Links>
{service_tail_xml()}
\t</WorkFlow>
</Unit>
"""


def main() -> None:
    if not LGP.is_file():
        raise FileNotFoundError(LGP)

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    unit1 = build_unit1_xml()
    (WORK / "Unit_1" / "Unit.xml").write_text(unit1, encoding="utf-8")

    bak = LGP.with_suffix(".lgp.bak_python_unit1")
    shutil.copy2(LGP, bak)
    try:
        LGP.unlink()
    except OSError as exc:
        raise SystemExit(f"Close Loginom and unlock {LGP}: {exc}") from exc

    with zipfile.ZipFile(LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)

    print(f"Rebuilt Unit_1 in {LGP}")
    print(f"  Backup: {bak}")
    print(f"  Nodes: reference + valid metrics + test metrics + k,c grid")
    print("  Run scenario 1, then scenario 2. Upper=valid, lower=test.")


if __name__ == "__main__":
    main()
