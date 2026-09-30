# ICT3113 Group 10 ticket triage baseline

This service receives one complaint at a time, asks a local Ollama model to assign one of seven categories, and stores the result in SQLite. You can search stored complaints and retrieve category counts. There is no graphical interface or homepage, and the service does not forward complaints to departments.

The Assignment 1 baseline uses one synchronous Flask/Werkzeug request handler, CPU-only inference, no application cache, no background jobs, and no bulk CSV import. It is a laboratory baseline, not a production deployment.

## What has been verified

- Six automated unit/API and HTTP integration tests passed.
- Docker-to-Ollama classification, search, counts, restart persistence, and request-log correlation passed using synthetic text.
- Ollama reported `100% CPU`. Evidence is in [local verification](docs/local-verification.md) and [the retained smoke logs](logs/smoke-2026-09-23/).
- Model correctness is not established: `qwen3:0.6b` returned `Bank account or service` for our synthetic mortgage complaint.
- Browser access has exposed a hanging-request issue. Closing browser tabs and restarting cleared it, but the underlying cause has not been fixed. Use PowerShell for the walkthrough below.

These checks cover the implemented Member 1 baseline. The 175-ticket golden set now has complete independent labels, adjudication evidence, a reproducible agreement report, and a validator. Member 4 preparation includes four locally pinned, synthetically compatible candidate models, a full model/environment manifest, a draft prediction record, and a guarded accuracy runner. Freezing the prediction record, formal accuracy testing, JMeter load/stress testing, and the final recommendation remain. See [Member 4 handoff](docs/member4-handoff.md).

## Prerequisites

On Windows, install Git and Docker Desktop with its Linux engine available. Python 3.12 is needed for the automated tests and smoke script; the service itself runs in Docker. Allow disk space for the images and model download. No host Ollama installation or GPU is needed.

All commands below are PowerShell commands. Copy only the contents of code blocks, without prompt text, Markdown backticks, or link formatting. Run one block at a time. Keep URLs as plain quoted strings. Do not use the PowerShell `curl` alias for JSON submission; use the native commands shown below.

## 1. Get the code and open the repository

For the existing local checkout:

```powershell
cd "D:\SWE\School\3113\Assignment 1"
```

For a new checkout, clone the implementation branch from a directory of your choice (repository access is required):

```powershell
git clone --branch feat/member1-baseline https://github.com/ssimplee/ICT3113-PTO-P1-10-Assignment-1.git
cd ICT3113-PTO-P1-10-Assignment-1
```

This expanded guide is developed on `docs/setup-and-testing`, based on the implementation branch. Once that branch is pushed, use `git fetch origin` and `git switch docs/setup-and-testing` to obtain it before it is merged.

## 2. Check Docker and start the service

Open Docker Desktop, wait for its engine to run, then check:

```powershell
docker version
docker compose version
```

`docker version` must show both Client and Server information. A missing Linux engine pipe means Docker is not ready.

Create the optional configuration file without overwriting an existing one:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Both `service` and `ollama` should be running. Container startup does not guarantee that the model is downloaded yet.

## 3. Download the model

For the default connection-check model:

```powershell
docker compose exec ollama ollama pull qwen3:0.6b
docker compose exec ollama ollama list
```

Wait until the pull reports `success`. The model should appear in the list. This small model verifies connectivity; it is not a final benchmark recommendation. If you changed `OLLAMA_MODEL` in `.env`, pull that exact tag instead.

## 4. Check the initially empty database

```powershell
$baseUrl = 'http://127.0.0.1:18000'
Invoke-RestMethod "$baseUrl/stats" -TimeoutSec 10 | ConvertTo-Json -Depth 5
```

A fresh database returns `total: 0` and zero for every category. Previously stored tickets remain across restarts, so nonzero counts are normal on a reused volume. The root URL `/` returns a JSON 404 because there is no homepage.

## 5. Submit one synthetic ticket

```powershell
$before = (Invoke-RestMethod "$baseUrl/stats" -TimeoutSec 10).total
$body = @{ narrative = 'My mortgage payment was charged twice.' } | ConvertTo-Json
$ticket = Invoke-RestMethod -Uri "$baseUrl/tickets" -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 180
$ticket | Format-List
```

Expected: a response containing `id`, `narrative`, `category`, `created_at`, and `model`. The HTTP success status is 201. The request waits for classification before returning. The category must be one of the seven supported values, but a valid category can still be incorrect for the complaint.

## 6. Search and verify the counts

```powershell
Invoke-RestMethod "$baseUrl/search?q=mortgage" -TimeoutSec 10 | ConvertTo-Json -Depth 5
$after = Invoke-RestMethod "$baseUrl/stats" -TimeoutSec 10
$after | ConvertTo-Json -Depth 5
$after.total -eq ($before + 1)
```

Search should include your new ticket. On a fresh database, `count` is 1; repeated tests can produce more matches. The final expression should print `True`. Search is literal and case-sensitive: `%` and `_` are ordinary characters, not wildcards.

