# Performance and accuracy requirements

## Measurement rules

Test each candidate using its frozen Ollama tag and digest, the same prompt and inference settings, the same workload data, fixed machine resources, and a recorded Git revision. Use JMeter client elapsed time for latency.

Report p50, p95, p99, achieved throughput, and error rate. Run each formal configuration three times. A model passes only when every run passes. Exclude the two-minute warm-up. Count timeouts, connection failures, HTTP 5xx responses, and invalid classifications as errors.

## Performance requirements

| ID | Requirement |
|---|---|
| PERF-01 | Under 12.0 POST `/tickets`, 2.4 GET `/search`, and 0.6 GET `/stats` requests per minute for 15 minutes, the system shall achieve at least 99% of offered POST throughput in all three runs. |
| PERF-02 | Under PERF-01, POST `/tickets` shall have p95 latency at most 10 seconds and p99 at most 20 seconds in all three runs. |
| PERF-03 | Under PERF-01, the total HTTP error rate shall be below 1.0% in all three runs. |
| PERF-04 | Under PERF-01, GET `/search` and GET `/stats` shall each have p95 latency at most 5 seconds in all three runs. |
| PERF-05 | Under 36.0 POST, 7.2 search, and 1.8 stats requests per minute for 10 minutes, the system shall achieve at least 95% of offered throughput, keep errors below 1.0%, and keep POST p95 at most 30 seconds in all three runs. |
| PERF-06 | The stress test shall identify the highest five-minute step at which achieved POST throughput is at least 95%, POST errors are at most 1%, and POST p95 is at most 30 seconds. |
| PERF-07 | Every reported run shall retain its raw JMeter `.jtl` and matching service logs without unexplained missing requests. |

The response-time thresholds are team service targets, not CFPB-published values. If no candidate passes the workload-derived peak requirement, report that result rather than weakening the requirement after testing.

## Accuracy requirements

| ID | Requirement |
|---|---|
| ACC-01 | On the frozen 175-ticket Golden Set, a model shall achieve at least 80% overall accuracy: at least 140 correct predictions. |
| ACC-02 | A model shall achieve at least 70% accuracy in each of the seven categories. |
| ACC-03 | All 175 responses shall contain exactly one allowed category. Empty, malformed, multiple, or unsupported outputs count as incorrect and as invalid-output errors. |
| ACC-04 | Testing shall not expose Golden labels in the prompt or change labels after observing model predictions. |

Minimum correct predictions for ACC-02 under the frozen final-label distribution:

| Category | Tickets | Minimum correct |
|---|---:|---:|
| Bank account or service | 29 | 21 |
| Consumer loan | 21 | 15 |
| Credit card | 22 | 16 |
| Credit reporting | 39 | 28 |
| Debt collection | 18 | 13 |
| Money transfer or service | 23 | 17 |
| Mortgage | 23 | 17 |

Report overall accuracy, per-category accuracy, the confusion matrix, invalid-output count, and classification error analysis.

## Recommendation rule

A model is eligible for recommendation only if it passes ACC-01 through ACC-04. Among eligible models, prefer the one that passes all normal-load requirements and the most peak/stress requirements. If none passes everything, report each shortfall and recommend the closest fit with a specific Assignment 2 optimisation direction.

## Benchmark readiness

The Golden Set was frozen in Git commit `abe7e5e`. Formal benchmarking may proceed once the candidate-model list and prediction record are also frozen. The audit workbook contains final labels for all 175 tickets.
