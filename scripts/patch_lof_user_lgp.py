#!/usr/bin/env python3
"""Patch saved LOF package: fix Python row order (train before test)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_lof_project import PYTHON_SPLIT_CODE, pack, xml_escape_code
from loginom_pack import unpack_lgp

from paths import LOF_PACKAGE_LGP, WORK_LOF_USER_PATCH

LGP = LOF_PACKAGE_LGP
WORK = WORK_LOF_USER_PATCH
PYTHON_NODE = "a8f3c2e1-4b5d-6a7c-8d9e-0f1a2b3c4d5e"


def patch_unit0(unit_xml: str) -> str:
    code_xml = xml_escape_code(PYTHON_SPLIT_CODE)
    pattern = (
        rf'(<Item Guid="{PYTHON_NODE}"[^>]*>.*?'
        rf'<Engine xsi:type="TBGPythonEngine" Code=")[^"]*(" CodeConfigurableColumns)'
    )
    def _repl(m: re.Match[str]) -> str:
        return m.group(1) + code_xml + m.group(2)

    new_text, n = re.subn(pattern, _repl, unit_xml, count=1, flags=re.DOTALL)
    if n != 1:
        raise RuntimeError(f"Python node replace failed (n={n})")
    return new_text


def main() -> None:
    unpack_lgp(LGP, WORK)
    u0 = WORK / "Unit_0" / "Unit.xml"
    u0.write_text(patch_unit0(u0.read_text(encoding="utf-8")), encoding="utf-8")
    pack(WORK, LGP)
    print(f"Patched {LGP}")


if __name__ == "__main__":
    main()
