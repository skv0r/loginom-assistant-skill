#!/usr/bin/env python3
"""Extract node summaries from Loginom .lgp packages (ZIP + XML)."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

XSI = "{http://www.w3.org/2001/XMLSchema-instance}"


def summarize_lgp(path: Path) -> dict:
    try:
        rel = path.relative_to(Path(__file__).resolve().parents[4])
        path_str = rel.as_posix()
    except ValueError:
        path_str = path.name
    result: dict = {"path": path_str, "units": []}
    with zipfile.ZipFile(path) as zf:
        pinfo = zf.read("PackageInfo.xml").decode("utf-8")
        match = re.search(r'ApplicationVersion="([^"]+)"', pinfo)
        if match:
            result["version"] = match.group(1)
        match = re.search(r'Name="([^"]+)"', pinfo)
        if match:
            result["name"] = match.group(1)

        for name in sorted(zf.namelist()):
            if not name.endswith("Unit.xml"):
                continue
            root = ET.fromstring(zf.read(name))
            nodes = []
            for item in root.findall(".//{*}Nodes/{*}Item"):
                eng = item.find(".//{*}Engine")
                et = eng.get(XSI + "type") if eng is not None else None
                nodes.append(
                    {
                        "display": item.get("DisplayName", ""),
                        "engine": et.split(":")[-1] if et else None,
                    }
                )
            result["units"].append({"unit": name, "nodes": nodes})
    return result


def main() -> int:
    from paths import (
        ABC_TEMPLATE_LGP,
        ASSOCIATION_REFERENCE_LGP,
        CLUSTERING_REFERENCE_LGP,
        ETL_REFERENCE_LGP,
        FEATURES_REFERENCE_LGP,
        REGRESSION_REFERENCE_LGP,
        SCORING_REFERENCE_LGP,
    )

    files = {
        "etl": ETL_REFERENCE_LGP,
        "association": ASSOCIATION_REFERENCE_LGP,
        "features": FEATURES_REFERENCE_LGP,
        "clustering": CLUSTERING_REFERENCE_LGP,
        "abc": ABC_TEMPLATE_LGP,
        "regression": REGRESSION_REFERENCE_LGP,
        "scoring": SCORING_REFERENCE_LGP,
    }
    out = Path(__file__).parent / "_node_maps.json"
    maps = {k: summarize_lgp(v) for k, v in files.items() if v.exists()}
    out.write_text(json.dumps(maps, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in maps.items():
        total = sum(len(u["nodes"]) for u in v["units"])
        print(f"{k}: v{v.get('version')} units={len(v['units'])} nodes={total}")
    print(f"written {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
