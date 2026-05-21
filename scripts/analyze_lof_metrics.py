#!/usr/bin/env python3
"""Compare user Loginom metrics vs teacher targets and sklearn reference."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, fbeta_score, precision_recall_fscore_support
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

from paths import (
    LOF_DATA,
    LOF_EXPORT_OUT,
    LOF_EXPORT_REFERENCE,
    LOF_EXPORT_SCRIPT_OUT,
)

FEATURES = [f"VAR{i}" for i in range(2, 142)]


def load_export() -> pd.DataFrame:
    for p in (LOF_EXPORT_SCRIPT_OUT, LOF_EXPORT_OUT, LOF_EXPORT_REFERENCE):
        if p.is_file():
            df = pd.read_csv(p, sep="\t", decimal=",")
            if "VAR2" not in df.columns and len(df.columns) > 5:
                df = pd.read_csv(p, sep="\t")
            return df
    raise FileNotFoundError(f"No export file in {LOF_DATA}")


def eval_split(df: pd.DataFrame, sample: str, k: int = 15, c: float = 0.05) -> dict:
    train = df[(df["SAMPLE"] == "train") & (df["CLASS"] == 1)]
    scoring = df[df["SAMPLE"] == sample]
    scaler = StandardScaler()
    xt = scaler.fit_transform(train[FEATURES])
    xs = scaler.transform(scoring[FEATURES])
    model = LocalOutlierFactor(n_neighbors=k, contamination=c, novelty=True, n_jobs=-1)
    model.fit(xt)
    pred = model.predict(xs)
    yt = np.where(scoring["CLASS"].values == 1, 0, 1)
    yp = np.where(pred == -1, 1, 0)
    tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
    p, r, f1, _ = precision_recall_fscore_support(
        yt, yp, average="binary", pos_label=1, zero_division=0
    )
    fb = fbeta_score(yt, yp, beta=2, pos_label=1, zero_division=0)
    return {
        "n": len(scoring),
        "precision": p,
        "recall": r,
        "f1": f1,
        "fbeta": fb,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }


def main() -> None:
    df = load_export()
    teacher = {"valid": {"fn": 5}, "test": {"fn": 2}}
    user_loginom = {
        "valid": {"fn": 11, "recall": 0.93, "n": 2638},
        "test": {"fn": 4, "recall": 0.97, "n": 2638},
    }

    print("=== sklearn reference (same export, k=15 c=0.05) ===")
    for s in ("valid", "test"):
        m = eval_split(df, s)
        print(
            f"{s}: n={m['n']} fn={m['fn']} recall={m['recall']:.2f} "
            f"precision={m['precision']:.2f} fbeta={m['fbeta']:.2f}"
        )

    print("\n=== teacher vs your Loginom screenshot ===")
    for s in ("valid", "test"):
        ref = eval_split(df, s)
        print(f"\n{s}:")
        print(f"  teacher fn ~ {teacher[s]['fn']}")
        print(f"  your Loginom fn={user_loginom[s]['fn']} (n={user_loginom[s]['n']} rows in table)")
        print(f"  sklearn on export fn={ref['fn']} (n={ref['n']} rows)")
        if user_loginom[s]["n"] != ref["n"]:
            print(
                f"  NOTE: metrics table has {user_loginom[s]['n']} rows, "
                f"expected {ref['n']} for SAMPLE={s} only"
            )


if __name__ == "__main__":
    main()
