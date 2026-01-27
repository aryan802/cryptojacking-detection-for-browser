# cryptojacking-detection-for-browser

PROJECT LOG

23 - 24 jan
1)	Structure done, and installed some libraries and chromedriver
2)	Making a web crawler that can open url, capture page source, n/w req, extract .wasm urls and saves everything to disk(data -> raw)
3)	Extract js and wasm – identify js and wasm files, download and load them locally, prepare foundation for static and evasion-resistant detection
4)	Dynamic behaviour capture (early detection process) – for each visited webpage collect – cpu usage over time, network bytes over time, timing windows(5s, 10s, 30s) – later we will feed these to models, we will capture time based signals that enable early detection, anomaly detection and robustness against obfuscation
We capture fine-grained browser execution metrics via Chrome DevTools to enable early and behavior-based cryptojacking detection, independent of static code features

25 - 26 jan
1)	Standardize dataset structure, create labels and prepare datasets for models
2)	Data collection pipeline complete now
3)	Scale on benign and cryptojacking websites, no feature extraction and ml yet
4)	Initial target – 300 – 500 benign websites and 150 – 300 cryptojacking websites
5)	Made fast and deep crawling modes, and made crawling have separate browser instances so it may not create bias due to cache content
6)	Obtain reliable cryptojacking website candidates, void false positives & dead domains, populate in controlled batches to prevent
7)	Crypto sites we need – 
Fast crawl – 200-300
Validated – 100 – 150
Deep crawl – 60 – 100

8)	Likely cryptojacking candidates -> wasm presence, abnormal runtime behaviour(cpu + heap growth)
9)	 Modern browser almost always use wasm, normal page load rarely need wasm, obfuscation doesn’t remove wasm

10)	Writing a wasm detector (indicator 1)

11)	Each website was crawled in an isolated browser instance to eliminate caching and cross-site artifacts.

12)	Runtime Behavior (CPU + Heap Growth) (indicator 2{anomaly indicator})

Signals (from runtime metrics):
•	JSHeapUsedSize
•	TaskDuration
•	ScriptDuration
•	ProcessTime

13)	A site is cryptojacking candidate if(False negatives are not acceptable with this):
WASM present(indicator 1)  OR  suspicious runtime behavior(indicator 2)

14)	Candidate list generation and saving them

Difference b/w deep and fast crawl
Aspect	FAST	DEEP
WAIT_TIME	5s	15s
METRIC_DURATION	10s	30s
HTML saved	❌	✅
Sites crawled	many	only candidates
Purpose	screening	final dataset
15)	Deep crawl on cryptojacking candidates
16)	Wasm -> runtime -> select  (run order for candidate generation)
17)	Fast -> indicators -> deep  (may include false positives), heavy js sites may come
18)	With validation pipeline complete Working towards final labelled dataset
•	Sources for cryptojack url – URLhaus and github
•	For benign urls – trance top sites
•	Making data fault tolerant – cuz many crypto jacked urls are may have been taken down, which will hinder our crawling process

