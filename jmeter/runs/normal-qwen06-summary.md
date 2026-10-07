# Qwen 0.6B normal-load results

Three repetitions; two-minute warm-up excluded. Latency uses all measured arrivals and linear-interpolated percentiles.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 1361.000 | 1304.000 | 1262.000 | 1309.000 | 1262.000-1361.000 |
| POST tickets / p95_ms | 3195.000 | 3189.700 | 3929.000 | 3437.900 | 3189.700-3929.000 |
| POST tickets / p99_ms | 3725.400 | 3582.500 | 5197.400 | 4168.433 | 3582.500-5197.400 |
| POST tickets / completions_per_minute | 12.067 | 12.200 | 12.133 | 12.133 | 12.067-12.200 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / p50_ms | 33.000 | 36.000 | 33.000 | 34.000 | 33.000-36.000 |
| GET search / p95_ms | 1830.600 | 2897.500 | 1095.000 | 1941.033 | 1095.000-2897.500 |
| GET search / p99_ms | 2677.640 | 3324.020 | 1919.480 | 2640.380 | 1919.480-3324.020 |
| GET search / completions_per_minute | 2.467 | 2.333 | 2.467 | 2.422 | 2.333-2.467 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 31.000 | 27.000 | 26.000 | 28.000 | 26.000-31.000 |
| GET stats / p95_ms | 1362.500 | 1438.800 | 1349.950 | 1383.750 | 1349.950-1438.800 |
| GET stats / p99_ms | 1726.100 | 1463.760 | 1518.790 | 1569.550 | 1463.760-1726.100 |
| GET stats / completions_per_minute | 0.667 | 0.600 | 0.533 | 0.600 | 0.533-0.667 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

PERF-01 through PERF-04 meet their numeric thresholds in all three repetitions. All 762 client requests succeeded and reconcile with service IDs, endpoint, status and model. Each log has one additional preflight GET /stats; no JMeter WARN/ERROR entries or duplicate client IDs were found.

Run 3 includes one warm-up POST completion inside the measured window: 181 measured POST arrivals versus 182 window completions. Arrival-cohort throughput is 12.0667/min, still above the required threshold. No measured requests remained pending at the window end.

Only 8-10 measured stats requests per repetition; tail percentiles have limited precision. No per-run CPU observation files were supplied for these repetitions. Passing normal-load performance does not override the model's failed accuracy requirements; peak and read-heavy testing remain separate.

Sources: normal-qwen06-r1 through normal-qwen06-r3 analysis.json, JTL and corresponding service logs.
