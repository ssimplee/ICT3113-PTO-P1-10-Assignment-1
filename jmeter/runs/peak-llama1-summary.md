# Llama 1B peak-load results

Two-minute warm-up excluded; ten-minute measurement windows. Linear-interpolated latency percentiles of all measured arrivals, including eventual drain outcomes.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 54846.500 | 61404.500 | 75624.000 | 63958.333 | 54846.500-75624.000 |
| POST tickets / p95_ms | 121417.900 | 142301.050 | 122770.100 | 128829.683 | 121417.900-142301.050 |
| POST tickets / p99_ms | 123721.950 | 146431.540 | 125028.360 | 131727.283 | 123721.950-146431.540 |
| POST tickets / completions_per_minute | 30.400 | 29.900 | 30.900 | 30.400 | 29.900-30.900 |
| POST tickets / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| POST tickets / pending_at_window_end | 67.000 | 77.000 | 64.000 | 69.333 | 64.000-77.000 |
| GET search / p50_ms | 51723.000 | 51526.000 | 81737.000 | 61662.000 | 51526.000-81737.000 |
| GET search / p95_ms | 108322.400 | 141461.800 | 118973.400 | 122919.200 | 108322.400-141461.800 |
| GET search / p99_ms | 121713.880 | 145655.960 | 123349.560 | 130239.800 | 121713.880-145655.960 |
| GET search / completions_per_minute | 6.500 | 6.400 | 6.600 | 6.500 | 6.400-6.600 |
| GET search / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET search / pending_at_window_end | 8.000 | 13.000 | 12.000 | 11.000 | 8.000-13.000 |
| GET stats / p50_ms | 50983.000 | 48376.000 | 57754.500 | 52371.167 | 48376.000-57754.500 |
| GET stats / p95_ms | 93659.600 | 124909.200 | 117692.500 | 112087.100 | 93659.600-124909.200 |
| GET stats / p99_ms | 111217.520 | 132253.840 | 123044.100 | 122171.820 | 111217.520-132253.840 |
| GET stats / completions_per_minute | 1.800 | 1.500 | 1.700 | 1.667 | 1.500-1.800 |
| GET stats / error_percent | 0.000 | 0.000 | 0.000 | 0.000 | 0.000-0.000 |
| GET stats / pending_at_window_end | 1.000 | 3.000 | 2.000 | 2.000 | 1.000-3.000 |

PERF-05 FAILS in all three repetitions: POST p95 exceeds 30 seconds; POST completion throughput is below 34.2/min (95% of the 36/min target). All-endpoint completion throughput is also below 42.75/min (95% of the 45/min mixed target). Error rate is zero. Actual attempted arrival counts vary with the seeded random schedules; POST throughput also falls below 95% of actual measured offered arrivals in every repetition.

All 1,617 client requests reconcile exactly with service request IDs, status, endpoint and model. Each run has one additional preflight GET /stats. No JMeter WARN/ERROR entries. Outstanding measured POSTs at the measurement cutoff: 67, 77, 64; all eventually complete during drain.

Window completion counts include warm-up carry-over. They must not be confused with eventual success of measured arrivals. Observed buildup and high read latency are consistent with head-of-line blocking in the synchronous single-handler baseline; this is a diagnosis to supplement with resource observations, not proof of CPU saturation alone.

Evidence: peak-llama1-r1 through peak-llama1-r3 analysis.json, JTL and matching service logs. No per-run ollama-ps.txt was supplied for these peak repetitions.
