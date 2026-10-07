# Qwen 1.7B peak run 3 evidence note

PERF-05 numeric failure: POST p95 300.00985s (client timeout-censored), POST completion throughput 21.2/min, measured overall errors 153/455 = 33.6264%. Whole-run errors 153/539 = 28.3859%.

386 responses with real request IDs reconcile. Failures comprise 75 SocketTimeoutExceptions (56 POST, 18 search, 1 stats) and 78 NoHttpResponseExceptions (65 POST, 10 search, 3 stats). All 153 have missing response IDs. Repeated MISSING is a sentinel, not duplicate server UUIDs.

76 unmatched service entries are one preflight GET /stats plus 75 successful completions (56 POST, 18 search, 1 stats), consistent in aggregate with socket timeouts. Individual pairing is unproven. The remaining 78 no-response failures lack matched server entries; exact cause is not established. sentBytes=0 on failed samples does not prove the server received nothing.

All captured handler completions precede client-finish.json. Preserve this failed run and container diagnostics; no rerun replaces it. Complete request-level traceability remains a limitation. Sources: JTL, JMeter log, analysis.json, service logs and container-diagnostics.log.
