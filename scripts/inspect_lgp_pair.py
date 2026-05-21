#!/usr/bin/env python3
"""Compare node lists in two .lgp packages (template vs user)."""
import re
import zipfile
from pathlib import Path

from paths import LOF_PACKAGE_LGP, LOF_REFERENCE_LGP

WORK = Path(__file__).parent / "_work"


def extract(lgp: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(lgp) as zf:
        zf.extractall(dest)


def list_nodes(xml: str) -> list[str]:
    return re.findall(r'<Item Guid="[^"]+" DisplayName="([^"]+)"', xml)


def main() -> None:
    items = [
        ("reference", "template_pkg", LOF_REFERENCE_LGP),
        ("user", "user_pkg", LOF_PACKAGE_LGP),
    ]
    for label, folder, lgp in items:
        if not lgp.is_file():
            print(f"skip missing {lgp}")
            continue
        dest = WORK / folder
        extract(lgp, dest)
        print(f"=== {label} ({lgp.name}) ===")
        for unit in ("Unit_0", "Unit_1"):
            xml = (dest / unit / "Unit.xml").read_text(encoding="utf-8")
            print(f"  {unit}:")
            for n in list_nodes(xml):
                print(f"    - {n}")
            refs = re.findall(
                r'DisplayName="([^"]+)"[^>]*GlobalNodeID="([^"]+)"', xml
            )
            for dn, gid in refs:
                print(f"    [public] {dn} -> {gid}")


if __name__ == "__main__":
    main()
