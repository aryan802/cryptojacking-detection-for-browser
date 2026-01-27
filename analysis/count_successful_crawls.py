import os

RAW_DIR = "../data/raw/crypto" # crypto or benign

success = 0
dead = 0

for site in os.listdir(RAW_DIR):
    site_dir = os.path.join(RAW_DIR, site)

    if not os.path.isdir(site_dir):
        continue

    net = os.path.join(site_dir, "network_logs.json")
    run = os.path.join(site_dir, "runtime_metrics.json")

    if os.path.exists(net) and os.path.exists(run):
        success += 1
    else:
        dead += 1

print(f"Successful crawls: {success}")
print(f"Dead/failed domains: {dead}")
print(f"Total attempted: {success + dead}")
