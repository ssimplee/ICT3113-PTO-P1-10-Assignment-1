# Llama 1B read-heavy sensitivity results

Ten-minute measurement windows, excluding two-minute warm-up. This configuration is a sensitivity test, not the load condition specified by PERF-01 through PERF-04.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 2216.000 | 2290.000 | 2291.000 | 2265.667 | 2216.000-2291.000 |
| POST tickets / p95_ms | 5237.250 | 7557.600 | 6210.000 | 6334.950 | 5237.250-7557.600 |
| POST tickets / p99_ms | 6654.250 | 9317.640 | 7797.800 | 7923.230 | 6654.250-9317.640 |
| POST tickets / completions_per_minute | 12.600 | 12.600 | 12.200 | 12.467 | 12.200-12.600 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| POST tickets / pending_at_window_end | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / p50_ms | 37.000 | 36.000 | 53.000 | 42.000 | 36.000-53.000 |
| GET search / p95_ms | 3040.450 | 3986.800 | 4221.600 | 3749.617 | 3040.450-4221.600 |
| GET search / p99_ms | 4006.310 | 5854.040 | 6102.240 | 5320.863 | 4006.310-6102.240 |
| GET search / completions_per_minute | 4.800 | 5.000 | 4.900 | 4.900 | 4.800-5.000 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / pending_at_window_end | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 22.000 | 134.500 | 24.000 | 60.167 | 22.000-134.500 |
| GET stats / p95_ms | 2790.600 | 6942.500 | 4222.000 | 4651.700 | 2790.600-6942.500 |
| GET stats / p99_ms | 3042.120 | 7210.900 | 4295.600 | 4849.540 | 3042.120-7210.900 |
| GET stats / completions_per_minute | 1.300 | 1.200 | 1.100 | 1.200 | 1.100-1.300 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / pending_at_window_end | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

All 645 client attempts succeeded and reconcile with service request IDs, endpoint, status and model. No duplicate client IDs or JMeter WARN/ERROR entries. No measured arrivals remained pending at the window end.

Stats p95 was 6.9425 seconds in run 2, above the normal-load 5-second reference. This is sensitivity evidence, not a separate formal PERF-04 failure under its prescribed load. Only 11-13 measured stats samples per repetition; tail estimates have limited precision.

POST completion throughput includes one warm-up carry-over completion in runs 2 and 3. Measured-arrival cohorts contain 126, 125 and 121 POSTs respectively; window completions are 126, 126 and 122.

Each service log includes a preflight GET /stats. Run 1 also includes a later GET /stats at 2026-10-07 09:06:10 SGT, outside the measured period; its origin is not established from these files. It is excluded from results. No per-run CPU observation files were supplied for these repetitions.

Sources: read-heavy-llama1-r1 through read-heavy-llama1-r3 analysis.json, JTL and matching service logs.
