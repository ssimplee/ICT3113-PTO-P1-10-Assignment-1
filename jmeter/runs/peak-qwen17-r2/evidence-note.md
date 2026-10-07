# Qwen 1.7B peak run 2 evidence note

PERF-05 numeric failure: POST p95 300.00905 seconds (limited by the client timeout), successful POST window throughput 20.8/min, and measured total error rate 153/450 = 34%. Whole-run errors are 153/539 = 28.3859%.

386 responses with real request IDs match service logs by status, endpoint and model. The 153 failures lack response IDs: 77 SocketTimeoutExceptions (65 POST, 9 search, 3 stats), and 76 NoHttpResponseExceptions (68 POST, 7 search, 1 stats). Repeated MISSING is an extraction sentinel, not duplicated server UUIDs.

78 additional server entries comprise one preflight GET /stats and 77 successful completions (65 POST, 9 search, 3 stats). These endpoint counts agree with the socket-timeout counts, consistent with server completion after client timeout; individual client-to-server pairing is NOT established. The 76 no-response failures have no remaining matched server entries. The precise cause requires investigation. Do not interpret exception sample sentBytes=0 as proof that no request reached the server.

The last captured handler completion precedes client-finish.json. Preserve the run; do not replace failures by rerunning. Capture of container diagnostics occurred after completion and may include earlier activity from the shared Ollama container. Client latency/error/throughput measurements are available; request-level reconciliation of failed samples remains incomplete. No JMeter WARN/ERROR log entries were recorded, but failed JTL samples remain failures.

Sources: results.jtl, analysis.json, service-logs/requests.jsonl, client-finish.json and container-diagnostics.log.
