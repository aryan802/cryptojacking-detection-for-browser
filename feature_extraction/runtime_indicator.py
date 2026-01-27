import os
import json

RAW_DIR = "../data/raw"

def load_metrics(site_dir):
    path = os.path.join(site_dir, "runtime_metrics.json")
    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f)

def heap_growth(metrics):
    values = [
        m["metrics"].get("JSHeapUsedSize", 0)
        for m in metrics
        if "JSHeapUsedSize" in m["metrics"]
    ]
    if len(values) < 2:
        return 0
    return values[-1] - values[0]

def high_cpu(metrics):
    values = [
        m["metrics"].get("TaskDuration", 0)
        for m in metrics
    ]
    return sum(values)

if __name__ == "__main__":
    results = []

    for site in os.listdir(RAW_DIR):
        site_dir = os.path.join(RAW_DIR, site)
        metrics = load_metrics(site_dir)

        if metrics is None:
            continue

        heap_delta = heap_growth(metrics)
        cpu_load = high_cpu(metrics)

        suspicious = (heap_delta > 2_000_000) or (cpu_load > 1.0)

        results.append({
            "site_id": site,
            "heap_growth": heap_delta,
            "cpu_load": cpu_load,
            "suspicious_runtime": suspicious
        })

    with open("../data/processed/runtime_indicator.json", "w") as f:
        json.dump(results, f, indent=2)

    print("[✓] Runtime indicator extraction complete")
