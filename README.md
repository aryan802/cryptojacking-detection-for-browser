# Cryptojacking Detection for Browsers
### Early Detection using Classical Machine Learning and Quantum Machine Learning (QML)

---

# 📌 Problem Statement

Design and evaluate an early-stage browser-based cryptojacking detection framework that:

1. Uses dynamic browser execution behavior instead of static signatures
2. Remains resilient against JavaScript and WebAssembly obfuscation
3. Evaluates whether Quantum Machine Learning (QML) provides advantages over classical ML for small-sample cybersecurity datasets

---

# 👥 Authors

- Aryan Jain — [@aryan802](https://github.com/aryan802)
- Mridul Agarwal / Yadav

### Under the Guidance of
Dr. Adrija Bhattacharya

---

# 🧠 Overview

Browser-based cryptojacking is a stealthy attack in which malicious JavaScript or WebAssembly code uses a victim’s device to mine cryptocurrency without consent.

Traditional signature-based detection methods struggle against:
- obfuscated scripts
- dynamically loaded miners
- rapidly changing infrastructure
- short-lived attack campaigns

This project proposes a behavior-first detection pipeline that analyzes browser runtime activity during the early execution phase of websites.

Instead of relying on source-code signatures, the system monitors:
- CPU usage
- memory consumption
- JavaScript execution behavior
- task execution characteristics
- network activity
- WebAssembly usage

The project evaluates both Classical Machine Learning and Quantum Machine Learning approaches under identical experimental conditions.

---

# ✨ Key Features

- Early-stage cryptojacking detection
- Dynamic runtime behavior analysis
- Obfuscation-resilient design
- Browser automation using Selenium
- Runtime and network-aware feature extraction
- Classical ML and Quantum ML comparison
- Lightweight feature space suitable for QML
- Comparative ROC-AUC evaluation

---

# 🏗️ Technical Architecture

## Core Components

### 1. Automated Browser Crawler
- Headless Chrome-based crawler
- Selenium-driven automated browsing
- Collects runtime and network activity

### 2. Runtime Metrics Collector
Extracts:
- CPU usage
- Heap memory statistics
- Task execution behavior
- JavaScript runtime metrics

### 3. Network Activity Analyzer
Captures:
- total requests
- script requests
- WebAssembly requests
- unique host communication

### 4. Feature Extraction Pipeline
Aggregates runtime observations into compact numerical features suitable for ML and QML models.

### 5. Model Training and Evaluation
Implements:
- Classical ML models
- Quantum Kernel methods
- Hybrid QML approaches

---

# ⚡ FAST Crawl Strategy

This project focuses on FAST crawl analysis for early detection.

| Feature | FAST Crawl |
|------|------|
| Wait Time | ~5 seconds |
| Metric Window | ~10 seconds |
| HTML Capture | No |
| Scale | Hundreds of websites |
| Goal | Early behavioral detection |

The system intentionally prioritizes early behavioral indicators instead of long-duration monitoring.

---

# 🚩 Detection Indicators

## Indicator 1 — WebAssembly Presence
WebAssembly activity is used as a high-recall screening signal because many browser miners rely on WASM execution.

## Indicator 2 — Runtime Behavioral Anomalies
Behavioral indicators include:
- abnormal CPU utilization
- unusual task duration
- increasing heap memory usage
- suspicious execution patterns

Indicators are used only for candidate identification and dataset preparation.

---

# 📊 Dataset Summary

| Class | Count |
|------|------|
| Cryptojacking Websites | 89 |
| Benign Websites | 177 |
| Total | 266 |

### Data Sources
- Public threat intelligence feeds
- Academic cryptojacking datasets
- Blocklists
- Tranco Top Sites

Only successfully crawled domains were retained due to the short-lived nature of cryptojacking infrastructure.

---

# 🧪 Feature Extraction

## Runtime Features

1. `task_mean`
2. `task_std`
3. `heap_delta`
4. `heap_mean`
5. `heap_std`

## Network Features

6. `total_requests`
7. `script_requests`
8. `wasm_requests`
9. `unique_hosts`

Total Features: **9**

The feature space was intentionally kept compact for compatibility with Quantum Machine Learning models.

---

# 🧹 Data Preprocessing

The preprocessing pipeline includes:

- label encoding
- removal of unnecessary columns
- RobustScaler normalization
- feature scaling
- optional quantum-compatible encoding

RobustScaler was selected because browser runtime data contains significant outliers.

---

# 🤖 Classical Machine Learning Models

The following classical models were implemented using Scikit-learn:

## Random Forest
- ROC-AUC: **0.848**

## Support Vector Machine (SVM)
- ROC-AUC: **0.747**

## XGBoost
- ROC-AUC: **0.835**

### Observation
Random Forest achieved the highest and most stable performance across folds.

---

# ⚛️ Quantum Machine Learning Models

The following Quantum Machine Learning models were implemented using PennyLane:

## Quantum Kernel SVM
- ROC-AUC: **0.671 ± 0.062**

## Trainable Quantum Kernel
- ROC-AUC: **0.72 ± 0.18**

## Hybrid QML Model
- ROC-AUC: **0.56 ± 0.11**

### Observation
Quantum models showed:
- higher variance
- sensitivity to feature encoding
- instability across folds
- strong dependence on dataset size

---

# 📈 Evaluation Metric

The models were evaluated using:

## ROC-AUC

ROC-AUC measures the ability of a model to distinguish between benign and cryptojacking classes across different thresholds.

This metric is suitable for imbalanced cybersecurity datasets.

---

# 📂 Project Structure

```bash
cryptojacking-detection-for-browser-main/
│
├── analysis/
├── crawler/
├── data/
├── feature_extraction/
├── models_classical/
├── models_qml/
├── chromedriver.exe
├── requirements.txt
└── README.md

