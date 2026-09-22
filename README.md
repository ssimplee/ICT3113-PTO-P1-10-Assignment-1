# ICT3113-PTO-P1-10 Assignment 1

This repository contains the deliberately simple Assignment 1 baseline: one single-threaded Flask handler, synchronous Ollama classification, SQLite storage, and JSONL request logs. It is a lab baseline, not a production deployment. The Werkzeug development server deliberately runs one handler at a time (`threaded=False`, one process); it has no cache, background jobs, or queue.

## Run locally with Docker

Copy the environment example if you need to change a host setting:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose exec ollama ollama pull qwen3:0.6b
```

The default service address is `http://127.0.0.1:18000`. Ollama has no host port and is reachable only from the Compose network. Images are pinned to `python:3.12.11-slim-bookworm` and `ollama/ollama:0.11.11`; Ollama uses CPU only: the application sends `num_gpu: 0` for each request, Compose assigns no GPU devices, and `OLLAMA_NUM_PARALLEL=1` keeps one model request in flight.

`SERVICE_BIND_ADDRESS` defaults to `127.0.0.1`, and `SERVICE_PORT` defaults to `18000` so it can coexist with other local projects. A separately controlled test host can set `SERVICE_BIND_ADDRESS=0.0.0.0`. `LOG_DIR` defaults to `./logs`; set it to a distinct host directory for an isolated run, for example `LOG_DIR=./logs/smoke-2026-09-23`. The database lives in the named `tickets-data` volume at `/data`; logs are bind-mounted at `/logs`.

The initial `tickets-data` volume is empty. Ticket records persist when containers restart or are recreated, and only disappear when that named volume is deliberately removed. `ollama-models` similarly preserves pulled models.

## Model selection and connection smoke check

`qwen3:0.6b` is the default only for a connection smoke check. Pull it before submitting any ticket, then use a synthetic narrative to confirm that the service can reach a local model. Do not bulk-import CSV data.

Choose benchmark candidates separately, set `OLLAMA_MODEL` to the selected local tag, and restart the service after changing it:

```powershell
$env:OLLAMA_MODEL = "candidate:tag"
docker compose up -d --force-recreate service
```

Before benchmarking, inspect the CPU-only model process and record the exact model digest. `ollama ps` should show the active processor state:

```powershell
docker compose exec ollama ollama ps
```

The tag-to-digest record can be collected without exposing Ollama to the host; run a one-off Python request through the service container:

```powershell
docker compose exec service python -c "import os,requests; tag=os.environ['OLLAMA_MODEL']; rows=requests.get(os.environ['OLLAMA_BASE_URL']+'/api/tags',timeout=10).json()['models']; print([(m['name'],m.get('digest')) for m in rows if m['name']==tag])"
```

Freeze the human-labelled golden set and its prediction record in Git before running a benchmark. The synthetic smoke check is only a connectivity check; it is not accuracy, latency, throughput, or load evidence.

## HTTP contract

`POST /tickets` accepts a JSON object containing a non-empty string `narrative`. It classifies synchronously and returns `201` with `id`, `narrative`, `category`, `created_at`, and `model`. `GET /search?q=...` returns `tickets` and `count`; it uses literal, case-sensitive substring matching, so `%` and `_` are ordinary characters. `GET /stats` returns `total` and all seven category counts, including zeroes.

Every response includes `X-Request-ID`. Errors have this shape:

```json
{"error":{"code":"invalid_narrative","message":"narrative must be a non-empty string."},"request_id":"..."}
```

Expected application errors include `invalid_narrative` (400), `invalid_query` (400), `unsupported_media_type` (415), `ollama_unavailable` (502), `invalid_classification` (502), and `ollama_timeout` (504). Unexpected failures return `internal_error` (500). Each request appends one JSON object to `requests.jsonl` with request ID, timestamp, method, path, status, duration, configured model, category, ticket ID, and error code. Narratives are never written to that log; a log-write failure is reported by the service logger.

## Functional checks

The unit/API tests use a fake Ollama response and temporary files. The HTTP integration test starts the real service process and a controlled HTTP backend; it verifies blocking classification, sequential backend calls, persistence across restarts, and log correlation. Neither requires Docker or a pulled model:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r service/requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Run a real Ollama connection check in a separate Compose project so that the
normal service database stays empty:

```powershell
$env:LOG_DIR = './logs/smoke-2026-09-23'
docker compose -p ict3113-group10-smoke up -d --build
docker compose -p ict3113-group10-smoke exec ollama ollama pull qwen3:0.6b
python scripts/smoke_check.py --output logs/smoke-2026-09-23/responses.json
docker compose -p ict3113-group10-smoke exec ollama ollama ps
docker compose -p ict3113-group10-smoke down
Remove-Item Env:LOG_DIR
```

This inserts one synthetic ticket into the isolated smoke database. `down`
preserves its volumes. Keep service JSONL logs and raw JMeter results for every
reported run in Git. Service duration measures handler time; JMeter measures
client-observed latency including waiting before the single handler accepts a
request. Do not substitute one for the other.

## Branch and commit workflow

Use `feat/<topic>` for features, `docs/<topic>` for documentation-only work,
and `fix/<topic>` for fixes. Keep related work in small, tested commits. The
Member 1 baseline is developed on `feat/member1-baseline`; merge it after team
review. Benchmarking and final model recommendations belong to the later team
steps, not this implementation change.
