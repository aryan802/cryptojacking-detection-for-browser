# cryptojacking-detection-for-browser

PROJECT LOG
24th jan
1)	Structure done, and installed some libraries and chromedriver
2)	Making a web crawler that can open url, capture page source, n/w req, extract .wasm urls and saves everything to disk(data -> raw)
3)	Extract js and wasm – identify js and wasm files, download and load them locally, prepare foundation for static and evasion-resistant detection
4)	Dynamic behaviour capture (early detection process) – for each visited webpage collect – cpu usage over time, network bytes over time, timing windows(5s, 10s, 30s) – later we will feed these to models, we will capture time based signals that enable early detection, anomaly detection and robustness against obfuscation
We capture fine-grained browser execution metrics via Chrome DevTools to enable early and behavior-based cryptojacking detection, independent of static code features

25th
1)	Standardize dataset structure, create labels and prepare datasets for models
2)	Data collection pipeline complete now
3)	Scale on benign and cryptojacking websites, no feature extraction and ml yet
4)	Initial target – 300 – 500 benign websites and 150 – 300 cryptojacking websites
5)	Made fast and deep crawling modes, and made crawling have separate browser instances so it may not create bias due to cache content
6)	Obtain reliable cryptojacking website candidates, void false positives & dead domains
