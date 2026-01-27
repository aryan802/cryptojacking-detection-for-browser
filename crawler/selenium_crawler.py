import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# -----------------------------
# Configuration
# -----------------------------
DATASET_TYPE = "crypto"  # or "benign"
OUTPUT_DIR = f"../data/raw/{DATASET_TYPE}"
CRAWL_MODE = "FAST"   # FAST or DEEP

if CRAWL_MODE == "FAST":
    WAIT_TIME = 5
    METRIC_DURATION = 10
elif CRAWL_MODE == "DEEP":
    WAIT_TIME = 15
    METRIC_DURATION = 30

METRIC_INTERVAL = 1

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Chrome options (reused)
# -----------------------------
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Disable images & video (speed)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.video": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Enable performance logging
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    return chrome_options

# -----------------------------
# Utility: load URLs
# -----------------------------
def load_urls_from_file(filepath):
    with open(filepath, "r") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]
def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url

# -----------------------------
# Runtime metrics collector
# -----------------------------
def collect_runtime_metrics(driver, duration, interval):
    metrics = []

    driver.execute_cdp_cmd("Performance.enable", {})

    for t in range(0, duration, interval):
        data = driver.execute_cdp_cmd("Performance.getMetrics", {})
        metrics.append({
            "timestamp": t,
            "metrics": {m["name"]: m["value"] for m in data.get("metrics", [])}
        })
        time.sleep(interval)

    return metrics

# -----------------------------
# Main crawler function
# -----------------------------
def crawl_site(url, site_id):
    print(f"[+] Crawling: {url}")
    site_id = site_id + 299   # temp arangement ****** ******
    site_dir = os.path.join(OUTPUT_DIR, f"site_{site_id}")
    os.makedirs(site_dir, exist_ok=True)

    # ✅ Fresh browser instance per site (NO CACHE)
    driver = webdriver.Chrome(options=get_chrome_options())

    try:
        try:
            driver.get(normalize_url(url))
            time.sleep(WAIT_TIME)
        except Exception as e:
            print(f"[!] Failed to load {url}: {e}")
            driver.quit()
            return


        # Save HTML only in DEEP mode
        if CRAWL_MODE == "DEEP":
            with open(os.path.join(site_dir, "page.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)

        # Save network logs
        logs = driver.get_log("performance")
        with open(os.path.join(site_dir, "network_logs.json"), "w") as f:
            json.dump(logs, f, indent=2)

        # Collect runtime metrics
        runtime_metrics = collect_runtime_metrics(
            driver,
            duration=METRIC_DURATION,
            interval=METRIC_INTERVAL
        )

        with open(os.path.join(site_dir, "runtime_metrics.json"), "w") as f:
            json.dump(runtime_metrics, f, indent=2)

        print(f"[✓] Saved data for {url}")

    finally:
        driver.quit()   # 🔒 ensure cleanup even if site fails

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    benign_urls = load_urls_from_file("../data/urls/crypto_external_web_2.txt")

    for idx, url in enumerate(benign_urls):
        crawl_site(url, idx)



