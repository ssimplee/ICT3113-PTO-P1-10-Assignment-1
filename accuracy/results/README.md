# Formal candidate-model accuracy results

## Result

All four frozen candidates were tested once against the same 175-ticket golden
set through the real `POST /tickets` service path. Llama 3.2 3B achieved the
highest overall accuracy, 52.57%, but returned ten HTTP 504 timeouts and was far
slower than every smaller candidate. None of the four is accurate and balanced
enough to recommend unconditionally. Member 5 must combine these findings with
repeatable load and stress results before the team selects a final model.

| Exact Ollama tag | Correct / 175 | Errors | Overall accuracy | Macro category accuracy | Median | p95 |
|---|---:|---:|---:|---:|---:|---:|
| `qwen3:0.6b-q4_K_M` | 35 | 0 | 20.00% | 18.18% | 3.80 s | 9.90 s |
| `llama3.2:1b-instruct-q4_K_M` | 66 | 0 | 37.71% | 32.09% | 8.11 s | 18.92 s |
| `qwen3:1.7b-q4_K_M` | 62 | 0 | 35.43% | 29.45% | 9.10 s | 22.11 s |
| `llama3.2:3b-instruct-q4_K_M` | 92 | 10 | 52.57% | 48.06% | 72.48 s | 114.42 s |

Overall accuracy uses all 175 tickets as its denominator, so a timeout counts as
incorrect. The 3B model's valid-response accuracy was 55.76% (92/165). “Macro”
is the unweighted mean of the seven per-category accuracies. Latencies are
client-observed sequential-request times from this accuracy run; they are useful
diagnostics, not substitutes for Member 5's JMeter measurements.

## Per-category accuracy

| Actual category (golden total) | Qwen 0.6B | Llama 1B | Qwen 1.7B | Llama 3B |
|---|---:|---:|---:|---:|
| Credit reporting (39) | 2.56% | 92.31% | 97.44% | 94.87% |
| Debt collection (18) | 0.00% | 22.22% | 33.33% | 61.11% |
| Mortgage (23) | 0.00% | 47.83% | 26.09% | 39.13% |
| Credit card (22) | 9.09% | 0.00% | 9.09% | 18.18% |
| Bank account or service (29) | 96.55% | 20.69% | 17.24% | 62.07% |
| Consumer loan (21) | 19.05% | 28.57% | 14.29% | 52.38% |
| Money transfer or service (23) | 0.00% | 13.04% | 8.70% | 8.70% |

The per-model `confusion_matrix.csv` files are the authoritative full confusion
matrices. Their `__ERROR__` column includes service failures.

## Classification error analysis

### Systematic prediction bias

- Qwen 0.6B predicted **Bank account or service** for 151/175 tickets (86.29%).
  Its 20.00% overall result is therefore largely a majority-like single-class
  strategy, not broad classification ability. Its largest routes were Credit
  reporting -> Bank account (31), Money transfer -> Bank account (23), and
  Mortgage -> Bank account (21).
- Llama 1B predicted **Credit reporting** for 134/175 tickets (76.57%). It found
  36/39 genuine Credit reporting tickets but classified every Credit card ticket
  incorrectly; 22/22 Credit card tickets became Credit reporting.
- Qwen 1.7B had the same stronger bias: 137/175 predictions (78.29%) were Credit
  reporting. Its largest routes were Bank account -> Credit reporting (21),
  Money transfer -> Credit reporting (19), and Credit card -> Credit reporting
  (18). It was slower and less accurate than Llama 1B, so greater parameter count
  did not improve this prompt/task combination.
- Llama 3B was more diverse but still predicted Credit reporting 93 times
  (53.14%). Its main semantic errors were Credit card -> Credit reporting (17),
  Consumer loan -> Credit reporting (10), and Mortgage -> Credit reporting (8).

These patterns support two conclusions. First, the frozen one-sentence prompt
provides category names but no decision rules or examples, so it does not encode
the labelling protocol's “primary issue” distinctions. Second, larger models
reduce but do not remove the tendency to fall back to Credit reporting. This is
an inference from the observed confusion matrices, not a separate prompt
experiment; changing the prompt now would require a new, explicitly versioned
benchmark rather than rewriting these frozen results.

### Timeout errors

Only Llama 3B produced service errors. Ten requests exceeded the service's
120-second Ollama timeout, at golden rows 10225, 10272, 10321, 10381, 10395,
10492, 10657, 10791, 10797 and 10814. By actual category, the timeouts were one
Credit reporting, four Mortgage, two Bank account or service, and three Money
transfer or service tickets. The model's maximum client time was 120.46 seconds,
consistent with the configured backend cutoff. The accuracy runner's 300-second
client timeout did not create these failures; it waited long enough to receive
the service's 504 response.

### Difficult categories and frozen predictions

The frozen record correctly anticipated confusion between Credit reporting and
Debt collection, Credit card and Bank account, and Consumer loan and Mortgage,
but the measured dominant fallback was broader than predicted: many categories
collapsed into Credit reporting. All four accuracy predictions were optimistic:
measured accuracy was lower by 25.00, 12.29, 22.57 and 11.43 percentage points
respectively. Median latency was also slower than predicted by 1.30, 4.61, 4.10
and 64.48 seconds respectively. The 3B miss is chiefly explained by its long
CPU-only inference and proximity to the service timeout.

## Recommendation and handoff

For accuracy alone, Llama 3.2 3B ranks first. It is not the operational winner:
its 5.71% request-error rate and extreme latency create a serious performance
risk. Llama 3.2 1B is the current balanced candidate because it ranks second in
accuracy, has no request errors, and is about nine times faster at the median
than Llama 3B. This is a provisional recommendation for Member 5 to test, not the
team's final model selection.

Member 5 should run the frozen JMeter plan on at least Llama 1B and Llama 3B,
using the exact tags and digests in `docs/member4-model-manifest.json`. Testing
all four retains the strongest size/family comparison if time permits. Do not
rerun or overwrite these directories when changing prompts, timeouts, hardware,
or resource limits; create a new dated result set and document the changed
condition.

## Reproducibility and retained evidence

- Frozen prediction commit: `7af35aecf95ba9f8b737c48e4512ff2b9bedeb81`
- Runner Git revision: `e5cd01769a6dea923d53fcfc081be7da63ea86c2`
- Golden CSV SHA-256:
  `2faa7a5f22414ad1bf62872c2bb1c5adb1a9badaa41c02c9d50ef81c6119fc13`
- Environment: 8 Docker CPUs, 4,003,487,744 bytes Docker memory, CPU-only,
  Ollama 0.11.11, `OLLAMA_NUM_PARALLEL=1`, and sequential service requests.
- Run directories use Singapore date 1 October 2026. Manifest timestamps are
  UTC, so their start times appear under 30 September 2026.

Each model directory retains its manifest, raw JSONL, predictions, per-category
CSV, confusion matrix, summary, service log and isolated SQLite database. The
machine-readable cross-model table is `model-comparison.csv`.
