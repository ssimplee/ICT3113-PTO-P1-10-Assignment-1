# Member 4 handoff

## Current status

Member 4 preparation is implemented, but no formal golden-set accuracy run has
been performed. This is intentional: the human-label audit and prediction freeze
must be complete first.

Prepared artifacts:

- `docs/member4-candidate-models.md`: proposed four-model shortlist and rationale.
- `docs/member4-model-manifest.json`: exact runtime, full digests and synthetic compatibility evidence.
- `predictions/prediction_record.md`: specific, falsifiable draft predictions.
- `accuracy/run_accuracy.py`: guarded, resumable formal accuracy runner.
- `tests/test_accuracy_runner.py`: validation and report-generation tests.

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

## Blocking items before formal testing

1. The team must approve the currently tested service/Ollama benchmark machine,
   or repeat compatibility and pinning on the final machine. This run used 8
   Docker CPUs and 4,003,487,744 bytes of Docker memory; older smoke evidence
   reports 16 CPUs and about 8 GB, so those results are not directly comparable.
2. Review, mark and commit the prediction record as frozen before any formal run.

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
