import os, json
import numpy as np
import csv

LABELS = "../data/metadata/labels.csv"
OUT = "../data/features/runtime_features.csv"

def load_metrics(path):
    with open(path) as f:
        return json.load(f)

rows = []

with open(LABELS) as f:
    next(f)
    for line in f:
        dataset, site_id, label = line.strip().split(",")
        base = f"../data/raw/{dataset}/{site_id}"
        fpath = os.path.join(base, "runtime_metrics.json")
        if not os.path.exists(fpath):
            continue

        data = load_metrics(fpath)
        task = [x["metrics"].get("TaskDuration", 0) for x in data]
        heap = [x["metrics"].get("JSHeapUsedSize", 0) for x in data]

        rows.append([
            dataset, site_id, label,
            np.mean(task), np.std(task),
            heap[-1] - heap[0] if heap else 0,
            np.mean(heap), np.std(heap)
        ])

os.makedirs("../data/features", exist_ok=True)

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "dataset","site_id","label",
        "task_mean","task_std",
        "heap_delta","heap_mean","heap_std"
    ])
    w.writerows(rows)

print(f"[✓] Runtime features written: {len(rows)} samples")
