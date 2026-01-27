import json

with open("../data/processed/wasm_indicator.json") as f:
    wasm = {x["site_id"]: x["wasm_present"] for x in json.load(f)}

with open("../data/processed/runtime_indicator.json") as f:
    runtime = {x["site_id"]: x["suspicious_runtime"] for x in json.load(f)}

candidates = []

for site in wasm:
    if wasm.get(site) or runtime.get(site):
        candidates.append(site)

with open("../data/processed/crypto_candidates.txt", "w") as f:
    for c in candidates:
        f.write(c + "\n")

print(f"[✓] Selected {len(candidates)} cryptojacking candidates")
