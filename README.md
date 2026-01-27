# Cryptojacking Detection for Browsers
### Early Detection using Classical ML and Quantum Machine Learning (QML)

---

## 📌 Problem Statement

Design and evaluate an early-stage browser-based cryptojacking detection framework that:

1. Leverages **dynamic browser execution behavior** (runtime and network signals) rather than static signatures  
2. Is **resilient to JavaScript and WebAssembly obfuscation and code diversification**  
3. Evaluates whether **Quantum Machine Learning (QML)** provides advantages over classical ML in **small-sample, early-detection scenarios**

---

## 👥 Authors

- **Aryan Jain** — [@aryan802](https://github.com/aryan802)  
- **Mridul Yadav** — [@mridul2493](https://github.com/mridul2493)  

**Under the guidance of:**  
Dr. Adrija Bhattacharya

---

## 🧠 Overview

Cryptojacking is a stealthy browser-based attack in which malicious JavaScript or WebAssembly code exploits user devices to mine cryptocurrency without consent. Signature-based and static approaches are increasingly ineffective due to obfuscation, rapid infrastructure churn, and short-lived campaigns.

This project proposes a **behavior-first detection pipeline** that analyzes **early browser execution traces**—including memory usage, task execution behavior, and network activity—to detect cryptojacking within the **first few seconds of page load**.

The framework is explicitly designed for:
- early detection
- evasion resistance
- small, high-quality datasets  
making it particularly suitable for **QML experimentation**.

---

## ✨ Key Features

- **Early Detection Focus** using short execution windows (FAST crawl)
- **Dynamic Runtime Analysis** via Chrome DevTools metrics
- **Network-Aware Detection** (request patterns, scripts, WASM activity)
- **Obfuscation-Resilient Design** independent of code signatures
- **Fault-Tolerant Crawling** for dead and sinkholed domains
- **QML-Compatible Feature Space** (≤ 12 numeric features)

---

## 🏗️ Technical Architecture

### Core Components

1. **FAST Web Crawler**
   - Headless Chrome-based crawler
   - Collects runtime metrics and network logs
   - Designed for large-scale screening

2. **Runtime Metrics Collector**
   - Extracts fine-grained execution metrics
   - Focus on early behavioral signals

3. **Network Log Analyzer**
   - Parses request counts, script loads, WASM activity, and host diversity

4. **Indicator-Based Screening**
   - Lightweight heuristics for candidate selection
   - Used only for dataset curation, not final labeling

5. **Dataset Builder**
   - Ensures strict separation of benign and cryptojacking data
   - Prevents cross-contamination and overwriting

---

## 🚩 Detection Indicators (Screening Stage)

> Indicators are used **only for candidate identification**, not for final labels.

### Indicator 1 — WebAssembly Presence
- WASM usage as a high-recall screening signal
- Robust against code obfuscation

### Indicator 2 — Runtime Behavioral Anomalies
Collected over short windows (~10 seconds):
- `JSHeapUsedSize`
- `TaskDuration`
- Overall execution dynamics

A site is flagged as a candidate if:
WASM present OR suspicious runtime behavior


---

## 📊 Dataset Summary (Current)

| Class | Count | Crawl Mode |
|-----|------|-----------|
| Cryptojacking | 89 | FAST |
| Benign | 177 | FAST |
| **Total** | **266** | |

### Data Sources
- **Cryptojacking candidates**: Public threat intelligence feeds, academic datasets, blocklists
- **Benign websites**: Tranco Top Sites list

Due to the ephemeral nature of cryptojacking infrastructure, many candidate domains are unreachable at crawl time. Only successfully crawled sites are retained.

---

## ⚡ Crawling Modes

| Feature | FAST Crawl |
|------|-----------|
| Wait time | ~5 seconds |
| Metric window | ~10 seconds |
| HTML capture | No |
| Scale | Hundreds of sites |
| Purpose | Early detection & screening |

This project intentionally focuses on **FAST crawl data** for early detection analysis.

---

## 🧪 Feature Extraction (FAST Data)

### Runtime Features
1. `task_mean` — mean TaskDuration  
2. `task_std` — standard deviation of TaskDuration  
3. `heap_delta` — last − first JSHeapUsedSize  
4. `heap_mean`  
5. `heap_std`

### Network Features
6. `total_requests`  
7. `script_requests`  
8. `wasm_requests`  
9. `unique_hosts`

**Total features: 9**  
Optimized for anomaly detection and QML models.

---

## 🧬 Project Status

- ✅ Crawling and data collection pipeline completed
- ✅ Robust handling of dead cryptojacking domains
- ✅ Final labeled dataset prepared
- ✅ FAST runtime and network features extracted
- 🔜 Classical ML baselines
- 🔜 Quantum Machine Learning models and evaluation

---

## ⚙️ Requirements

- Python 3.12+
- Chrome / Chromium
- ChromeDriver
- Selenium
- NumPy, Pandas, Scikit-learn  
(QML libraries will be added in later phases)

---


## 📝 Notes

- The system prioritizes **early detection and robustness**
- Screening-stage false positives are expected and documented
- Dataset design is aligned with **small-sample learning**
- QML evaluation focuses on feasibility and comparative benefit

---

## 📚 References

- URLhaus: https://urlhaus.abuse.ch/  
- Tranco Top Sites: https://tranco-list.eu/  
- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/

