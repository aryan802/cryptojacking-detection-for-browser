# Cryptojacking Detection for Browser

## PROBLEM STATEMENT

Design and evaluate a hybrid classical - quantum machine learning framework for browser-based cryptojacking detection that:

(a) combines static (URL / HTML / JS / Wasm) and dynamic (CPU, network, DNS, timing) signals

(b) is resilient to WebAssembly obfuscation and code diversification 

(c) demonstrates whether and how QML components improve detection, early-warning latency, and robustness compared to state-of-the-art classical baselines.

## Authors

1) Aryan Jain ([aryan802](https://github.com/aryan802))
2) Mridul Yadav ([mridul2493](https://github.com/mridul2493))

under guidance of Dr. Adrija Bhattacharya

## Overview

This project develops an intelligent detection mechanism for cryptojacking—malicious code that hijacks browser resources to mine cryptocurrencies without user consent. Unlike traditional signature-based approaches, our system uses fine-grained browser execution metrics and behavioral analysis to detect cryptojacking attacks early, making it resilient against obfuscation and code variations.

## Key Features

- **Dynamic Behavior Capture**: Monitors CPU usage, network traffic, and memory heap growth in real-time
- **Static Code Analysis**: Detects WebAssembly (WASM) files and suspicious JavaScript patterns
- **Evasion-Resistant Detection**: Works independently of static code features, making it robust against obfuscation
- **Isolated Browser Instances**: Each website is crawled in a separate browser to eliminate caching bias and cross-site artifacts
- **Dual Crawling Modes**: Fast screening mode for initial candidate identification and deep crawl mode for detailed analysis
- **Comprehensive Data Pipeline**: Automated collection, validation, and labeling of benign and cryptojacking datasets

## Technical Architecture

### Components

1. **Web Crawler**: Opens URLs, captures page source, network requests, and extracts WASM URLs
2. **Asset Extractor**: Downloads and locally loads JavaScript and WASM files for analysis
3. **Metrics Collector**: Gathers fine-grained browser execution metrics via Chrome DevTools
4. **Candidate Generator**: Identifies cryptojacking candidates based on multiple indicators
5. **Dataset Pipeline**: Standardizes, validates, and labels data for model training

### Detection Indicators

**Indicator 1: WebAssembly Presence**
- WASM detection as a primary screening indicator
- Based on observation that normal page loads rarely require WASM
- Robust against obfuscation (WASM presence isn't removed by code transformation)

**Indicator 2: Runtime Behavior Anomalies**
Monitored metrics collected over multiple time windows (5s, 10s, 30s):
- `JSHeapUsedSize`: Memory heap usage patterns
- `TaskDuration`: Browser task execution duration
- `ScriptDuration`: JavaScript execution time
- `ProcessTime`: Overall process runtime

A site is flagged as a cryptojacking candidate if it exhibits:
```
WASM_present OR suspicious_runtime_behavior
```

## Dataset Strategy

### Target Scale
- **Benign websites**: 300-500 initial, ~100-150 validated
- **Cryptojacking websites**: 150-300 initial, ~60-100 validated

### Data Sources
- **Cryptojacking URLs**: URLhaus, GitHub repositories
- **Benign URLs**: Tranco top sites list
- **Data Validation**: Fault-tolerant pipeline to handle dead domains and false positives

### Crawling Modes

| Aspect | Fast Crawl | Deep Crawl |
|--------|-----------|-----------|
| Wait Time | 5 seconds | 15 seconds |
| Metric Duration | 10 seconds | 30 seconds |
| HTML Capture | ❌ No | ✅ Yes |
| Scope | Many sites (screening) | Validated candidates only |
| Purpose | Initial screening | Final dataset preparation |

### Data Collection Workflow
1. **Fast Crawl**: Rapid screening on candidate list using WASM and runtime indicators
2. **Indicator Analysis**: Filter by WASM presence and suspicious behavior
3. **Deep Crawl**: Detailed analysis on high-confidence candidates with full HTML and metrics
4. **Validation**: Manual verification to eliminate false positives and dead domains

## Project Timeline

### January 23-24
- Project structure and library setup
- Web crawler development (URL opening, page source capture, network request logging)
- JavaScript and WASM file extraction and local loading
- Dynamic behavior capture pipeline implementation
- Browser metrics collection via Chrome DevTools (CPU, network, timing windows)

### January 25-26
- Dataset standardization and labeling
- Data collection pipeline completion
- Fast and deep crawling mode implementation
- Isolated browser instance architecture (per-site isolation)
- WebAssembly detector development
- Runtime behavior analysis (CPU + heap growth detection)
- Cryptojacking candidate generation and filtering
- Validation pipeline for false positive reduction
- Final labeled dataset preparation in progress

### January 27
- 89 crypto samples, now fast crawling over 160 benign samples
- Currently have 89 crypto and 177 benign with fast crawl
- Now we have runtime metrics (time series), network logs, and early execution behaviour
- Its perfect for early detection, anomaly detection, and qml(which prefers small samples)
- Next steps for today will be
     -  Dataset finalization & labelling
     -  Feature extraction (from FAST data crawl)


## Requirements

- Python 3.12+
- Chrome/Chromium browser
- ChromeDriver
- Chrome DevTools Protocol support

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run fast crawl on candidate list
python crawler.py --mode fast --input candidates.txt

# Run deep crawl for validation
python crawler.py --mode deep --input validated_candidates.txt

# Analyze and label dataset
python dataset_processor.py --input raw_data/ --output labeled_data/
```

## Data Storage

All collected data is organized in a structured format:
```
data/
├── raw/
│   ├── page_sources/
│   ├── network_requests/
│   ├── javascript_files/
│   ├── wasm_files/
│   └── metrics/
└── labeled/
    ├── benign/
    └── cryptojacking/
```

## Notes

- False negatives are not acceptable in cryptojacking detection
- The system prioritizes precision to minimize false positives in the dataset
- Each website is analyzed in isolation to ensure data integrity
- WASM presence combined with runtime anomalies provides high-confidence detection signals


## References

- URLhaus: https://urlhaus.abuse.ch/
- Tranco Top Sites: https://tranco-list.eu/
- Chrome DevTools Protocol Documentation

---

**Status**: Active Development - Currently doing Data collection and validation pipeline, next will move towards classical baselines models

