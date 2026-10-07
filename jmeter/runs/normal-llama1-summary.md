# Llama 1B normal-load results

Three repetitions; two-minute warm-up excluded. Percentiles use linear interpolation on all measured arrivals.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 2266.000 | 2376.000 | 2209.000 | 2283.667 | 2209.000-2376.000 |
| POST tickets / p95_ms | 6013.000 | 5540.600 | 7999.000 | 6517.533 | 5540.600-7999.000 |
| POST tickets / p99_ms | 6305.800 | 6700.260 | 10772.200 | 7926.087 | 6305.800-10772.200 |
| POST tickets / completions_per_minute | 12.067 | 12.200 | 12.200 | 12.156 | 12.067-12.200 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / p50_ms | 33.000 | 45.000 | 62.000 | 46.667 | 33.000-62.000 |
| GET search / p95_ms | 3577.400 | 5611.400 | 2945.800 | 4044.867 | 2945.800-5611.400 |
| GET search / p99_ms | 4493.240 | 5741.280 | 4060.840 | 4765.120 | 4060.840-5741.280 |
| GET search / completions_per_minute | 2.467 | 2.333 | 2.467 | 2.422 | 2.333-2.467 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / p50_ms | 25.000 | 2176.000 | 133.000 | 778.000 | 25.000-2176.000 |
| GET stats / p95_ms | 2718.650 | 2818.600 | 4090.350 | 3209.200 | 2718.650-4090.350 |
| GET stats / p99_ms | 2755.730 | 2830.120 | 4605.270 | 3397.040 | 2755.730-4605.270 |
| GET stats / completions_per_minute | 0.667 | 0.600 | 0.533 | 0.600 | 0.533-0.667 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |

PERF-01, PERF-02 and PERF-03 meet their numeric thresholds in all three runs. PERF-04 FAILS: search p95 in run 2 was 5.6114 seconds against a 5-second limit. A passing mean does not override a failed repetition. Peak and stress are not evaluated here.

All 762 client request IDs match service records, with no duplicate IDs or status/endpoint/model mismatch. Each run has one additional preflight GET /stats. All client attempts succeeded and no JMeter WARN/ERROR entries were found.

Run 3 has 181 POST arrivals in the measurement window and 183 successful completions: two warm-up requests finished after the measurement window began. The completion throughput (12.2/min) includes these two; measured-arrival completion throughput is 181/15 = 12.0667/min. Both exceed the required target. No measured arrivals remained pending at the window end.

GET stats has only 8-10 measured samples per run; tail percentiles have limited precision. CPU-only observation was retained for run 1; no separate ollama-ps.txt was supplied for runs 2 and 3. Historical accuracy results used different hardware. This comparison does not override the failed accuracy requirements.

Sources: normal-llama1-r1/analysis.json, normal-llama1-r2/analysis.json, normal-llama1-r3/analysis.json and their retained JTL/service logs.
