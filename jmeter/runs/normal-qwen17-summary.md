# Qwen 1.7B normal-load results

Three repetitions; two-minute warm-up excluded. Latencies include all measured attempts and use linear-interpolated percentiles.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 4070.000 | 4327.000 | 3466.000 | 3954.333 | 3466.000-4327.000 |
| POST tickets / p95_ms | 9572.000 | 10764.600 | 13259.000 | 11198.533 | 9572.000-13259.000 |
| POST tickets / p99_ms | 11029.800 | 13556.040 | 18546.000 | 14377.280 | 11029.800-18546.000 |
| POST tickets / completions_per_minute | 12.000 | 12.200 | 12.267 | 12.156 | 12.000-12.267 |
| POST tickets / error_percent | 0.000 | 0.546 | 0.000 | 0.182 | 0.000-0.546 |
| GET search / p50_ms | 768.000 | 974.000 | 783.000 | 841.667 | 768.000-974.000 |
| GET search / p95_ms | 5805.200 | 9179.300 | 8682.000 | 7888.833 | 5805.200-9179.300 |
| GET search / p99_ms | 6880.240 | 12556.700 | 11450.800 | 10295.913 | 6880.240-12556.700 |
| GET search / completions_per_minute | 2.467 | 2.333 | 2.467 | 2.422 | 2.333-2.467 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 25.500 | 4259.000 | 737.000 | 1673.833 | 25.500-4259.000 |
| GET stats / p95_ms | 3489.550 | 7388.800 | 7842.400 | 6240.250 | 3489.550-7842.400 |
| GET stats / p99_ms | 3756.310 | 8336.960 | 9370.080 | 7154.450 | 3756.310-9370.080 |
| GET stats / completions_per_minute | 0.667 | 0.600 | 0.533 | 0.600 | 0.533-0.667 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

PERF-02 FAILS: POST p95 exceeds 10 seconds in repetitions 2 and 3. PERF-04 FAILS: search p95 exceeds 5 seconds in every repetition; stats exceeds 5 seconds in repetitions 2 and 3. PERF-01 throughput and PERF-03 overall error-rate numeric thresholds are met in all repetitions. Means do not override individual failures.

Of 762 whole-run attempts, 761 succeeded and match service logs. Run 2 has one ConnectTimeoutException with sentBytes=0 and request_id=MISSING, explaining its unmatched ID (see normal-qwen17-r2/evidence-note.md). Preserve this failed attempt in all-attempt latency and error metrics. Every service log also includes one preflight GET /stats. No duplicate client IDs or JMeter WARN/ERROR entries.

Run 3 counts 184 POST completions in the window, including three warm-up requests, versus 181 measured arrivals. Run 1 has one POST finish during drain; run 2 has one warm-up completion and one measured connection timeout ending after the window. All throughput comparisons remain above the required target when these boundaries are explained.

Only 8-10 measured stats requests per run; tail estimates have limited precision. No per-run CPU observation files supplied for these repetitions. Sources: normal-qwen17-r1 through normal-qwen17-r3 analysis.json, JTL and service logs.