## 7. Verify persistence after restart

```powershell
docker compose restart service
```

After the restart completes, run:

```powershell
$restarted = Invoke-RestMethod "$baseUrl/stats" -TimeoutSec 10
$restarted | ConvertTo-Json -Depth 5
$restarted.total -eq $after.total
```

Expected: `True`. If the first request races startup and fails to connect, wait briefly and retry it. Restarting does not reset the SQLite volume.

## 8. Verify invalid-input handling

Use PowerShell directly to preserve the JSON quotes:

```powershell
try {
    Invoke-RestMethod -Uri "$baseUrl/tickets" -Method Post -ContentType 'application/json' -Body '{"narrative":""}' -TimeoutSec 10
} catch {
    [int]$_.Exception.Response.StatusCode
    $_.ErrorDetails.Message
}
```

Expected: status `400` and error code `invalid_narrative`. No ticket should be added:

```powershell
(Invoke-RestMethod "$baseUrl/stats" -TimeoutSec 10).total -eq $restarted.total
```

Expected: `True`. If you see `bad_request`, the JSON could not be parsed; this is different from testing an empty narrative. Some Windows PowerShell/native curl combinations strip JSON quotes. Reuse the exact PowerShell command above.

## 9. Check request logs and CPU-only inference

```powershell
Get-Content .\logs\requests.jsonl -Tail 10
docker compose exec ollama ollama ps
```

The logs should contain successful GET/POST requests and the rejected POST with status 400 and `invalid_narrative`. Every response carries `X-Request-ID`; errors also include the same ID in their JSON body. Match that ID to `request_id` in the log.

`ollama ps` should show `100% CPU` shortly after a classification. If the model has unloaded after inactivity, an empty list is normal; submit another synthetic ticket to load it before checking again. That adds another stored ticket.

Each JSONL record contains `timestamp` (UTC), `request_id`, `method`, `path`, `status`, `duration_ms`, `model`, `category`, `ticket_id`, and `error`. Category and ticket ID are null for requests that did not create a ticket. Narratives and search query text are omitted from these logs. Log-write failures are reported to container stderr.

If `LOG_DIR` is customized, read that directory instead of `./logs`.

## Automated unit and integration tests

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r service/requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Expected: `Ran 6 tests` followed by `OK`. No virtual-environment activation is required. On systems where only the Python launcher is available, use `py -3.12 -m venv .venv` for the first command.

