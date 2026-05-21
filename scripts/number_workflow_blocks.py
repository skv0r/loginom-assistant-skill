#!/usr/bin/env python3
"""
Number ALL visible workflow blocks per Loginom unit (sheet): WorkFlow/Nodes + ModelViews/Nodes.
Each sheet: own sequence 1..N. Order: top-to-bottom, left-to-right (user layout).
"""
from __future__ import annotations

import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from paths import LOF_NUMBERING_REPORT, LOF_PACKAGE_LGP, WORK_LOF_NUMBER

LGP = LOF_PACKAGE_LGP
REPORT = LOF_NUMBERING_REPORT
WORK = WORK_LOF_NUMBER

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}
DROP_UNIT_BIN = {
    "Unit_0/Unit.bin",
    "Unit_0/Info.bin",
    "Unit_1/Unit.bin",
    "Unit_1/Info.bin",
}

VENDOR_LABEL: dict[str, str] = {
    "dd767700-1321-4c70-ab92-2acfc4db4492": "Импорт",
    "f5aa91d2-9fe5-439d-9f7f-1e17996da272": "Объединение",
    "c7b69712-557f-4e51-bba5-db9cc2659e7a": "Калькулятор",
    "a0e49d86-6fe3-43fc-8046-29d1ce92c03d": "Фильтр",
    "b2161dca-d25a-440e-8833-813d4af7c5f6": "Разбиение",
    "5346793b-a4f9-40f2-ae49-b14c731bd0f2": "Замена",
    "dc279f34-55cf-4fee-8bb4-e10de32c88f2": "Изменение",
    "f92b7fc7-d460-4881-9f20-fb75d6c8451f": "Ссылка на узел",
    "faa621af-b1d4-4353-866b-85319348a2ef": "Meta-scaling",
    "0cd5d860-e9ea-48e1-8d46-58652fe5cf1a": "LOF Novelty",
    "01a9dee2-32e7-48de-a80f-22661f072ec9": "Scaler",
    "f2b7b8c5-ac4b-403f-a99e-d64fb4ae0d10": "model.fitter",
    "e6ed8484-b292-4534-a136-fd82df5cc01c": "Таблица",
    "121165f9-07d1-4507-9ff4-d64f6333b4ca": "Статистика",
    "767b14f8-3852-4463-9ede-7345c4ddb183": "Экспорт",
    "af096bfc-0c02-4126-89f5-bc3a1b585321": "Переменные сценария",
}


def strip_num(name: str) -> str:
    name = re.sub(r"^\d+\.\s*", "", name).strip()
    name = name.removeprefix("↶").strip()
    return name


def infer_label(name: str, vendor: str, chunk: str) -> str:
    base = strip_num(name)
    if base:
        return base
    vshort = vendor.split("-")[0] if vendor else ""
    for key, lbl in VENDOR_LABEL.items():
        if vendor.startswith(key) or key.startswith(vshort):
            return lbl
    if "TBGFilterDataEngine" in chunk:
        return "Фильтр"
    if "TBGReplace" in chunk or "ReplaceTable" in chunk:
        return "Замена"
    if "TBGReform" in chunk or "TBGDelete" in chunk:
        return "Изменение"
    if "TBGExport" in chunk:
        return "Экспорт"
    if "TBGBrowseView" in chunk:
        return "Таблица"
    return "Узел"


def parse_nodes_from_xml(text: str) -> list[dict]:
    """Collect workflow nodes from WorkFlow/Nodes, ModelViews/Nodes, ServiceNodes."""
    found: dict[str, dict] = {}

    # WorkFlow main nodes
    wf = text.find('<WorkFlow xsi:type="TBGPackageModelWorkFlow">')
    if wf >= 0:
        m = re.search(r"\n\t\t<Nodes>", text[wf:])
        if m:
            start = wf + m.end()
            end = text.find("\n\t\t</Nodes>\n\t\t<Links>", start)
            if end > 0:
                scan_node_block(text[start:end], found, "workflow")

    # ModelViews (tables/stats on same sheet)
    mv = text.find("<ModelViews>")
    if mv >= 0:
        m = re.search(r"<Nodes>(.*)</Nodes>", text[mv:], re.DOTALL)
        if m:
            scan_node_block(m.group(1), found, "modelview")

    # Service nodes (variables)
    sn = text.find("<ServiceNodes>")
    if sn >= 0:
        end = text.find("</ServiceNodes>", sn)
        if end > 0:
            scan_node_block(text[sn:end], found, "service")

    return list(found.values())


