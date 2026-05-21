#!/usr/bin/env python3
"""Find split logic matching reference export.txt SAMPLE labels."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from paths import LOF_DATA, LOF_EXPORT_REFERENCE

REF = LOF_EXPORT_REFERENCE


def load_ref() -> pd.DataFrame:
    ref = pd.read_csv(REF, sep="\t", decimal=",", low_memory=False)
    cols = ["CLASS", "SAMPLE", "IsTestSet", "OBJECT"] + [f"VAR{i}" for i in range(2, 142)]
    return ref[cols].sort_values("OBJECT").reset_index(drop=True)


def base_df() -> pd.DataFrame:
    train = pd.read_csv(LOF_DATA / "ecg_train.txt")
    test = pd.read_csv(LOF_DATA / "ecg_test.txt")
    df = pd.concat([train, test], ignore_index=True)
    df = df[df["CLASS"] != 2].copy()
    df["OBJECT"] = [f"obj{i + 1}" for i in range(len(df))]
    return df


def match(name: str, df: pd.DataFrame, sample: pd.Series, ref: pd.DataFrame) -> float:
    pred = pd.Series(sample.values, index=df["OBJECT"])
    ref_map = ref.set_index("OBJECT")["SAMPLE"]
    acc = (pred == ref_map.reindex(pred.index)).mean()
    print(f"{name}: {acc:.4f} ({int(acc * len(df))}/3233)")
    return acc


def main() -> None:
    ref = load_ref()
    df = base_df()
    rng = np.random.RandomState(42)
    norm = df[df["CLASS"] == 1].copy()
    anom = df[df["CLASS"] != 1].copy()

    # A: current build script
    perm = rng.permutation(len(norm))
    n_train = int(round(0.7 * len(norm)))
    train_n = norm.iloc[perm[:n_train]]
    rest = pd.concat([norm.iloc[perm[n_train:]], anom], ignore_index=True)
    valid, test = train_test_split(rest, test_size=0.5, random_state=42, stratify=rest["CLASS"])
    s = pd.Series("train", index=df.index)
    s.loc[valid.index] = "valid"
    s.loc[test.index] = "test"
    match("A perm+stratify rest", df, s, ref)

    # E: train_test_split 70% on norm
    train_n, rest_n = train_test_split(norm, train_size=0.7, random_state=42)
    rest = pd.concat([rest_n, anom], ignore_index=True)
    valid, test = train_test_split(rest, test_size=0.5, random_state=42, stratify=rest["CLASS"])
    s = pd.Series("train", index=df.index)
    s.loc[train_n.index] = "train"
    s.loc[valid.index] = "valid"
    s.loc[test.index] = "test"
    match("E tts norm 70%", df, s, ref)

    # B: 70/30 all rows
    rng = np.random.RandomState(42)
    perm_all = rng.permutation(len(df))
    n70 = int(round(0.7 * len(df)))
    train70 = df.iloc[perm_all[:n70]]
    rest30 = df.iloc[perm_all[n70:]]
    valid, test = train_test_split(rest30, test_size=0.5, random_state=42, stratify=rest30["CLASS"])
    s = pd.Series(index=df.index, dtype=object)
    s.loc[train70.index] = "train"
    s.loc[valid.index] = "valid"
    s.loc[test.index] = "test"
    match("B 70/30 all", df, s, ref)

    # G: Loginom partition 70 train / 30 test on norm, then 50/50 on 30 branch
    # Simulate: first split norm 70/30 with seed 42 (train_test_split)
    train_n, branch30 = train_test_split(norm, test_size=0.3, random_state=42)
    valid_n, test_n = train_test_split(branch30, test_size=0.5, random_state=42)
    # anomalies: all go to valid+test 50/50 stratified
    anom_v, anom_t = train_test_split(anom, test_size=0.5, random_state=42, stratify=anom["CLASS"])
    s = pd.Series("train", index=df.index)
    s.loc[train_n.index] = "train"
    s.loc[valid_n.index] = "valid"
    s.loc[test_n.index] = "test"
    s.loc[anom_v.index] = "valid"
    s.loc[anom_t.index] = "test"
    match("G norm 70/30 then 50/50 + anom split", df, s, ref)

    # H: same but branch30 split without stratify
    train_n, branch30 = train_test_split(norm, test_size=0.3, random_state=42)
    valid_n, test_n = train_test_split(branch30, test_size=0.5, random_state=42)
    anom_v, anom_t = train_test_split(anom, test_size=0.5, random_state=42, stratify=anom["CLASS"])
    s = pd.Series("train", index=df.index)
    s.loc[train_n.index] = "train"
    s.loc[valid_n.index] = "valid"
    s.loc[test_n.index] = "test"
    s.loc[anom_v.index] = "valid"
    s.loc[anom_t.index] = "test"
    match("H norm 70/30 50/50 no strat + anom", df, s, ref)

    # I: full 3233 row order split 70 then 50/50 on remainder (class 2 removed)
    rng = np.random.RandomState(42)
    perm = rng.permutation(len(df))
    n70 = int(round(0.7 * len(df)))
    train_idx = perm[:n70]
    rest_idx = perm[n70:]
    rest_df = df.iloc[rest_idx]
    valid, test = train_test_split(rest_df, test_size=0.5, random_state=42, stratify=rest_df["CLASS"])
    s = pd.Series(index=df.index, dtype=object)
    s.iloc[train_idx] = "train"
    s.loc[valid.index] = "valid"
    s.loc[test.index] = "test"
    match("I 70/30 all rows perm", df, s, ref)

    # check train only class1 in ref
    print("\nref train CLASS counts:\n", ref[ref.SAMPLE == "train"].CLASS.value_counts())
    print("ref non-train with CLASS=1:", ((ref.SAMPLE != "train") & (ref.CLASS == 1)).sum())


if __name__ == "__main__":
    main()
