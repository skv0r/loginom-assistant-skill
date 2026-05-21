#!/usr/bin/env python3
"""
Fix LOF Unit_1 metrics chain (template-based):
- y_true (CLASS): 0=normal, 1=anomaly (2..5 -> 1, 1 -> 0)
- y_pred (outlier_label): 0=inlier, 1=outlier (1 -> 0, -1 -> 1)
- Do not re-apply sklearn-style CLASS rules in final replace node (928f35a2)
- beta=2, model path C:\\model\\k15_c05
"""
from __future__ import annotations

import re
import shutil
import uuid
import zipfile
from pathlib import Path

from paths import LOF_PACKAGE_LGP, WORK_LOF_FIX_METRICS

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_FIX_METRICS

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}
DROP_UNIT_BIN = {
    "Unit_0/Unit.bin",
    "Unit_0/Info.bin",
    "Unit_1/Unit.bin",
    "Unit_1/Info.bin",
}

NODE_CLASS_BINARY = (
    "928f35a2-cacf-4f40-a824-d9b65e019fdb",  # valid: CLASS + outlier_label
    "15926c8b-d23c-4f84-900d-5d13402fdfe4",  # test: CLASS + outlier_label
)
NODE_OUTLIER = (
    "928f35a2-cacf-4f40-a824-d9b65e019fdb",
    "15926c8b-d23c-4f84-900d-5d13402fdfe4",
)

CLASS_BINARY_REPLACE = """
\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g3}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="3"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>
\t\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g4}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="4"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>
\t\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g2}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="2"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>
\t\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g5}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="5"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>
\t\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g1}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="0"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>"""

OUTLIER_BINARY_REPLACE = """
\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g1}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="0"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>
\t\t\t\t\t\t\t\t\t\t\t\t\t<Item Guid="{g2}">
\t\t\t\t\t\t\t\t\t\t\t\t\t<DataValue DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="-1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</DataValue>
\t\t\t\t\t\t\t\t\t\t\t\t\t<ReplaceBy DataType="dtInteger">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<Value xsi:type="TBGIntegerVariableContainer" Value="1"/>
\t\t\t\t\t\t\t\t\t\t\t\t\t</ReplaceBy>
\t\t\t\t\t\t\t\t\t\t\t\t\t</Item>"""


def _column_replace_pattern(node_guid: str, column: str) -> str:
    return (
        rf"(<Item Guid=\"{re.escape(node_guid)}\"[^>]*>.*?)"
        rf'(<Item Name="{re.escape(column)}"[^>]*>.*?<ReplaceTable[^>]*>\s*)'
        rf"(?:<Items>.*?</Items>\s*)?"
        rf"(<RegExpressions/>.*?</ReplaceTable>)"
    )


def patch_class_binary(text: str, node_guid: str) -> str:
    g = [str(uuid.uuid4()) for _ in range(5)]
    block = CLASS_BINARY_REPLACE.format(
        g2=g[0], g3=g[1], g4=g[2], g5=g[3], g1=g[4]
    )
    pattern = _column_replace_pattern(node_guid, "CLASS")

    def repl(m: re.Match[str]) -> str:
        return m.group(1) + m.group(2) + "<Items>" + block + "\n\t\t\t\t\t\t\t\t\t\t\t</Items>\n\t\t\t\t\t\t\t\t\t\t\t" + m.group(3)

    new_text, n = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"CLASS replace not patched for node {node_guid} (n={n})")
    return new_text


def clear_class_replace(text: str, node_guid: str) -> str:
    pattern = _column_replace_pattern(node_guid, "CLASS")

    def repl(m: re.Match[str]) -> str:
        return m.group(1) + m.group(2) + "<Items/>\n\t\t\t\t\t\t\t\t\t\t\t" + m.group(3)

    new_text, n = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"CLASS clear not applied for node {node_guid} (n={n})")
    return new_text


def patch_outlier_binary(text: str, node_guid: str) -> str:
    g = [str(uuid.uuid4()) for _ in range(2)]
    block = OUTLIER_BINARY_REPLACE.format(g1=g[0], g2=g[1])
    pattern = _column_replace_pattern(node_guid, "outlier_label")

    def repl(m: re.Match[str]) -> str:
        return m.group(1) + m.group(2) + "<Items>" + block + "\n\t\t\t\t\t\t\t\t\t\t\t</Items>\n\t\t\t\t\t\t\t\t\t\t\t" + m.group(3)

    new_text, n = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"outlier_label replace not patched for node {node_guid} (n={n})")
    return new_text


def fix_broken_items_wrappers(text: str) -> str:
    """Repair ReplaceTable blocks where <Items> was dropped by a bad patch."""
    text = re.sub(
        r'(<ReplaceTable(?: ReplaceMode="rmTable")?>)\s*\n(\s*<Item Guid=")',
        r"\1\n\t\t\t\t\t\t\t\t\t\t\t<Items>\n\2",
        text,
    )
    text = re.sub(
        r"(</Item>\s*\n)(\s*<RegExpressions/>)",
        r"\1\t\t\t\t\t\t\t\t\t\t\t</Items>\n\2",
        text,
    )
    return text


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
    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    text = (WORK / "Unit_1" / "Unit.xml").read_text(encoding="utf-8")
    text = fix_broken_items_wrappers(text)

    for guid in NODE_CLASS_BINARY:
        text = patch_class_binary(text, guid)
    for guid in NODE_OUTLIER:
        text = patch_outlier_binary(text, guid)

    text, n_beta = re.subn(
        r'(__baseName="beta">\s*<DefaultValue[^>]*Value=")4(")',
        r"\g<1>2\2",
        text,
    )

    text = text.replace(r"C:\model", r"C:\model\k15_c05")
    text = text.replace("../../../8/model", r"C:\model\k15_c05")
    text = text.replace("../../../../data/lof/model", r"C:\model\k15_c05")

    text = re.sub(
        r'(__baseName="params">\s*<DefaultValue[^>]*Value=")[^"]+(")',
        r"\g<1>n_neighbors=15,contamination=0.05\2",
        text,
        count=1,
    )

    (WORK / "Unit_1" / "Unit.xml").write_text(text, encoding="utf-8")

    bak = LGP.with_suffix(".lgp.bak_metrics")
    if LGP.exists():
        shutil.copy2(LGP, bak)
        try:
            LGP.unlink()
        except OSError as exc:
            raise SystemExit(
                f"Close Loginom and unlock {LGP} before re-running ( {exc} )"
            ) from exc

    with zipfile.ZipFile(LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)

    print(f"Patched {LGP}")
    print(f"  CLASS binary: {', '.join(NODE_CLASS_BINARY)}")
    print(f"  outlier_label 1->0, -1->1: {', '.join(NODE_OUTLIER)}")
    print(f"  beta=2 replacements: {n_beta}")
    print("  model path: C:\\model\\k15_c05")


if __name__ == "__main__":
    main()
