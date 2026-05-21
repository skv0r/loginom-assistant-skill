#!/usr/bin/env python3
"""
Safe visual differentiation of Unit_1: rename + reposition by node GUID only.
Does not insert/delete nodes or rewire links — preserves metrics and XML validity.
"""
from __future__ import annotations

import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from paths import LOF_PACKAGE_LGP, WORK_LOF_LAYOUT

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_LAYOUT

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}
DROP_UNIT_BIN = {
    "Unit_0/Unit.bin",
    "Unit_0/Info.bin",
    "Unit_1/Unit.bin",
    "Unit_1/Info.bin",
}

RENAME: dict[str, str] = {
    "e4796837-1c62-43bd-9ef5-4ef59c13da33": "1. Ссылка: датасет LOF (Unit_0)",
    "8a85064b-d064-47f3-9341-0c2d4cac30f6": "2. Meta-scaling (z по train)",
    "b09518ba-668e-424b-a203-9268c24d2e1d": "3. Параметры Scaler",
    "81b9378b-412a-4c8a-8a8a-0abc4755879d": "4. LOF Novelty (k=15, c=0.05)",
    "d3ecf000-f856-4c3c-b2a9-15160bf1969f": "5. Обучение LOF (simple.fitter)",
    "e9c4c313-1a66-4bdb-8c87-d6bf5edefd29": "6. Сохранение модели LOF",
    "e2a95e1d-aa96-4a92-8a0b-3aa28127b4a7": "7. Отбор SAMPLE=valid",
    "f7a8b9c0-d1e2-4345-a678-901234567abc": "8. Отбор SAMPLE=test",
    "e9f6e143-ca72-47ed-aa6a-e3f90790a876": "9. Скоринг LOF → valid",
    "36e30bc4-f1d9-441e-bbc0-855e7c21b6b9": "10. Скоринг LOF → test",
    "2143c602-da33-479e-a185-8b268d23aa5e": "11. Замена: CLASS (train)",
    "055676ef-d423-4779-8606-9cb01cc26357": "12. Удаление, Изменение (train)",
    "014d564c-96da-4238-ae2f-e99b094baffe": "13. Изменение (valid)",
    "928f35a2-cacf-4f40-a824-d9b65e019fdb": "14. Замена: outlier_label, CLASS (valid)",
    "92caeb79-9c23-475e-80f9-285ff33943de": "15. Метрики Fβ valid",
    "fbcace4c-70fc-4333-9e4c-e4b7cda3c504": "16. Изменение (test)",
    "15926c8b-d23c-4f84-900d-5d13402fdfe4": "17. Замена: outlier_label, CLASS (test)",
    "40adf7a8-c6a5-4a6b-a64c-c1ceacb2dffb": "18. Метрики Fβ test",
    "f3f566b4-73d4-47fd-be47-da486221750e": "19. Таблица: train",
    "5d45870f-274f-4e22-ab3b-a9967b67ab29": "20. Таблица: valid",
    "fd30fbee-aa24-4fbe-908b-2be1f165539b": "21. Таблица: test",
    "ba1494a4-814a-409d-8c42-adc438bdbeab": "22. Таблица: метрики valid",
    "59d627ac-f4ca-43d3-bcc7-4f3fabd720e1": "23. Таблица: метрики test",
    "a6859f02-d21f-48f0-99ed-ba0ebddfdfb3": "24. Статистика train",
    "5e6adeb9-f08c-48c3-b2e0-fc4cc62c5ba6": "25. Таблица: z-scores",
    "6f8e1a8b-7ee8-42e0-8f61-95b63b8200c5": "26. Таблица: LOF scores",
    "29529701-4a69-4799-a0fa-608c50e63727": "27. Статистика valid",
    "313e29f4-b691-4539-b905-00a3a59ccf36": "28. Статистика test",
    "b893b697-a566-42d3-88ff-61b58637190c": "29. Статистика метрик",
}

