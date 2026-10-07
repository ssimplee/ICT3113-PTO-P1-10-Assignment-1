# Llama 3B peak run 3 evidence note

PERF-05 fails: POST successful completion throughput is 6.9/min; POST p95 is 300.013 seconds (client timeout-censored). Measured overall failures are 420/455 = 92.3077%; whole-run failures are 420/539 = 77.9221%. Failed attempts remain included in latency percentiles.

119 responses with real request IDs reconcile by endpoint, status and model. The 420 failures have missing response IDs: 212 SocketTimeoutExceptions (165 POST, 41 search, 6 stats) and 208 NoHttpResponseExceptions (172 POST, 29 search, 7 stats). Repeated MISSING is a sentinel, not duplicate server UUIDs.

The final service log contains 332 entries. Its 213 entries without matching client IDs comprise one preflight GET /stats and 212 successful completions (165 POST, 41 search, 6 stats). These counts match socket timeouts in aggregate; individual pairing is unproven. The 208 no-response failures lack matched service entries, and their exact cause is not established. Complete request-level traceability remains a limitation.

The last recorded handler completion was 2026-10-07T13:17:25.585546Z, 91.539 seconds after client-finish.json. No subsequent entries appeared for over two minutes before preparing the next run. JMeter completion alone did not establish server drain completion. Late server completions do not replace client failures or count toward measured client throughput.

Preserve this failed repetition; do not replace it with a rerun. Sources: results.jtl, jmeter.log, analysis.json, service-logs/requests.jsonl, client-finish.json and container-diagnostics.log.
