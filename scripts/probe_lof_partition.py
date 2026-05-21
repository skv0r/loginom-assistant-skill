#!/usr/bin/env python3
"""Probe which split logic matches sample_by_object.tsv."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from paths import LOF_DATA



def load_df() -> pd.DataFrame:
    train = pd.read_csv(LOF_DATA / "ecg_train.txt")
    test = pd.read_csv(LOF_DATA / "ecg_test.txt")
    train = train[train["CLASS"] != 2].copy()
    test = test[test["CLASS"] != 2].copy()
    df = pd.concat([train, test], ignore_index=True)
    df["OBJECT"] = [f"obj{i + 1}" for i in range(len(df))]
    return df


def accuracy(df: pd.DataFrame, sample: pd.Series) -> float:
    ref = pd.read_csv(LOF_DATA / "sample_by_object.tsv", sep="\t").set_index("OBJECT")["SAMPLE"]
    pred = pd.Series(sample.values, index=df["OBJECT"].values)
    return float((pred.values == ref.loc[df["OBJECT"]].values).mean())


def methodology_split(df: pd.DataFrame, *, random_normals: bool) -> pd.Series:
    norm = df[df["CLASS"] == 1]
    anom = df[df["CLASS"] != 1]
    n = len(norm)
    n_train = int(round(0.7 * n))
    if random_normals:
        perm = np.random.RandomState(42).permutation(n)
        train_idx = norm.index[perm[:n_train]]
        rest_norm_idx = norm.index[perm[n_train:]]
    else:
        train_idx = norm.index[:n_train]
        rest_norm_idx = norm.index[n_train:]
    pool = df.loc[rest_norm_idx.union(anom.index)]
    valid, test = train_test_split(
        pool, test_size=0.5, random_state=42, stratify=pool["CLASS"]
    )
    out = pd.Series(index=df.index, dtype=object)
    out.loc[train_idx] = "train"
    out.loc[valid.index] = "valid"
    out.loc[test.index] = "test"
    return out


def full_partition(df: pd.DataFrame, teach_pct: int, *, method: str) -> tuple[pd.Index, pd.Index]:
    n = len(df)
    n_teach = int(round(teach_pct / 100 * n))
    idx = np.arange(n)
    if method == "sequence":
        teach = df.index[:n_teach]
        test = df.index[n_teach:]
    else:
        perm = np.random.RandomState(42).permutation(n)
        teach = df.index[perm[:n_teach]]
        test = df.index[perm[n_teach:]]
    return teach, test


def main() -> None:
    df = load_df()
    ref = pd.read_csv(LOF_DATA / "sample_by_object.tsv", sep="\t")
    print(f"rows={len(df)} train={(ref.SAMPLE=='train').sum()} valid={(ref.SAMPLE=='valid').sum()}")

    for name, sample in [
        ("rand70+strat50", methodology_split(df, random_normals=True)),
        ("seq70+strat50", methodology_split(df, random_normals=False)),
    ]:
        print(name, accuracy(df, sample))

    # Classmate-style: 70/30 on full data, then labels on branches
    teach, rest = full_partition(df, 70, method="random")
    sample = pd.Series(index=df.index, dtype=object)
    sample.loc[teach] = "train"
    valid, test = train_test_split(
        df.loc[rest], test_size=0.5, random_state=42, stratify=df.loc[rest, "CLASS"]
    )
    sample.loc[valid.index] = "valid"
    sample.loc[test.index] = "test"
    print("full_rand70+strat50", accuracy(df, sample))

    teach, rest = full_partition(df, 70, method="sequence")
    sample = pd.Series(index=df.index, dtype=object)
    sample.loc[teach] = "train"
    valid, test = train_test_split(
        df.loc[rest], test_size=0.5, random_state=42, stratify=df.loc[rest, "CLASS"]
    )
    sample.loc[valid.index] = "valid"
    sample.loc[test.index] = "test"
    print("full_seq70+strat50", accuracy(df, sample))


if __name__ == "__main__":
    main()
