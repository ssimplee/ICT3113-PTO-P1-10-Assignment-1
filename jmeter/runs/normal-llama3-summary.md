# Llama 3B normal-load results

Fifteen-minute measurement windows after two-minute warm-up. All measured-arrival percentiles use linear interpolation.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 31229.000 | 35235.000 | 65828.000 | 44097.333 | 31229.000-65828.000 |
| POST tickets / p95_ms | 96543.000 | 118361.500 | 107268.000 | 107390.833 | 96543.000-118361.500 |
| POST tickets / p99_ms | 105954.800 | 121326.200 | 120601.200 | 115960.733 | 105954.800-121326.200 |
| POST tickets / completions_per_minute | 11.333 | 10.867 | 11.467 | 11.222 | 10.867-11.467 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| POST tickets / pending_at_window_end | 20.000 | 25.000 | 12.000 | 19.000 | 12.000-25.000 |
| GET search / p50_ms | 18289.000 | 29570.000 | 65491.000 | 37783.333 | 18289.000-65491.000 |
| GET search / p95_ms | 85199.200 | 90583.900 | 99712.400 | 91831.833 | 85199.200-99712.400 |
| GET search / p99_ms | 95760.000 | 105869.160 | 108440.080 | 103356.413 | 95760.000-108440.080 |
| GET search / completions_per_minute | 2.400 | 2.267 | 2.200 | 2.289 | 2.200-2.400 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / pending_at_window_end | 2.000 | 1.000 | 4.000 | 2.333 | 1.000-4.000 |
| GET stats / p50_ms | 9726.000 | 32106.000 | 10068.000 | 17300.000 | 9726.000-32106.000 |
| GET stats / p95_ms | 53412.250 | 70304.000 | 103137.300 | 75617.850 | 53412.250-103137.300 |
| GET stats / p99_ms | 64109.650 | 74428.800 | 105517.860 | 81352.103 | 64109.650-105517.860 |
| GET stats / completions_per_minute | 0.667 | 0.600 | 0.533 | 0.600 | 0.533-0.667 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / pending_at_window_end | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

PERF-01, PERF-02 and PERF-04 fail in every repetition: POST completion throughput below 11.88/min, POST p95 above 10s and p99 above 20s, read p95 above 5s. PERF-03 numeric error threshold passes; every client request eventually succeeds.

All 762 whole-run requests reconcile by ID, endpoint, status and model. Each service log includes one preflight GET /stats. No duplicate IDs or JMeter WARN/ERROR entries.

Measured POSTs outstanding at the window cutoff: 20, 25, 12. Window completions also include 9, 5, 3 warm-up POSTs respectively. Late drain completions are excluded from sustained throughput but included in measured-arrival latency. Eventual success does not establish capacity at the offered arrival rate.

Only 8-10 measured stats requests per repetition; tail precision is limited. No per-run CPU observation files supplied. Sources: normal-llama3-r1 through normal-llama3-r3 analysis.json, JTL and service logs.
