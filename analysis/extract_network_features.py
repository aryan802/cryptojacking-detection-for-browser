import os, json, csv
from collections import Counter
from urllib.parse import urlparse

LABELS = "../data/metadata/labels.csv"
OUT = "../data/features/network_features.csv"

rows = []

with open(LABELS) as f:
    next(f)
    for line in f:
        dataset, site_id, label = line.strip().split(",")
        base = f"../data/raw/{dataset}/{site_id}"
        fpath = os.path.join(base, "network_logs.json")
        if not os.path.exists(fpath):
            continue

        with open(fpath) as nf:
            logs = json.load(nf)

        urls = []
        for e in logs:
            try:
                msg = json.loads(e["message"])["message"]
                if msg.get("method") == "Network.requestWillBeSent":
                    u = msg["params"]["request"]["url"]
                    urls.append(u)
            except:
                pass

        hosts = [urlparse(u).hostname for u in urls if urlparse(u).hostname]
        wasm = [u for u in urls if ".wasm" in u.lower()]
        scripts = [u for u in urls if u.lower().endswith(".js")]

        rows.append([
            dataset, site_id, label,
            len(urls),
            len(scripts),
            len(wasm),
            len(set(hosts))
        ])

os.makedirs("../data/features", exist_ok=True)

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "dataset","site_id","label",
        "total_requests","script_requests",
        "wasm_requests","unique_hosts"
    ])
    w.writerows(rows)

print(f"[✓] Network features written: {len(rows)} samples")
