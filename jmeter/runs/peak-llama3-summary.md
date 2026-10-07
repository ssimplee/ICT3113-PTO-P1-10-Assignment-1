# Llama 3B peak-load results

Ten-minute measurement windows after two-minute warm-up. All-attempt linear-interpolated percentiles include failed requests; values near 300s are censored by the client response timeout.

| Endpoint / metric | Run 1 | Run 2 | Run 3 | Mean | Min-max |
|---|---:|---:|---:|---:|---:|
| POST tickets / p50_ms | 244835.500 | 284065.500 | 224425.500 | 251108.833 | 224425.500-284065.500 |
| POST tickets / p95_ms | 300011.650 | 300013.000 | 300013.000 | 300012.550 | 300011.650-300013.000 |
| POST tickets / p99_ms | 300015.330 | 300017.410 | 300016.000 | 300016.247 | 300015.330-300017.410 |
| POST tickets / completions_per_minute | 6.900 | 7.100 | 6.900 | 6.967 | 6.900-7.100 |
| POST tickets / error_percent | 94.293 | 93.611 | 92.582 | 93.495 | 92.582-94.293 |
| GET search / p50_ms | 274275.000 | 300006.000 | 300005.000 | 291428.667 | 274275.000-300006.000 |
| GET search / p95_ms | 300013.000 | 300013.000 | 300012.400 | 300012.800 | 300012.400-300013.000 |
| GET search / p99_ms | 300016.520 | 300014.000 | 300021.280 | 300017.267 | 300014.000-300021.280 |
| GET search / completions_per_minute | 1.900 | 1.900 | 1.600 | 1.800 | 1.600-1.900 |
| GET search / error_percent | 87.671 | 91.781 | 95.890 | 91.781 | 87.671-95.890 |
| GET stats / p50_ms | 134778.000 | 135077.000 | 202146.500 | 157333.833 | 134778.000-202146.500 |
| GET stats / p95_ms | 300008.400 | 300011.400 | 300011.650 | 300010.483 | 300008.400-300011.650 |
| GET stats / p99_ms | 300011.280 | 300012.680 | 300019.130 | 300014.363 | 300011.280-300019.130 |
| GET stats / completions_per_minute | 0.500 | 0.500 | 0.700 | 0.567 | 0.500-0.700 |
| GET stats / error_percent | 84.211 | 88.235 | 72.222 | 81.556 | 72.222-88.235 |

Measured overall error rates: 92.8261%, 93.1111%, 92.3077%; mean 92.7483%, min-max 92.3077-93.1111%.

PERF-05 numeric thresholds fail in every repetition: POST completion throughput is below 34.2/min (95% of the 36/min target), POST p95 exceeds 30s and overall errors exceed 1%. Completion throughput includes successful warm-up carry-over; late drain completions are excluded.

1,617 whole-run attempts: 351 responses with real IDs reconcile; 1,266 client failures lack response IDs. The 639 socket timeouts match unmatched successful service completions by endpoint count in aggregate, not individually. The 627 no-response failures lack matched server entries. Full request-level reconciliation and PERF-07 satisfaction are not established. See each evidence-note.md.

The last recorded server completions occurred 167.313, 179.205 and 91.539 seconds after client finish respectively. The backlog was allowed to finish before recreating the service. These late server completions do not erase client failures or increase measured client throughput.

No per-run CPU observation files supplied. JMeter logs contain no WARN/ERROR entries, but JTL failures are retained. Sources: peak-llama3-r1 through peak-llama3-r3 analysis.json, JTL, service logs and preserved container diagnostics.
