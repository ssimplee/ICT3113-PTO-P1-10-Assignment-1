# Group 10 prediction record

**Status:** FROZEN

Frozen on 1 October 2026 before the first formal accuracy, load or stress run.
The predictions below were not changed after the synthetic compatibility checks.
No golden-set model output existed when this record was frozen. The benchmark
environment and full candidate digests are pinned in
`docs/member4-model-manifest.json`; the golden CSV SHA-256 is
`2faa7a5f22414ad1bf62872c2bb1c5adb1a9badaa41c02c9d50ef81c6119fc13`.

## Proposed candidates

| Exact proposed Ollama tag | Parameters | Quantisation | Prediction: overall accuracy | Prediction: warm single-request latency |
|---|---:|---|---:|---:|
| `qwen3:0.6b-q4_K_M` | 0.6B | Q4_K_M | 45% | 2.5 s |
| `llama3.2:1b-instruct-q4_K_M` | 1B | Q4_K_M | 50% | 3.5 s |
| `qwen3:1.7b-q4_K_M` | 1.7B | Q4_K_M | 58% | 5.0 s |
| `llama3.2:3b-instruct-q4_K_M` | 3B | Q4_K_M | 64% | 8.0 s |

The latency values are deliberately falsifiable point predictions, not measured
results. They assume CPU-only inference, a warm loaded model, the current
sequential service, one request in flight and the recorded 4 GB Docker allocation
on the 8 GB host. They must be reviewed if another service host is selected.
Cold model-load time is excluded and must be reported separately if observed.

## Bottleneck prediction

Ollama CPU inference will be the first capacity bottleneck. The Flask service
handles classification synchronously and sequentially, and Ollama is configured
with `OLLAMA_NUM_PARALLEL=1`. SQLite writes and the HTTP/JSON work are expected to
be negligible compared with model inference. Once the arrival rate approaches
the reciprocal of model service time, requests will queue and tail latency will
rise faster than achieved throughput. Larger candidates should reach that point
at lower arrival rates.

## Expected difficult categories

1. **Credit reporting versus Debt collection.** Many narratives mention both a
   collector and damage to a credit report; the correct label depends on the
   primary requested remedy.
2. **Credit card versus Bank account or service.** Both can describe disputed
   transactions, fees and account access, so the product type must dominate.
3. **Consumer loan versus Mortgage.** Both concern lending, repayment and
   servicing; mortgage-specific property context may be indirect or absent.

Smaller models are expected to rely more heavily on surface keywords and
therefore make more errors in these overlapping pairs. The 3B instruction model
is expected to follow the protocol's primary-issue rule more consistently.

## Required freeze checklist

- [x] Rows 10329 and 10440 have genuine second independent human labels.
- [x] Agreement statistics and the audit workbook are corrected and committed.
- [x] The exact proposed benchmark host and Docker resource allocation are recorded.
- [x] Every candidate is pulled and its full `sha256:` digest is recorded.
- [x] All candidates pass a synthetic structured-output compatibility check.
- [x] The team approves these point predictions without using golden-set output.
- [x] Status is changed to `FROZEN` and this record plus the golden CSV are committed.

Do not revise this record after the first formal benchmark. Differences between
predictions and measurements belong in the final analysis.
