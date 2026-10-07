# Qwen 0.6B read-heavy sensitivity results

Ten-minute measurement windows, excluding two-minute warm-up. Percentiles use linear interpolation on all measured arrivals.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 1485.000 | 1447.000 | 1432.000 | 1454.667 | 1432.000-1485.000 |
| POST tickets / p95_ms | 3264.750 | 4262.400 | 3366.000 | 3631.050 | 3264.750-4262.400 |
| POST tickets / p99_ms | 4299.750 | 4931.280 | 4692.400 | 4641.143 | 4299.750-4931.280 |
| POST tickets / completions_per_minute | 12.600 | 12.500 | 12.100 | 12.400 | 12.100-12.600 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / p50_ms | 30.500 | 31.000 | 33.000 | 31.500 | 30.500-33.000 |
| GET search / p95_ms | 1826.450 | 2462.350 | 2145.000 | 2144.600 | 1826.450-2462.350 |
| GET search / p99_ms | 2455.630 | 3899.230 | 3423.160 | 3259.340 | 2455.630-3899.230 |
| GET search / completions_per_minute | 4.800 | 5.000 | 4.900 | 4.900 | 4.800-5.000 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 23.000 | 50.500 | 23.000 | 32.167 | 23.000-50.500 |
| GET stats / p95_ms | 2128.600 | 4257.100 | 2535.500 | 2973.733 | 2128.600-4257.100 |
| GET stats / p99_ms | 2526.520 | 4740.220 | 2924.700 | 3397.147 | 2526.520-4740.220 |
| GET stats / completions_per_minute | 1.300 | 1.200 | 1.100 | 1.200 | 1.100-1.300 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

All 645 whole-run requests succeeded and reconcile by request ID, endpoint, status and model. No duplicates or JMeter WARN/ERROR entries. Each service log contains one additional preflight GET /stats. No measured requests remained pending at the window end.

Read-heavy is a sensitivity condition, not the prescribed normal-load requirement condition. All p95 values here are below the corresponding normal-load reference thresholds. Only 11-13 measured stats requests per repetition; tail estimates have limited precision.

All nine Qwen 0.6B load runs are complete. Normal and peak numeric performance requirements passed across their three repetitions, but the existing accuracy failure still prevents a compliant deployment recommendation. No per-run CPU observation files were supplied for these repetitions.

Sources: read-heavy-qwen06-r1 through read-heavy-qwen06-r3 analysis.json, JTL and matching service logs.
