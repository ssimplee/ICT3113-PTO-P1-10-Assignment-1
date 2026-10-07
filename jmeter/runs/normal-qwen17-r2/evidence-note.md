# Qwen 1.7B normal run 2 evidence note

PERF-02 fails: POST p95 10.7646s exceeds 10s. PERF-04 fails: search p95 9.1793s and stats p95 7.3888s exceed 5s. Overall measured error rate is 1/227 = 0.4405%, below PERF-03's 1% limit. POST error rate is 1/183 = 0.5464%.

The JTL failure at 2026-10-07T15:05:30.748000+08:00, golden row 10951, is a ConnectTimeoutException after 10,003ms, with sentBytes=0, no HTTP status and request_id=MISSING. No service request record is expected for this failed connection. This explains the analyzer's unmatched-ID entry; it must not be dropped from latency/error metrics. These records do not establish whether network conditions or the server connection backlog caused the timeout.

All 253 other client requests match one service entry each. The 254th service entry is the preflight GET /stats. There are no unexplained extra handled requests, no duplicate client IDs, and no JMeter WARN/ERROR log entries. The timeout is still recorded as a failed JTL sample.

Window completions include one successful warm-up POST; measured POST arrivals are 183, of which 182 succeed. The failed connection completes its timeout after the window end and is the analyzer's one pending measured POST at the cutoff; that count is client-outstanding, not proof of a server-side queued ticket. Window completion throughput is 12.2/min; successful measured-cohort throughput is 182/15 = 12.1333/min. Both exceed the required throughput threshold.

Sources: results.jtl, analysis.json, jmeter.log and service-logs/requests.jsonl in this folder. Preserve this run; do not replace it with a rerun.
