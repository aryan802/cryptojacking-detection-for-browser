import numpy as np
import pandas as pd

df = pd.read_csv("../data/features/features_fast.csv")

df = df.drop(columns=["dataset", "site_id"])
df["label"] = df["label"].map({"benign":0,"cryptojacking":1})

features = df.drop("label", axis=1)

print("Minimum values per feature:\n")
print(features.min())