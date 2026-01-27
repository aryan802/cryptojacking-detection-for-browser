import os
import csv

OUT = "../data/metadata/labels.csv"

def list_sites(base):
    sites = []
    if not os.path.exists(base):
        return sites
    for name in sorted(os.listdir(base)):
        p = os.path.join(base, name)
        if not os.path.isdir(p):
            continue
        # consider usable if runtime + network logs exist
        if (os.path.exists(os.path.join(p, "runtime_metrics.json")) and
            os.path.exists(os.path.join(p, "network_logs.json"))):
            sites.append(name)
    return sites

crypto_sites = list_sites("../data/raw/crypto")
benign_sites = list_sites("../data/raw/benign")

os.makedirs("data/metadata", exist_ok=True)

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["dataset", "site_id", "label"])
    for s in crypto_sites:
        w.writerow(["crypto", s, "cryptojacking"])
    for s in benign_sites:
        w.writerow(["benign", s, "benign"])

print(f"[✓] labels.csv written")
print(f"Crypto sites: {len(crypto_sites)}")
print(f"Benign sites: {len(benign_sites)}")
