#!/usr/bin/env python3
"""Set model.fitter filepath to C:\\model in LOF package."""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

from paths import LOF_PACKAGE_LGP, WORK_LOF_FIX_MODEL

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_FIX_MODEL
MODEL_DIR = Path(r"C:\model")

SKIP_ROOT_BIN = {"PackageIndex.bin", "PackageInfo.bin"}
DROP_UNIT_BIN = {
    "Unit_0/Unit.bin",
    "Unit_0/Info.bin",
    "Unit_1/Unit.bin",
    "Unit_1/Info.bin",
}

# XML attribute value (forward slashes are ok on Windows in Loginom)
NEW_PATH = r"C:\model"

FILEPATH_VALUE_RE = re.compile(
    r'(<Item __derived="true" __baseName="filepath">\s*'
    r'<DefaultValue[^>]*Value=")[^"]+(")',
    re.MULTILINE,
)


def patch_filepath_xml(text: str) -> tuple[str, int]:
    def _repl(m: re.Match[str]) -> str:
        return f'{m.group(1)}{NEW_PATH}{m.group(2)}'

    new_text, n = FILEPATH_VALUE_RE.subn(_repl, text)
    new_text, n2 = re.subn(
        r'(<Item[^>]*Name="filepath"[^>]*>[\s\S]*?<Value>)[^<]+(</Value>)',
        lambda m: f"{m.group(1)}{NEW_PATH}{m.group(2)}",
        new_text,
    )
    return new_text, n + n2


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    with zipfile.ZipFile(LGP) as zf:
        zf.extractall(WORK)

    unit1 = WORK / "Unit_1" / "Unit.xml"
    text = unit1.read_text(encoding="utf-8")
    text, n = patch_filepath_xml(text)
    if n == 0:
        raise RuntimeError("No filepath entries updated in Unit_1/Unit.xml")
    unit1.write_text(text, encoding="utf-8")

    vars_xml = WORK / "Variables.xml"
    if vars_xml.is_file():
        vtext = vars_xml.read_text(encoding="utf-8")
        vtext, vn = patch_filepath_xml(vtext)
        if vn:
            vars_xml.write_text(vtext, encoding="utf-8")

    bak = LGP.with_suffix(".lgp.bak_path")
    if LGP.exists():
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

    print(f"Updated {n} filepath value(s) -> {NEW_PATH}")
    print(f"Patched {LGP}")
    print(f"Created {MODEL_DIR}")


if __name__ == "__main__":
    main()