Run the groups separately if diagnosing a failure:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_service.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_http_integration.py -v
```

The five unit/API tests use temporary SQLite databases and simulated Ollama responses. They cover all categories, storage, search, counts, request logs, input errors, backend timeouts/connection failures, and malformed predictions. The HTTP integration test starts an actual service subprocess and controlled HTTP backend, verifies that classification blocks and model calls are sequential, then checks persistence across restart and log correlation. These tests do not modify the Docker database or measure model accuracy.

## Automated real-Ollama smoke check

With the normal Compose stack running and the model downloaded:

```powershell
$runId = Get-Date -Format 'yyyyMMdd-HHmmss'
.\.venv\Scripts\python.exe scripts/smoke_check.py --url $baseUrl --output "logs/manual-$runId/responses.json"
```

Expected output begins `PASS: real HTTP classification, persistence, search, stats, validation and request IDs.` This inserts one synthetic ticket into the running database. It accepts any valid category and is not an accuracy test. Response evidence is saved separately; server logs remain in the configured `LOG_DIR`.

### Optional isolated smoke database

To keep the normal database unchanged, run the following in a NEW PowerShell window from the repository root. Port 18001 lets it coexist with the normal stack. The new project creates separate database and model volumes, so its model needs its own pull.

```powershell
$runId = Get-Date -Format 'yyyyMMdd-HHmmss'
$project = "ict3113-smoke-$runId"
$env:SERVICE_BIND_ADDRESS = '127.0.0.1'
$env:SERVICE_PORT = '18001'
$env:LOG_DIR = "./logs/$project"
$env:OLLAMA_MODEL = 'qwen3:0.6b'
docker compose -p $project up -d --build
docker compose -p $project exec ollama ollama pull qwen3:0.6b
.\.venv\Scripts\python.exe scripts/smoke_check.py --url 'http://127.0.0.1:18001' --output "logs/$project/responses.json"
docker compose -p $project exec ollama ollama ps
docker compose -p $project down
```

Close that PowerShell window afterward to discard its environment overrides. `down` preserves the isolated volumes and logs. Each new project consumes more disk space; reuse a project if you do not require a fresh database.

## Configuration and changing models

| Setting | Default | Purpose |
|---|---|---|
| `SERVICE_BIND_ADDRESS` | `127.0.0.1` | Host interface exposing the API |
| `SERVICE_PORT` | `18000` | Host API port |
| `LOG_DIR` | `./logs` | Host directory for JSONL logs |
| `OLLAMA_MODEL` | `qwen3:0.6b` | Exact local model tag |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | Backend request timeout |

Edit `.env` to persist settings. Shell environment variables override `.env`; a new terminal avoids accidental old overrides. After changing settings, run `docker compose up -d --force-recreate service`. `docker compose restart` alone does not apply changed environment configuration.

To try a team-selected model, replace the example tag below with an actual Ollama tag:

```powershell
$env:OLLAMA_MODEL = 'candidate:tag'
docker compose exec ollama ollama pull $env:OLLAMA_MODEL
docker compose up -d --force-recreate service
```

Record the exact selected tag and full digest:

```powershell
docker compose exec -T service python -c "import os,requests; tag=os.environ['OLLAMA_MODEL']; rows=requests.get(os.environ['OLLAMA_BASE_URL']+'/api/tags',timeout=10).json()['models']; print([(m['name'],m['digest']) for m in rows if m['name']==tag])"
```

Compose uses fixed image tags `python:3.12.11-slim-bookworm` and `ollama/ollama:0.11.11`. It assigns no GPU devices, sets `OLLAMA_NUM_PARALLEL=1`, and the service requests `num_gpu: 0`. Ollama is internal to the Compose network, without a host port. SQLite is at `/data/tickets.sqlite3` in the `tickets-data` volume; Ollama models use `ollama-models`.

## Stop, resume, and database state

```powershell
docker compose down
docker compose up -d
```

Stopping with `down` preserves tickets and downloaded models. Do not add `-v` unless you intend to delete both project volumes. For a fresh test database without deleting existing evidence, use the isolated-project procedure above. There is deliberately no API for bulk import or clearing tickets.

## Troubleshooting

| Symptom | Check or action |
|---|---|
| Docker reports missing Linux engine pipe | Open Docker Desktop and wait; rerun `docker version` until Server information appears. |
| Root URL returns `not_found` | Expected: use `/stats`, `/search?q=...`, or POST `/tickets`. There is no homepage. |
| Browser or `/stats` hangs | Close all tabs for this service, then `docker compose restart service`. Test using PowerShell with a timeout. Browser idle connections are a suspected cause, not confirmed; this remains an unresolved baseline issue. A pending classification also blocks other requests by design. |
| `502 ollama_unavailable` | Check `docker compose ps`, `docker compose exec ollama ollama list`, and model spelling; finish the model pull first. |
| `502 invalid_classification` | The backend returned incomplete, malformed, or unsupported category output. The ticket is not stored. |
| `504 ollama_timeout` | Ollama exceeded the configured request timeout. Inspect its logs and CPU/memory; this does not prove the machine can meet performance requirements. |
| `400 bad_request` | Malformed JSON, often native-command quote handling; use the PowerShell JSON commands above. |
| PowerShell displays `@{...}` or truncates output | Pipe to `ConvertTo-Json -Depth 5`. |
| Connection refused/empty reply immediately after startup | Wait briefly, retry, then inspect container status/logs if it persists. |
| Port already allocated | Set a free `SERVICE_PORT` in `.env`, recreate the service, and update `$baseUrl`. |

Useful diagnostics:

```powershell
docker compose ps
docker compose logs --tail 50 service
docker compose logs --tail 50 ollama
```

## Assignment testing boundaries and handoff

The seven categories are Credit reporting, Debt collection, Mortgage, Credit card, Bank account or service, Consumer loan, and Money transfer or service. The service starts empty with a new database and accepts tickets only through POST. Group 10 uses dataset rows 10000–10999 for assignment labelling and test traffic; synthetic checks here are development diagnostics, not submission benchmark evidence.

Before formal benchmarks, commit the independently human-labelled golden set and prediction record. Select 3–5 candidates across at least two parameter-size classes, recording their exact tags and digests. Formal JMeter tests require a separate load-generator machine, open-loop arrivals, three runs per configuration, retained raw `.jtl` files, and matching service logs. The guarded golden-set accuracy runner and Member 4 handoff are now present, but the human-label and prediction-freeze gates must pass before using them formally. The repository does not yet provide the final JMeter playbook.

For access from that separate machine, configure `SERVICE_BIND_ADDRESS=0.0.0.0`, recreate the service, and use the service host's LAN address and configured port. Permit the port through the host firewall on the intended test network. Record both machines' CPU, memory, OS, network, Docker resource allocation, model/runtime settings, and Git revision.

Keep logs and raw results for every reported run in Git. Service `duration_ms` measures handler time, excluding waiting before handling, network transport, and the subsequent log write. JMeter measures client-observed latency; use it for end-to-end percentiles. A run with missing log evidence is incomplete. See [Member 1 handoff](docs/member1-handoff.md) for architecture and teammate interfaces.

## Branch and commit workflow

Use `feat/<topic>` for features, `docs/<topic>` for documentation-only changes, and `fix/<topic>` for fixes. Keep focused commits with relevant checks and review changes before merging into `main`. The implementation branch is `feat/member1-baseline`; this README update uses `docs/setup-and-testing`.
