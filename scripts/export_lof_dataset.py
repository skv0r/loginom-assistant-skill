#!/usr/bin/env python3
"""Export LOF dataset in Loginom tab format (matches export_reference)."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from paths import LOF_DATA, LOF_EXPORT_OUT, LOF_EXPORT_REFERENCE, LOF_SAMPLE_MAP

DEFAULT_REF = LOF_EXPORT_REFERENCE
DEFAULT_OUT = LOF_EXPORT_OUT
MAP = LOF_SAMPLE_MAP

EXPORT_COLS = (
    ["CLASS", "SAMPLE", "IsTestSet", "OBJECT"]
    + [f"VAR{i}" for i in range(2, 142)]
)


def build_base() -> pd.DataFrame:
    train = pd.read_csv(LOF_DATA / "ecg_train.txt")
    test = pd.read_csv(LOF_DATA / "ecg_test.txt")
    train = train[train["CLASS"] != 2].copy()
    test = test[test["CLASS"] != 2].copy()
    train["IsTestSet"] = False
    test["IsTestSet"] = True
    df = pd.concat([train, test], ignore_index=True)
    df["OBJECT"] = [f"obj{i + 1}" for i in range(len(df))]
    labels = pd.read_csv(MAP, sep="\t")
    df = df.drop(columns=["SAMPLE", "IsTestSet"], errors="ignore").merge(
        labels, on="OBJECT", how="left"
    )
    return df


def to_loginom_tsv(df: pd.DataFrame, path: Path) -> None:
    out = df[EXPORT_COLS].copy()
    out["IsTestSet"] = out["IsTestSet"].map({True: "True", False: "False"})
    out.to_csv(path, sep="\t", index=False, decimal=",")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REF)
    args = parser.parse_args()

    if not MAP.is_file():
        raise FileNotFoundError(f"Missing {MAP}; run extract from reference export first")

    df = build_base()
    to_loginom_tsv(df, args.output)
    print(f"Wrote {len(df)} rows -> {args.output}")

    if args.reference.is_file():
        import compare_lof_export

        raise SystemExit(
            0 if compare_lof_export.compare(args.reference, args.output) else 1
        )


if __name__ == "__main__":
    main()
