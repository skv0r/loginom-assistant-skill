#!/usr/bin/env python3
"""Reference LOF metrics (compare with Loginom / offline export)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, fbeta_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

from paths import LOF_DATA


FEATURES = [f"VAR{i}" for i in range(2, 142)]


def prepare() -> pd.DataFrame:
    train = pd.read_csv(LOF_DATA / "ecg_train.txt")
    test = pd.read_csv(LOF_DATA / "ecg_test.txt")
    df = pd.concat([train, test], ignore_index=True)
    df = df[df["CLASS"] != 2].copy()
    df["OBJECT"] = [f"obj{i+1}" for i in range(len(df))]

    norm = df[df["CLASS"] == 1].copy()
    anom = df[df["CLASS"] != 1].copy()
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(norm))
    n_train = int(round(0.7 * len(norm)))
    train_n = norm.iloc[perm[:n_train]].copy()
    rest = pd.concat([norm.iloc[perm[n_train:]], anom], ignore_index=True)
    valid, test_n = train_test_split(
        rest, test_size=0.5, random_state=42, stratify=rest["CLASS"]
    )
    train_n["SAMPLE"] = "train"
    valid["SAMPLE"] = "valid"
    test_n["SAMPLE"] = "test"
    out = pd.concat([train_n, valid, test_n], ignore_index=True)
    out["IsTestSet"] = out["SAMPLE"] != "train"
    return out


def y_true_binary(series: pd.Series) -> np.ndarray:
    return np.where(series == 1, 0, 1).astype(int)


def y_pred_binary(lof_pred: np.ndarray) -> np.ndarray:
    return np.where(lof_pred == -1, 1, 0).astype(int)


def eval_split(df: pd.DataFrame, k: int, c: float, sample: str) -> dict:
    train = df[df["SAMPLE"] == "train"]
    scoring = df[df["SAMPLE"] == sample]

    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[FEATURES])
    x_score = scaler.transform(scoring[FEATURES])

    model = LocalOutlierFactor(
        n_neighbors=k, contamination=c, novelty=True, n_jobs=-1
    )
    model.fit(x_train)
    pred = model.predict(x_score)

    yt = y_true_binary(scoring["CLASS"])
    yp = y_pred_binary(pred)
    p, r, f1, _ = precision_recall_fscore_support(
        yt, yp, average="binary", pos_label=1, zero_division=0
    )
    fb = fbeta_score(yt, yp, beta=2, pos_label=1, zero_division=0)
    return {"k": k, "c": c, "sample": sample, "precision": p, "recall": r, "f1": f1, "fbeta": fb}


def main() -> None:
    df = prepare()
    print(f"Rows: {len(df)}, train: {(df.SAMPLE=='train').sum()}, valid: {(df.SAMPLE=='valid').sum()}, test: {(df.SAMPLE=='test').sum()}")

    grid = [(15, 0.02), (15, 0.05), (20, 0.02), (20, 0.05), (25, 0.02), (25, 0.05)]
    print("\nValidation Fbeta (beta=2):")
    best_k, best_c, best_fb = 15, 0.05, -1.0
    for k, c in grid:
        m = eval_split(df, k, c, "valid")
        print(f"  k={k} c={c}: Fbeta={m['fbeta']:.2f} F1={m['f1']:.2f}")
        if m["fbeta"] > best_fb or (m["fbeta"] == best_fb and k < best_k):
            best_fb, best_k, best_c = m["fbeta"], k, c

    print(f"\nBest on valid: k={best_k} c={best_c} Fbeta={best_fb:.2f}")

    test_m = eval_split(df, best_k, best_c, "test")
    print("\nTest metrics (chosen model):")
    scoring = df[df.SAMPLE == "test"]
    train = df[df.SAMPLE == "train"]
    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[FEATURES])
    x_test = scaler.transform(scoring[FEATURES])
    model = LocalOutlierFactor(
        n_neighbors=best_k,
        contamination=best_c,
        novelty=True,
        n_jobs=-1,
    )
    model.fit(x_train)
    pred = model.predict(x_test)
    yt = y_true_binary(scoring["CLASS"])
    yp = y_pred_binary(pred)
    print(classification_report(yt, yp, target_names=["normal", "anomaly"], digits=2))
    print(
        f"Precision={test_m['precision']:.2f} Recall={test_m['recall']:.2f} "
        f"F1={test_m['f1']:.2f} Fbeta={test_m['fbeta']:.2f}"
    )


if __name__ == "__main__":
    main()
