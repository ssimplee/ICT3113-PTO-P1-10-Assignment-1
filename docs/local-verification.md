# Member 1 local verification

This records development checks, not assignment benchmark results.

## Host observed on 22 September 2026

- Windows 11 Pro, version 10.0.26200.
- AMD Ryzen 7 7700, 8 cores and 16 logical processors.
- OS-visible memory: 16,482,252 KiB (approximately 15.72 GiB).
- Local Python 3.12; isolated dependencies in `.venv`.
- Docker client 29.5.3, configured for `desktop-linux`.

The initial Docker check failed because the Docker Desktop Linux engine pipe
was absent. Docker subsequently became available. On 23 September the complete
Compose stack was built and exercised with Ollama running inside Docker; a
host Ollama installation was not needed. Docker exposed 16 logical CPUs and
8,174,346,240 bytes of memory to its Linux environment.

## Functional checks

Run from the repository root after installing `service/requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Six automated tests passed. Unit/API tests use temporary databases and a simulated Ollama response. They check
empty initial state, successful persistence across app recreation, literal
search, counts for all categories, CPU-only request options, invalid input,
upstream timeout, invalid categories, and request-log correlation. These tests
do not measure model accuracy, actual inference latency, or load capacity.
The HTTP integration test starts the service in a separate process and a real
HTTP backend stub. It checks that classification blocks the response, two
requests call the model sequentially, data survives process restart, and HTTP
request IDs match persisted log entries.

## Docker and real Ollama integration

The isolated `ict3113-group10-smoke` Compose project built and started
successfully. A synthetic mortgage complaint was classified, persisted, found
by search, and counted by stats. Invalid input and an unknown route returned
400 and 404. Restarting the service container retained the one stored ticket.
All captured response IDs and statuses reconciled with service JSONL records.
The model returned `Bank account or service` for the mortgage-payment example;
the connection test accepts any valid category and does not establish correctness.

Ollama `0.11.11` reported `100% CPU` for `qwen3:0.6b`, with a 4096-token runtime
context. The full model digest was
`7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`.
This is a connection check, not a candidate recommendation or accuracy result.
The initial attempt occurred before the model pull completed and returned 502;
that failure evidence is retained alongside the successful retry.

Evidence is in `logs/smoke-2026-09-23/`: request logs, captured responses,
post-restart stats, automated test output, CPU processor status, model tags and
digests, Docker resource allocation, image digest, and dependency versions.
The tested implementation revision is recorded in `environment.json`.
The smoke containers were stopped and removed after verification; their named
model and database volumes were retained. The normal project database was not
populated by this check.

The supplied dataset was not imported or submitted to a model. The team must
record the actual Docker resource allocation, Ollama version, model tag and
digest, CPU-only processor status, and separate load-generator host before
benchmarking. Freeze the golden set and prediction record in Git first.
