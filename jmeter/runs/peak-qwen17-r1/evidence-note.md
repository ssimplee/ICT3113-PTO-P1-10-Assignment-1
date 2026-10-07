# Qwen 1.7B peak run 1: overload and reconciliation limits

PERF-05 numeric failure: POST p95 300.010s (client timeout-censored); successful POST completion throughput 22.2/min versus 34.2/min minimum. Overall measured errors: 110/460 = 23.9130%. Whole-run errors: 110/539 = 20.4082%. Keep every failed attempt in the results.

429 responses with request IDs reconcile exactly by status, endpoint and model. The remaining 110 JTL attempts have MISSING request IDs: 66 SocketTimeoutExceptions (59 POST, 6 search, 1 stats) and 44 NoHttpResponseExceptions (36 POST, 7 search, 1 stats). Repeated MISSING is a sentinel, not duplicated real UUIDs.

Service logs contain 67 entries without returned client IDs: one preflight stats request plus 66 successful completions (59 POST, 6 search, 1 stats). Their endpoint counts equal the socket-timeout counts, consistent with the server finishing requests after clients stopped waiting. This is aggregate reconciliation, NOT a proven one-to-one mapping. The 44 no-response attempts have no remaining matched server entries; the precise cause requires diagnostics. sentBytes=0 on these exception samples is not proof that no request reached the server.

Do not claim all 539 requests individually reconcile. The client-observed latency/error/throughput figures are retained, but complete request-level traceability for failed attempts remains a limitation. No rerun replaces this evidence. Retain container-diagnostics.log, JTL, JMeter log, service logs and SQLite data for further investigation. Container diagnostics may include earlier runtime activity because Ollama is shared across runs.

150 measured POST attempts were outstanding at the measurement cutoff; this is client-outstanding count, not an exact server queue size. The last unmatched server completion in the captured log finishes before client-finish.json; the six-minute client drain did not turn these failed client attempts into successes.
