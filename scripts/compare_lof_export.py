#!/usr/bin/env python3
"""Compare two Loginom TSV exports (reference vs generated)."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

EXPORT_COLS = (
    ["CLASS", "SAMPLE", "IsTestSet", "OBJECT"]
    + [f"VAR{i}" for i in range(2, 142)]
)


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", decimal=",", low_memory=False)
    if list(df.columns) != EXPORT_COLS:
        # reorder if same set
        missing = set(EXPORT_COLS) - set(df.columns)
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        df = df[EXPORT_COLS]
    return df.sort_values("OBJECT").reset_index(drop=True)


def compare(reference: Path, candidate: Path, atol: float = 1e-9) -> bool:
    ref = load(reference)
    cand = load(candidate)
    ok = True

    if len(ref) != len(cand):
        print(f"FAIL rows: ref={len(ref)} cand={len(cand)}")
        ok = False

    for col in ("CLASS", "SAMPLE", "IsTestSet", "OBJECT"):
        mism = (ref[col].astype(str) != cand[col].astype(str)).sum()
        if mism:
            print(f"FAIL {col}: {mism} mismatches")
            ok = False
        else:
            print(f"OK {col}")

    num = [f"VAR{i}" for i in range(2, 142)]
    diff = np.abs(ref[num].astype(float) - cand[num].astype(float))
    max_diff = diff.max().max()
    if max_diff > atol:
        print(f"FAIL numeric max diff: {max_diff}")
        ok = False
    else:
        print(f"OK numeric (max diff {max_diff})")

    if ok:
        print("MATCH: exports are identical")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if compare(args.reference, args.candidate) else 1)


if __name__ == "__main__":
    main()
