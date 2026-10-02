# Member 4 handoff

## Current status

Member 4's candidate selection and formal golden-set accuracy work are complete.
All four frozen candidates were tested against all 175 tickets through the real
service API. The full comparison and classification-error analysis are in
`accuracy/results/README.md`; machine-readable results and per-model evidence are
retained below `accuracy/results/`.

Prepared artifacts:

- `docs/member4-candidate-models.md`: proposed four-model shortlist and rationale.
- `docs/member4-model-manifest.json`: exact runtime, full digests and synthetic compatibility evidence.
- `predictions/prediction_record.md`: frozen, pre-benchmark falsifiable predictions.
- `accuracy/run_accuracy.py`: guarded, resumable formal accuracy runner.
- `tests/test_accuracy_runner.py`: validation and report-generation tests.
- `accuracy/results/model-comparison.csv`: cross-model measured results.
- `accuracy/results/README.md`: accuracy, latency, confusion and error analysis.

## Accuracy runner outputs

For each model/run directory the runner creates:

- `manifest.json`: Git revisions, input hash, exact tag/digest and timing metadata;
- `raw_predictions.jsonl`: append-only per-request evidence suitable for resume;
- `predictions.csv`: expected/predicted labels, correctness, request ID and latency;
- `summary.json`: overall and valid-response accuracy plus latency diagnostics;
- `per_category.csv`: per-category totals, errors and accuracy;
- `confusion_matrix.csv`: all seven predicted categories plus an error bucket.

The default command validates inputs only and sends nothing. A formal run also
requires `--confirm-formal-run`, a full local `sha256:` model digest and a Git
commit containing byte-identical copies of both the frozen prediction record and
golden CSV. The prediction record must say `**Status:** FROZEN`.

Example validation-only command:

```powershell
python accuracy/run_accuracy.py `
  --model-tag 'qwen3:0.6b-q4_K_M' `
  --model-digest 'sha256:REPLACE_WITH_64_HEX_CHARACTERS' `
  --output-dir 'accuracy/results/validation-only'
```

## Formal result and recommendation

| Exact tag | Overall accuracy | Errors | Median | p95 |
|---|---:|---:|---:|---:|
| `qwen3:0.6b-q4_K_M` | 20.00% | 0 | 3.80 s | 9.90 s |
| `llama3.2:1b-instruct-q4_K_M` | 37.71% | 0 | 8.11 s | 18.92 s |
| `qwen3:1.7b-q4_K_M` | 35.43% | 0 | 9.10 s | 22.11 s |
| `llama3.2:3b-instruct-q4_K_M` | 52.57% | 10 | 72.48 s | 114.42 s |

Llama 3.2 3B is the accuracy winner but not an operational recommendation: ten
of its 175 requests exceeded the service's 120-second Ollama timeout. Llama 3.2
1B is the provisional balanced candidate because it ranked second in accuracy,
had no request errors, and was roughly nine times faster at the median. Member 5
must use controlled JMeter load and stress evidence before the team makes its
final selection.

## Completed pre-label runtime work

- Docker Desktop is running and the Compose service/Ollama containers build and start.
- Four accepted exact tags are pulled, fully digested and compatible through `/tickets`.
- CPU-only execution was observed for every accepted candidate.
- The proposed 4B Qwen candidate was rejected after cold and warm HTTP 504 timeouts;
  the 1B Llama replacement passed. Evidence is retained in the model manifest.
- Four synthetic tickets were stored. They are development diagnostics and must
  not be included in formal accuracy, load or stress results.
- Git commit `957e43b` completes the two missing labels. The independent audit
  validator reconciles all 175 workbook rows with the golden CSV and calculates
  54.29% raw agreement and Cohen's kappa of 0.4629.

Member 5 should use the same exact tags, full digests, host, Docker configuration
and frozen Git revision for JMeter load/stress testing so the accuracy and
performance results describe the same candidates.
