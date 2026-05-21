#!/usr/bin/env python3
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from paths import REGRESSION_REFERENCE_LGP

XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
p = REGRESSION_REFERENCE_LGP
out = Path(__file__).parent / "_package_units.json"
result = {}
with zipfile.ZipFile(p) as z:
    for u in sorted(n for n in z.namelist() if n.endswith("Unit.xml")):
        root = ET.fromstring(z.read(u))
        nodes = []
        for item in root.findall(".//{*}Nodes/{*}Item"):
            dn = item.get("DisplayName", "")
            eng = item.find(".//{*}Engine")
            et = eng.get(XSI + "type") if eng is not None else None
            fn = eng.get("FileName") if eng is not None else None
            if dn:
                nodes.append({"display": dn, "engine": et.split(":")[-1] if et else None, "file": fn})
        info = z.read(u.replace("Unit.xml", "Info.xml")).decode("utf-8")
        import re

        m = re.search(r'Name="([^"]*)"', info)
        result[u] = {"scenario_name": m.group(1) if m else "", "nodes": nodes}
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("written", out)
