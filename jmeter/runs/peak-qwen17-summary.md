# Qwen 1.7B peak-load results

Ten-minute measurement windows after two-minute warm-up. All-attempt linear-interpolated percentiles include failed requests; values near 300s are censored by the client response timeout.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 206498.000 | 200767.500 | 215713.500 | 207659.667 | 200767.500-215713.500 |
| POST tickets / p95_ms | 300010.000 | 300009.050 | 300009.850 | 300009.633 | 300009.050-300010.000 |
| POST tickets / p99_ms | 300016.330 | 300015.000 | 300013.370 | 300014.900 | 300013.370-300016.330 |
| POST tickets / completions_per_minute | 22.200 | 20.800 | 21.200 | 21.400 | 20.800-22.200 |
| POST tickets / error_percent | 25.815 | 36.944 | 33.242 | 32.000 | 25.815-36.944 |
| GET search / p50_ms | 165087.000 | 196477.000 | 221108.000 | 194224.000 | 165087.000-221108.000 |
| GET search / p95_ms | 300007.000 | 300012.000 | 300009.400 | 300009.467 | 300007.000-300012.000 |
| GET search / p99_ms | 300010.560 | 300013.280 | 300010.840 | 300011.560 | 300010.560-300013.280 |
| GET search / completions_per_minute | 5.400 | 4.700 | 4.400 | 4.833 | 4.400-5.400 |
| GET search / error_percent | 17.808 | 21.918 | 38.356 | 26.027 | 17.808-38.356 |
| GET stats / p50_ms | 179393.000 | 212650.000 | 138391.500 | 176811.500 | 138391.500-212650.000 |
| GET stats / p95_ms | 288370.000 | 300005.000 | 291353.000 | 293242.667 | 288370.000-300005.000 |
| GET stats / p99_ms | 297679.600 | 300005.000 | 298275.400 | 298653.333 | 297679.600-300005.000 |
| GET stats / completions_per_minute | 1.700 | 1.100 | 1.400 | 1.400 | 1.100-1.700 |
| GET stats / error_percent | 10.526 | 23.529 | 22.222 | 18.759 | 10.526-23.529 |

Measured overall error rates: 23.9130%, 34.0000%, 33.6264%; mean 30.5131%, min-max 23.9130-34.0000%.

PERF-05 numeric thresholds fail in all three runs: throughput below 95% of target, POST p95 above 30s and overall error rate above 1%. Completion throughput includes warm-up carry-over; late drain completions are excluded.

1,617 whole-run attempts: 1,201 responses with real IDs reconcile, 416 client failures lack response IDs. Unmatched successful service completions agree with socket-timeout endpoint counts in aggregate, not individually. See each evidence-note.md. Do not claim full request-level reconciliation or PERF-07 satisfaction; failed-client/server mapping and no-response causes remain unresolved.

No per-run CPU observation files supplied. No JMeter WARN/ERROR entries, but JTL failures are retained. Sources: peak-qwen17-r1 through peak-qwen17-r3 analysis.json, JTL, service logs and preserved container diagnostics.
