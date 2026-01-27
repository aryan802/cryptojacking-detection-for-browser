import pandas as pd

rt = pd.read_csv("../data/features/runtime_features.csv")
net = pd.read_csv("../data/features/network_features.csv")

df = pd.merge(
    rt, net,
    on=["dataset","site_id","label"],
    how="inner"
)

df.to_csv("../data/features/features_fast.csv", index=False)
print(f"[✓] Final FAST feature table: {df.shape}")