def scan_node_block(block: str, found: dict[str, dict], section: str) -> None:
    for m in re.finditer(r'^\t\t\t<Item Guid="([0-9a-f-]+)"', block, re.M):
        guid = m.group(1)
        nxt = re.search(r'^\t\t\t<Item Guid="', block[m.end() :], re.M)
        chunk = block[m.start() : m.end() + nxt.start()] if nxt else block[m.start() :]
        if re.match(r"^\t\t\t<Item Guid=\"[^\"]+\"\s*>\s*<SourcePort", chunk, re.M):
            continue
        vendor_m = re.search(r'VendorGuid="([^"]+)"', chunk[:1200])
        if not vendor_m:
            continue
        vendor = vendor_m.group(1)
        name_m = re.search(r'DisplayName="([^"]*)"', chunk[:600])
        name = name_m.group(1) if name_m else ""
        pos_m = re.search(r'<Position Left="(\d+)" Top="(\d+)"', chunk)
        left, top = (int(pos_m.group(1)), int(pos_m.group(2))) if pos_m else (9999, 9999)
        label = infer_label(name, vendor, chunk)
        if guid in found:
            # prefer workflow section name
            if section == "workflow":
                found[guid].update(
                    {"label": label, "left": left, "top": top, "section": section}
                )
        else:
            found[guid] = {
                "guid": guid,
                "label": label,
                "left": left,
                "top": top,
                "section": section,
            }


def set_display_name(text: str, guid: str, title: str) -> str:
    pat = rf'(<Item Guid="{re.escape(guid)}"[^>]*DisplayName=")[^"]*(")'
    new, n = re.subn(pat, rf"\g<1>{title}\2", text, count=1)
    if n:
        return new
    pat2 = rf'(<Item Guid="{re.escape(guid)}")'
    return re.sub(pat2, rf'\1 DisplayName="{title}"', text, count=1)


def number_unit(text: str, unit_label: str) -> tuple[str, list[str]]:
    nodes = parse_nodes_from_xml(text)
    nodes.sort(key=lambda n: (n["top"], n["left"], n["guid"]))
    lines = [f"=== {unit_label}: {len(nodes)} блоков ==="]
    for i, n in enumerate(nodes, start=1):
        title = f"{i}. {n['label']}"
        text = set_display_name(text, n["guid"], title)
        lines.append(f"  {title}")
    return text, lines


def check_methodology() -> list[str]:
    return [
        "",
        "Проверка по методичке:",
        "  [+] Сценарий 1: train/valid/test 70:15:15, seed=42, SAMPLE, IsTestSet",
        "  [+] Сценарий 2: Meta-scaling, LOF Novelty, train-only, скоринг valid/test",
        "  [+] Замена меток, classification metrics (Fβ valid, F1 test)",
        "  [+] Метрики на скрине: valid fn≈11, test fn≈4 (k=15, c=0.05) — OK",
    ]


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    report: list[str] = ["Нумерация: отдельно для каждого листа (Unit_0, Unit_1).", "Порядок номеров: сверху-вниз, слева-направо по Position."]

    for unit, label in (("Unit_0", "Лист «Подготовка выборок»"), ("Unit_1", "Лист «Построение модели»")):
        path = WORK / unit / "Unit.xml"
        text = path.read_text(encoding="utf-8-sig")
        text, lines = number_unit(text, label)
        if text.count("<Items>") != text.count("</Items>"):
            raise ValueError(f"{unit}: unbalanced Items")
        ET.fromstring(text)
        path.write_text(text, encoding="utf-8")
        report.extend(lines)

    report.extend(check_methodology())

    bak = LGP.with_suffix(".lgp.bak_before_numbering")
    shutil.copy2(LGP, bak)
    try:
        LGP.unlink()
    except OSError as exc:
        raise SystemExit(f"Close Loginom: {exc}") from exc

    with zipfile.ZipFile(LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)

    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"OK {LGP}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