LAYOUT: dict[str, tuple[int, int]] = {
    "e4796837-1c62-43bd-9ef5-4ef59c13da33": (40, 100),
    "8a85064b-d064-47f3-9341-0c2d4cac30f6": (240, 100),
    "b09518ba-668e-424b-a203-9268c24d2e1d": (240, 260),
    "81b9378b-412a-4c8a-8a8a-0abc4755879d": (440, 100),
    "d3ecf000-f856-4c3c-b2a9-15160bf1969f": (640, 100),
    "e9c4c313-1a66-4bdb-8c87-d6bf5edefd29": (840, 100),
    "e2a95e1d-aa96-4a92-8a0b-3aa28127b4a7": (440, 280),
    "f7a8b9c0-d1e2-4345-a678-901234567abc": (440, 420),
    "e9f6e143-ca72-47ed-aa6a-e3f90790a876": (660, 280),
    "36e30bc4-f1d9-441e-bbc0-855e7c21b6b9": (660, 420),
    "2143c602-da33-479e-a185-8b268d23aa5e": (520, 220),
    "055676ef-d423-4779-8606-9cb01cc26357": (700, 220),
    "014d564c-96da-4238-ae2f-e99b094baffe": (880, 260),
    "928f35a2-cacf-4f40-a824-d9b65e019fdb": (1080, 260),
    "92caeb79-9c23-475e-80f9-285ff33943de": (1280, 260),
    "fbcace4c-70fc-4333-9e4c-e4b7cda3c504": (880, 420),
    "15926c8b-d23c-4f84-900d-5d13402fdfe4": (1080, 420),
    "40adf7a8-c6a5-4a6b-a64c-c1ceacb2dffb": (1280, 420),
    "f3f566b4-73d4-47fd-be47-da486221750e": (40, 560),
    "5d45870f-274f-4e22-ab3b-a9967b67ab29": (280, 560),
    "fd30fbee-aa24-4fbe-908b-2be1f165539b": (520, 560),
    "ba1494a4-814a-409d-8c42-adc438bdbeab": (760, 560),
    "59d627ac-f4ca-43d3-bcc7-4f3fabd720e1": (1000, 560),
    "a6859f02-d21f-48f0-99ed-ba0ebddfdfb3": (1240, 560),
    "5e6adeb9-f08c-48c3-b2e0-fc4cc62c5ba6": (1480, 560),
    "6f8e1a8b-7ee8-42e0-8f61-95b63b8200c5": (40, 700),
    "29529701-4a69-4799-a0fa-608c50e63727": (280, 700),
    "313e29f4-b691-4539-b905-00a3a59ccf36": (520, 700),
    "b893b697-a566-42d3-88ff-61b58637190c": (760, 700),
}


def set_workflow_display_name(text: str, guid: str, name: str) -> tuple[str, bool]:
    """Rename only package-level workflow node (3 tabs + VendorGuid on same line)."""
    pat = (
        rf'(\t\t\t<Item Guid="{re.escape(guid)}" DisplayName=")[^"]*(" VendorGuid=")'
    )
    new, n = re.subn(pat, rf"\g<1>{name}\2", text, count=1)
    return new, n > 0


def set_workflow_position(text: str, guid: str, left: int, top: int) -> tuple[str, bool]:
    """Move only the workflow node's <Position> (first after 3-tab Item with this guid)."""
    pat = (
        rf'(\t\t\t<Item Guid="{re.escape(guid)}"[^>]*>.*?<Position Left=")\d+(" Top=")\d+(")'
    )

    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{left}{m.group(2)}{top}{m.group(3)}"

    new, n = re.subn(pat, repl, text, count=1, flags=re.DOTALL)
    return new, n > 0


def validate_xml(text: str) -> None:
    if text.count("<Items>") != text.count("</Items>"):
        raise ValueError(
            f"Unbalanced <Items>: {text.count('<Items>')} vs {text.count('</Items>')}"
        )
    ET.fromstring(text)


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    unit_xml = WORK / "Unit_1" / "Unit.xml"
    text = unit_xml.read_text(encoding="utf-8-sig")

    renamed = positioned = 0
    for guid, name in RENAME.items():
        text, ok = set_workflow_display_name(text, guid, name)
        if ok:
            renamed += 1
    for guid, (left, top) in LAYOUT.items():
        text, ok = set_workflow_position(text, guid, left, top)
        if ok:
            positioned += 1

    text = re.sub(
        r'(<Item Guid="66288e98-7891-4952-9edb-960b2057a3e6"[^>]*Text=")[^"]*(")',
        r"\1LOF: novelty на ECG.&#10;Z-нормализация по train (CLASS=1).&#10;k=15, c=0.05, Fβ (β=2).&#10;Отдельный скоринг valid и test.\2",
        text,
        count=1,
    )
    text = re.sub(
        r'(<Item Guid="20043013-c106-4193-8dfa-f5f0b1faa536"[^>]*Text=")[^"]*(")',
        r"\1Метки: CLASS 1→0, 2..5→1; outlier_label 1→0, -1→1.\2",
        text,
        count=1,
    )

    validate_xml(text)
    unit_xml.write_text(text, encoding="utf-8")

    bak = LGP.with_suffix(".lgp.bak_before_safe_layout")
    shutil.copy2(LGP, bak)
    try:
        LGP.unlink()
    except OSError as exc:
        raise SystemExit(f"Close Loginom before repack: {exc}") from exc

    with zipfile.ZipFile(LGP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(WORK.rglob("*")):
            if not f.is_file():
                continue
            arc = f.relative_to(WORK).as_posix()
            if arc in SKIP_ROOT_BIN or arc in DROP_UNIT_BIN:
                continue
            zf.write(f, arc)

    numbered = len(re.findall(r'DisplayName="\d+\.', text))
    print(f"Safe layout applied: {LGP}")
    print(f"  Backup: {bak}")
    print(f"  Renamed workflow nodes: {renamed}")
    print(f"  Repositioned: {positioned}")
    print(f"  Numbered titles in file: {numbered}")


if __name__ == "__main__":
    main()
