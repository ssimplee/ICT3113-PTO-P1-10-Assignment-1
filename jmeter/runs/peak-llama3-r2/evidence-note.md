# Llama 3B peak run 2 evidence note

PERF-05 fails: POST successful completion throughput is 7.1/min; POST p95 is 300.013 seconds (client timeout-censored). Measured overall failures are 419/450 = 93.1111%; whole-run failures are 419/539 = 77.7365%. Failed attempts remain included in latency percentiles.

120 responses with real request IDs reconcile by endpoint, status and model. The 419 failures have missing response IDs: 217 SocketTimeoutExceptions (172 POST, 39 search, 6 stats) and 202 NoHttpResponseExceptions (165 POST, 28 search, 9 stats). Repeated MISSING is a sentinel, not duplicate server UUIDs.

After allowing the server backlog to finish, the service log contains 338 entries. The 218 entries without matching client IDs comprise one preflight GET /stats and 217 successful completions (172 POST, 39 search, 6 stats). These counts match socket timeouts in aggregate; individual pairing is unproven. The 202 no-response failures lack matched service entries, and their exact cause is not established. Complete request-level traceability remains a limitation.

The last recorded handler completion was 2026-10-07T12:53:28.113443Z, 179.205 seconds after client-finish.json. Logging was observed to stop before preparing the next run. JMeter completion alone did not establish server drain completion. Late server completions do not replace client failures or count toward measured client throughput.

Preserve this failed repetition; do not replace it with a rerun. Sources: results.jtl, jmeter.log, analysis.json, service-logs/requests.jsonl, client-finish.json and container-diagnostics.log.
