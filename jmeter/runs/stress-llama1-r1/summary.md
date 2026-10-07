# Llama 1B stress results

| Target POST/min | Arrivals | Completions | Throughput/min | POST p95 (s) | Errors (%) | Pending at step end | Numeric limits |
|---:|---:|---:|---:|---:|---:|---:|---|
| 6 | 30 | 30 | 6.00 | 4.25 | 0.00 | 0 | PASS |
| 12 | 60 | 60 | 12.00 | 6.76 | 0.00 | 0 | PASS |
| 18 | 90 | 88 | 17.60 | 6.77 | 0.00 | 2 | PASS |
| 24 | 120 | 118 | 23.60 | 15.06 | 0.00 | 4 | PASS |
| 30 | 150 | 146 | 29.20 | 15.35 | 0.00 | 8 | PASS |
| 36 | 180 | 154 | 30.80 | 70.45 | 0.00 | 34 | FAIL |

Start-time cohorts; interpolated (n-1)*p percentiles; completion throughput includes earlier-step carry-over. Compare throughput with actual offered arrivals; also show nominal target ratio. Six finite steps do not prove indefinite stability.

Last client completion was 60.643 seconds after the arrival schedule ended.

Source: analysis.json, results.jtl, jmeter.log and service-logs/requests.jsonl in this folder.
