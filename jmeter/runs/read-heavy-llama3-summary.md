# Llama 3B read-heavy results

Ten-minute measurement windows after two-minute warm-up. Percentiles use linear interpolation on all attempts starting in the measurement window. Successful completion throughput counts completions inside that window, including warm-up carry-over and excluding late drain completions.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 41150.500 | 29297.000 | 47389.000 | 39278.833 | 29297.000-47389.000 |
| POST tickets / p95_ms | 96124.250 | 48659.000 | 90188.000 | 78323.750 | 48659.000-96124.250 |
| POST tickets / p99_ms | 105349.500 | 56509.640 | 93113.000 | 84990.713 | 56509.640-105349.500 |
| POST tickets / completions_per_minute | 11.400 | 11.900 | 11.000 | 11.433 | 11.000-11.900 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / p50_ms | 36630.500 | 26242.500 | 46833.000 | 36568.667 | 26242.500-46833.000 |
| GET search / p95_ms | 98988.000 | 44377.700 | 86590.800 | 76652.167 | 44377.700-98988.000 |
| GET search / p99_ms | 101522.450 | 49229.760 | 92303.760 | 81018.657 | 49229.760-101522.450 |
| GET search / completions_per_minute | 4.700 | 4.600 | 4.600 | 4.633 | 4.600-4.700 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 25448.000 | 21216.500 | 22853.000 | 23172.500 | 21216.500-25448.000 |
| GET stats / p95_ms | 61069.600 | 44663.700 | 88270.500 | 64667.933 | 44663.700-88270.500 |
| GET stats / p99_ms | 89362.720 | 46294.340 | 88872.500 | 74843.187 | 46294.340-89362.720 |
| GET stats / completions_per_minute | 1.400 | 1.200 | 1.200 | 1.267 | 1.200-1.400 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

All 645 whole-run attempts succeeded and reconcile by request ID, endpoint, status and model. Each service log has one additional preflight GET /stats. There are no duplicate client IDs or JMeter WARN/ERROR entries. All recorded handlers completed before client finish.

This is a read-heavy sensitivity profile, not the normal profile used for PERF-01/02/04 acceptance. Read p95 values are elevated in every repetition; zero HTTP/assertion failures do not imply acceptable latency. Stats percentiles are based on only 13, 12 and 11 measured arrivals.

No per-run CPU observation files supplied. Sources: read-heavy-llama3-r1 through read-heavy-llama3-r3 analysis.json, JTL, JMeter logs, client finish records and service logs.
