# Qwen 0.6B peak-load results

Ten-minute measurement windows after two-minute warm-up. All measured-arrival latencies use linear-interpolated percentiles; throughput counts successful completions inside the window.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 3272.500 | 3384.000 | 3624.000 | 3426.833 | 3272.500-3624.000 |
| POST tickets / p95_ms | 8151.400 | 8495.650 | 10363.800 | 9003.617 | 8151.400-10363.800 |
| POST tickets / p99_ms | 11422.520 | 15675.070 | 13378.650 | 13492.080 | 11422.520-15675.070 |
| POST tickets / completions_per_minute | 36.700 | 36.000 | 36.600 | 36.433 | 36.000-36.700 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| POST tickets / pending_at_window_end | 1.000 | 0.000 | 1.000 | 0.667 | 0.000-1.000 |
| GET search / p50_ms | 2060.000 | 1887.000 | 2462.000 | 2136.333 | 1887.000-2462.000 |
| GET search / p95_ms | 6112.800 | 10855.600 | 8386.200 | 8451.533 | 6112.800-10855.600 |
| GET search / p99_ms | 10478.800 | 14640.840 | 13728.000 | 12949.213 | 10478.800-14640.840 |
| GET search / completions_per_minute | 7.300 | 7.300 | 7.300 | 7.300 | 7.300-7.300 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / pending_at_window_end | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 402.000 | 2702.000 | 2313.000 | 1805.667 | 402.000-2702.000 |
| GET stats / p95_ms | 4536.000 | 7011.400 | 6118.750 | 5888.717 | 4536.000-7011.400 |
| GET stats / p99_ms | 5025.600 | 11582.280 | 6598.150 | 7735.343 | 5025.600-11582.280 |
| GET stats / completions_per_minute | 1.900 | 1.700 | 1.900 | 1.833 | 1.700-1.900 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / pending_at_window_end | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

PERF-05 numeric thresholds pass in all three runs: POST throughput exceeds 34.2/min, mixed throughput exceeds 42.75/min, errors are below 1%, and POST p95 is below 30s. Throughput also exceeds 95% of actual offered starts. The normal-load 5s read-latency requirement is not applied to this peak configuration.

All 1,617 requests succeeded and reconcile by ID, endpoint, status and model. No duplicate client IDs or JMeter WARN/ERROR entries. Each service log has one additional preflight GET /stats.

Run 3 POST completions include three warm-up carry-over requests; one measured POST finishes in drain (364 arrivals, 366 window completions). Run 3 stats includes one warm-up carry-over completion. Run 1 also has one measured POST finishing in drain. These are retained, not dropped from latency statistics.

No per-run CPU observation files were supplied for these repetitions. Passing performance does not override the failed accuracy requirements. Sources: peak-qwen06-r1 through peak-qwen06-r3 analysis.json, JTL and matching service logs.
