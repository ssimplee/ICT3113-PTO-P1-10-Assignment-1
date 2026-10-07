# Llama 3B peak run 1 evidence note

PERF-05 fails: POST successful completion throughput is 6.9/min; POST p95 is 300.01165 seconds (client timeout-censored). Measured overall failures are 427/460 = 92.8261%; whole-run failures are 427/539 = 79.2208%. Failed attempts remain included in latency percentiles.

112 responses with real request IDs reconcile by endpoint, status and model. The 427 failures have missing response IDs: 210 SocketTimeoutExceptions (169 POST, 36 search, 5 stats) and 217 NoHttpResponseExceptions (178 POST, 28 search, 11 stats). Repeated MISSING is a sentinel, not duplicate server UUIDs.

After allowing the server backlog to finish, the service log contains 323 entries. The 211 entries without matching client IDs comprise one preflight GET /stats and 210 successful completions (169 POST, 36 search, 5 stats). These counts match socket timeouts in aggregate; individual pairing is unproven. The 217 no-response failures lack matched service entries, and their exact cause is not established. Complete request-level traceability remains a limitation.

The last recorded handler completion was 2026-10-07T12:28:27.140189Z, 167.313 seconds after client-finish.json. Server logging was observed to stop before preparing the next run. JMeter completion alone did not establish server drain completion. Late server completions do not replace client failures or count toward measured client throughput.

Preserve this failed repetition; do not replace it with a rerun. Sources: results.jtl, jmeter.log, analysis.json, service-logs/requests.jsonl, client-finish.json and container-diagnostics.log.
