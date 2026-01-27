import os
import json

RAW_DIR = "../data/raw"
OUTPUT_PATH = "../data/processed/wasm_indicator.json"

def wasm_present(site_dir):
    wasm_path = os.path.join(site_dir, "wasm")
    return os.path.exists(wasm_path) and len(os.listdir(wasm_path)) > 0

if __name__ == "__main__":
    results = []

    for site in os.listdir(RAW_DIR):
        site_dir = os.path.join(RAW_DIR, site)

        if not os.path.isdir(site_dir):
            continue

        results.append({
            "site_id": site,
            "wasm_present": wasm_present(site_dir)
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print("[✓] WASM indicator extraction complete")

