# JMeter preparation and run playbook

Status: results and analysis are retained for 36 load runs (four models across normal,
peak and read-heavy profiles, with three repetitions each) and one Llama 1B stress
run under [runs/](runs/). Each measured run has raw `results.jtl`, service logs and
`analysis.json`; the stress run also has a [summary](runs/stress-llama1-r1/summary.md).
Recorded results do not mean every configuration passed the requirements. Use the
per-run analysis and `docs/requirements.md` to assess performance and model selection.
Preparing bundles, opening a plan, and invoking the PowerShell scripts without their
execution switches send no test traffic.

## Files and machines

- Computer A: Docker triage service/Ollama, presently LAN address `192.168.1.5:18000`.
- Computer B: Windows, Java 21, Apache JMeter 5.6.3; run CLI measurements here only.
- `load-test.jmx`: editable normal-load template, status/category assertions and request-ID extraction.
- `prepare_run.py`: standard-library Python 3 script generating isolated, reproducible bundles.
- `Prepare-Server.ps1`: preview by default; `-Apply` recreates only the service with fresh per-run storage.
- `Start-Run.ps1`: preview by default; `-Start` invokes non-GUI JMeter.
- `results.properties`: CSV JTL including request_id, row, elapsed, status, assertions and threads.

Generated bundles exclude the template's disabled connectivity group.
Raw outputs and logs are not gitignored; retain them in the repository. SQLite storage
may be large; logs/JTL are the mandatory measurement evidence.

## Prepare new run bundles

Run from repository root on A (or B with Python installed):

```powershell
python jmeter/prepare_run.py --profile validation --model llama1 --run-id validation-llama1-r1
python jmeter/prepare_run.py --profile normal --model llama1 --repeat 1 --run-id normal-llama1-r1
```

Each folder under `jmeter/runs/` contains `plan.jmx`, `data/tickets.csv`,
`results.properties`, `manifest.json` and `server.override.json`. Generation refuses
to overwrite an existing folder. Use a new ID for retries. Hashes pin each generated
plan, CSV and properties file. Git revision and exact model tag/digest are recorded.

To generate bundles for the full 36-run matrix:

```powershell
foreach ($model in @('qwen06','llama1','qwen17','llama3')) {
    foreach ($profile in @('normal','peak','read-heavy')) {
        foreach ($repeat in 1..3) {
            $runId = "$profile-$model-r$repeat"
            if (-not (Test-Path "jmeter/runs/$runId")) {
                python jmeter/prepare_run.py --profile $profile --model $model --repeat $repeat --run-id $runId
                if ($LASTEXITCODE -ne 0) { throw "Preparation failed: $runId" }
            }
        }
    }
}
python jmeter/prepare_run.py --profile stress --model llama1 --run-id stress-llama1-r1
```

Use `--host NEW_IP` if A's address changes. Regenerate into new run IDs rather than
editing hashed bundles. Push the intended preparation files and fetch/pull them on B;
copy the identical bundle to both machines.
Preview commands (no traffic or container changes):

```powershell
.\jmeter\Prepare-Server.ps1 -RunId normal-llama1-r1
.\jmeter\Start-Run.ps1 -RunId normal-llama1-r1
```

The example run IDs already exist in the retained evidence. Use new IDs for new
measurements.

## Profile definitions

| Profile | Warm-up | Measured arrivals | POST/search/stats per minute |
|---|---:|---:|---|
| validation | 0 | 1 min | 2 / 2 / 2 (diagnostic only) |
| normal | 2 min | 15 min | 12 / 2.4 / 0.6 |
| peak | 2 min | 10 min | 36 / 7.2 / 1.8 |
| read-heavy | 2 min | 10 min | 12 / 4.8 / 1.2 |
| stress | 2 min at 6 POST/min | six 5-minute steps | 6,12,18,24,30,36 POST/min; reads 20%/5% |

All three groups start together, each with one HTTP sampler per arrival.
Random arrivals are independent of server response time. These rates are expected
rates, not exact counts: report actual attempted arrivals too. Use the same repeat
seeds across models. CSV order is shuffled with a recorded seed per repeat, then
recycled. Concurrent threads can change which arrival gets which row.
The subset is category-selected and contains only 175 of Group 10's 1,000 rows;
state this sampling limitation. Labels are never sent. Search uses fixed `payment`.

All profiles include 360 seconds of final drain with no new arrivals. JMeter's open
group interrupts threads at schedule end; this allowance exceeds the 10-second
connection plus 300-second response cutoffs. Confirm no samples were truncated.
Drain time is additional wall time: the 36 formal runs require about 11h48 of scheduled
time including warm-up and drain, before setup, downloads, validation and stress.
Client timeouts do not guarantee Ollama has stopped work; do not start another run
until the previous server activity has drained. This is especially important for 3B.

## Prepare a server for one run

