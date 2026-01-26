import os
import json
import requests
from urllib.parse import urlparse

RAW_DATA_DIR = "../data/raw"

def extract_urls_from_logs(log_file):
    with open(log_file, "r") as f:
        logs = json.load(f)

    js_urls = set()
    wasm_urls = set()

    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]
            if message["method"] == "Network.responseReceived":
                url = message["params"]["response"]["url"]
                if url.endswith(".js"):
                    js_urls.add(url)
                elif url.endswith(".wasm"):
                    wasm_urls.add(url)
        except Exception:
            continue

    return list(js_urls), list(wasm_urls)

def download_files(urls, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for url in urls:
        try:
            filename = os.path.basename(urlparse(url).path)
            filepath = os.path.join(output_dir, filename)

            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(r.content)
                print(f"[✓] Saved {filename}")
        except Exception:
            pass

if __name__ == "__main__":
    for site in os.listdir(RAW_DATA_DIR):
        site_path = os.path.join(RAW_DATA_DIR, site)
        log_file = os.path.join(site_path, "network_logs.json")

        if not os.path.exists(log_file):
            continue

        print(f"\n[+] Processing {site}")
        js_urls, wasm_urls = extract_urls_from_logs(log_file)

        download_files(js_urls, os.path.join(site_path, "js"))
        download_files(wasm_urls, os.path.join(site_path, "wasm"))
