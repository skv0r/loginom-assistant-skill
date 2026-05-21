#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path

from paths import LOF_EXPORT_SCRIPT_OUT
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, fbeta_score

FEATURES = [f"VAR{i}" for i in range(2, 142)]
df = pd.read_csv(
    LOF_EXPORT_SCRIPT_OUT,
    sep="\t",
    decimal=",",
)
train = df[(df["SAMPLE"] == "train") & (df["CLASS"] == 1)]


def eval_split(k: int, c: float, sample: str) -> dict:
    sc = df[df["SAMPLE"] == sample]
    scaler = StandardScaler()
    xt = scaler.fit_transform(train[FEATURES])
    xs = scaler.transform(sc[FEATURES])
    model = LocalOutlierFactor(n_neighbors=k, contamination=c, novelty=True, n_jobs=-1)
    model.fit(xt)
    pred = model.predict(xs)
    yt = np.where(sc["CLASS"].values == 1, 0, 1)
    yp = np.where(pred == -1, 1, 0)
    tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
    p, r, f1, _ = precision_recall_fscore_support(
        yt, yp, average="binary", pos_label=1, zero_division=0
    )
    fb = fbeta_score(yt, yp, beta=2, pos_label=1, zero_division=0)
    return dict(k=k, c=c, sample=sample, p=p, r=r, f1=f1, fb=fb, tn=tn, fp=fp, fn=fn, tp=tp)


print("=== YOUR export (Loginom split) ===")
for k, c in [(15, 0.02), (15, 0.05), (20, 0.05)]:
    for s in ("valid", "test"):
        m = eval_split(k, c, s)
        print(
            f"k={k} c={c} {s}: P={m['p']:.2f} R={m['r']:.2f} Fbeta={m['fb']:.2f} "
            f"tp={m['tp']} fn={m['fn']} fp={m['fp']} tn={m['tn']}"
        )

# User screenshot 1: tp=15 fn=142 -> predicted anomalies = 24
print("\nUser screenshot match (tp+fp):", 15 + 9, "of 157 anomalies")
print("Expected flags at c=0.02 (~2%):", int(round(0.02 * 595)))
print("Expected flags at c=0.05 (~5%):", int(round(0.05 * 595)))
