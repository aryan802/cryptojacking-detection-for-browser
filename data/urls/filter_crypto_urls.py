import re
import os
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = "crypto_external_raw.txt"
OUTPUT_FILE = "crypto_external_web_2.txt"

# Extensions that indicate non-browser malware
BAD_EXTENSIONS = (
    ".exe", ".scr", ".zip", ".rar", ".apk", ".sh",
    ".bat", ".cmd", ".msi", ".dll", ".bin", ".ps1"
)

# Regex to detect raw IP addresses
IP_REGEX = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

def is_ip_address(hostname):
    return bool(IP_REGEX.match(hostname))

def looks_like_binary(path):
    return any(path.lower().endswith(ext) for ext in BAD_EXTENSIONS)

def clean_url(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    # Ensure scheme so urlparse works
    if not line.startswith(("http://", "https://")):
        line = "http://" + line

    parsed = urlparse(line)

    # Drop raw IP hosts
    if is_ip_address(parsed.hostname or ""):
        return None

    # Drop binary paths
    if looks_like_binary(parsed.path):
        return None

    # Must have a hostname
    if not parsed.hostname:
        return None

    return parsed.hostname.lower()

def main():
    cleaned = set()

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            result = clean_url(line)
            if result:
                cleaned.add(result)

    with open(OUTPUT_FILE, "w") as f:
        f.write("# Browser-based cryptojacking candidates only\n")
        for domain in sorted(cleaned):
            f.write(domain + "\n")

    print(f"[✓] Filtered {len(cleaned)} browser-loadable domains")
    print(f"[✓] Output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
