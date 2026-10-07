# Qwen 1.7B read-heavy sensitivity results

Ten-minute windows after two-minute warm-up; interpolated percentiles include all measured arrivals.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 4031.000 | 3631.000 | 3498.000 | 3720.000 | 3498.000-4031.000 |
| POST tickets / p95_ms | 9153.500 | 11987.000 | 10619.000 | 10586.500 | 9153.500-11987.000 |
| POST tickets / p99_ms | 12281.500 | 14365.280 | 14044.600 | 13563.793 | 12281.500-14365.280 |
| POST tickets / completions_per_minute | 12.600 | 12.400 | 12.200 | 12.400 | 12.200-12.600 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / p50_ms | 33.000 | 38.000 | 1243.000 | 438.000 | 33.000-1243.000 |
| GET search / p95_ms | 5501.650 | 7841.350 | 7642.800 | 6995.267 | 5501.650-7841.350 |
| GET search / p99_ms | 10175.860 | 10381.370 | 10233.960 | 10263.730 | 10175.860-10381.370 |
| GET search / completions_per_minute | 4.800 | 5.000 | 4.900 | 4.900 | 4.800-5.000 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 1278.000 | 1001.000 | 32.000 | 770.333 | 32.000-1278.000 |
| GET stats / p95_ms | 6473.200 | 10859.000 | 7736.000 | 8356.067 | 6473.200-10859.000 |
| GET stats / p99_ms | 8178.640 | 11211.000 | 8520.800 | 9303.480 | 8178.640-11211.000 |
| GET stats / completions_per_minute | 1.300 | 1.200 | 1.100 | 1.200 | 1.100-1.300 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

All 645 whole-run requests succeed and reconcile with service logs. Each service log includes one preflight GET /stats. No duplicate client IDs or JMeter WARN/ERROR entries.

Read-heavy is a sensitivity configuration, not the prescribed normal-load requirement condition. Search and stats p95 exceed the normal-load 5s reference in all three runs. POST p95 exceeds the 10s reference in runs 2 and 3. Stats cohorts contain only 11-13 samples, limiting tail precision.

Run 2 has two measured POSTs finish in drain and one warm-up completion inside the window. Run 3 includes one warm-up POST completion. Do not equate window completion counts with measured arrival cohort counts.

All nine Qwen 1.7B load runs are completed. Normal latency and peak requirements fail. Peak failed-request reconciliation remains incomplete as documented in the peak evidence notes. No per-run CPU observation files supplied for these read-heavy repetitions.

Sources: read-heavy-qwen17-r1 through read-heavy-qwen17-r3 analysis.json, JTL and service logs.