On A, ensure the existing Compose stack runs and pull the chosen exact tag from the
bundle manifest if missing. Pulls can change mutable registry tags: the preparation
script rejects any digest that differs from the frozen pin. Do not substitute a new
digest without documenting a separate condition.

```powershell
.\jmeter\Prepare-Server.ps1 -RunId validation-llama1-r1 -Apply
```

The `-Apply` command checks the installed
digest, creates separate database/log folders, recreates the service and checks empty
stats. It preserves existing volumes and never bulk-loads data. The preflight GET is
in the service log but excluded from measured arrivals. Copy the generated
`server-ready.json` to the same bundle folder on B. Record wired/Wi-Fi connection,
both LAN addresses, network conditions, background applications and power settings
in a `network-notes.md` alongside it. Synchronize both Windows clocks and record any
known offset. Keep hardware, resource allocation, software and prompt fixed.

The current A has different hardware/resources from the historical accuracy host.
Report this explicitly; old latency predictions are not same-hardware comparisons.
The two-minute warm-up includes model loading; if it is insufficient, document it,
settle the warm-up rule before formal runs and regenerate all affected bundles.

## Short validation, then formal runs

On B, after server preparation, start the validation run:

```powershell
.\jmeter\Start-Run.ps1 -RunId validation-llama1-r1 -Start
```

The script captures B's environment and invokes `jmeter -n` with `-q`, `-l` and `-j`.
It rejects edited bundle hashes or reuse of a run already attempted. A server-ready
file is a snapshot, not live proof: confirm A is still serving that run and no other
person changed its configuration. No parallel benchmark processes on either machine.
The validation uses random arrivals, so an endpoint might receive zero requests;
repeat a diagnostic with a new ID if any endpoint is absent. This is not formal evidence.

Before formal tests, check all three endpoint labels, expected 201/200 codes, category
assertion compilation, nonempty CSV row IDs for POST, request-ID extraction, correct
JTL headers and actual arrival timestamps. Inspect `jmeter.log` for errors. Confirm
CPU-only inference with `docker compose exec ollama ollama ps` on A during activity
and retain output. Validate that the load generator keeps up and is not resource-bound.
Save validation evidence separately.

For each formal bundle, repeat server preparation, readiness transfer and client start.
Never reuse a validation database. After completion, copy A's `service-logs/` into B's
matching folder (or B's client files to A). Retain `results.jtl`, `jmeter.log`, manifests,
client start/finish files, server-ready file, CPU observations and all service logs.
Use `docker compose logs --no-color service ollama` to retain runtime diagnostics as
well. Keep full evidence even for unsuccessful or interrupted runs. Commit before
moving on to final report tables; do not replace failures with reruns silently.

## Stress and interpretation

The prepared stress profile explores 6 through 36 POST/min. It is an upper search
range, not a claimed system limit. If all steps pass, extend the next version to higher
rates. If 6 fails, follow with lower-rate steps to bracket the limit. The first failing
step bounds the sustainable rate only under this experiment's duration and thresholds.
If the server becomes unresponsive, stop gracefully, record when/why and preserve
evidence. A stopped run is partial, never a completed configuration.

For normal/peak/read-heavy, derive the start of arrivals from the JMeter engine start
event in `jmeter.log` (not the first randomly arriving sample). Record that timestamp
explicitly. Measurement is [start + warmup, start + warmup + measured duration).
Select latency/error cohorts by JTL sample START timestamp and retain their eventual
outcomes in the drain. Report elapsed (not JMeter's first-byte `Latency`) p50/p95/p99,
errors and sample counts per endpoint. Report successful completions inside the
measurement window as throughput per minute, plus actual offered starts and backlog;
do not count late drain completions as sustained-window throughput. Separately show
eventual success of the arrival cohort. Never drop timed-out requests from percentiles
without also providing the all-attempt view and timeout counts.

For stress, apply the same calculations to each five-minute step after warm-up.
Carry-over backlog is intentional; explain its effect. Use the specified 95% offered
POST throughput, <=1% POST errors and <=30s POST p95 boundary. Plot starts/completions
over time to diagnose buildup; observe recovery after arrivals stop.

Report all three individual runs plus mean and min/max spread, not just pooled data.
Evaluate every requirement in `docs/requirements.md`; all required repetitions must
pass. Join request_id to service logs and explain MISSING IDs, preflight requests and
client timeouts that later finish on the server. Unexplained gaps block using a run
as evidence. Do not use service handler duration as end-to-end latency.

## References

- [Apache Open Model Thread Group](https://jmeter.apache.org/usermanual/component_reference.html#Open_Model_Thread_Group): schedules, seeds and drain behaviour.
- [Apache CLI workflow](https://jmeter.apache.org/usermanual/get-started.html): non-GUI measurement.
- [Apache result properties](https://jmeter.apache.org/usermanual/properties_reference.html): CSV fields and sample variables.
