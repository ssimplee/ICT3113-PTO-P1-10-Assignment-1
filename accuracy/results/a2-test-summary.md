# Assignment 2 test-set accuracy results

6 configurations, each run once through `POST /tickets` with `accuracy/run_accuracy.py` on the 79 test-set tickets in `golden-set/split/golden_test_even_rows.csv`. Runs started 2026-11-19T12:02:46Z and finished 2026-11-19T12:27:36Z (UTC).

Every percentage uses all tickets in the group as its denominator, so a request error would count as a wrong answer. Counts are shown next to every percentage.

## 1. Overall accuracy and the overall limit

| Configuration | Correct of 79 | Accuracy | Wrong | Overall limit (at least 42 of 79) | Source |
|---|---:|---:|---:|---|---|
| Llama 3B alone | 49 | 62.0% | 30 | reference | `accuracy/results/a2-test-llama3.2-3b/summary.json` |
| Llama 1B alone | 30 | 38.0% | 49 | below | `accuracy/results/a2-test-llama3.2-1b/summary.json` |
| Qwen 1.7B alone | 28 | 35.4% | 51 | below | `accuracy/results/a2-test-qwen3-1.7b/summary.json` |
| Qwen 0.6B alone | 16 | 20.3% | 63 | below | `accuracy/results/a2-test-qwen3-0.6b/summary.json` |
| Cascade, Setting A (T = 223) | 46 | 58.2% | 33 | meets | `accuracy/results/a2-test-cascade-a/summary.json` |
| Cascade, Setting B (T = 142) | 44 | 55.7% | 35 | meets | `accuracy/results/a2-test-cascade-b/summary.json` |

**Overall limit.** Llama 3B scored 49 of 79 (62.0%) on the test set. The limit is 62.0% minus 10 points = 52.0%, which a configuration meets with 42 or more correct of 79 (53.2%); 41 of 79 is 51.9%.

Source: `correct` and `overall_accuracy` in each `summary.json`, recomputed from the `predicted`, `expected` and `status` columns of each `predictions.csv`.

## 2. Per-category accuracy and the per-category limits

Each cell is correct answers of the tickets in that category. The limit is Llama 3B's accuracy in the category minus 15 points; **bold** marks a cell below its limit.

| Category | Tickets | Llama 3B alone | Llama 1B alone | Qwen 1.7B alone | Qwen 0.6B alone | Cascade, Setting A (T = 223) | Cascade, Setting B (T = 142) | Limit (Llama 3B minus 15 points) | Fewest correct that meets it |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Credit reporting | 16 | 16 (100.0%) | 16 (100.0%) | 16 (100.0%) | **0 (0.0%)** | 16 (100.0%) | 16 (100.0%) | 85.0% | 14 of 16 |
| Debt collection † | 8 | 6 (75.0%) | **2 (25.0%)** | **3 (37.5%)** | **0 (0.0%)** | 5 (62.5%) | **4 (50.0%)** | 60.0% | 5 of 8 |
| Mortgage | 10 | 5 (50.0%) | 6 (60.0%) | **3 (30.0%)** | **0 (0.0%)** | 6 (60.0%) | 6 (60.0%) | 35.0% | 4 of 10 |
| Credit card † | 9 | 1 (11.1%) | 0 (0.0%) | 1 (11.1%) | 1 (11.1%) | 0 (0.0%) | 0 (0.0%) | -3.9% (cannot be missed) | 0 of 9 |
| Bank account or service | 14 | 13 (92.9%) | **2 (14.3%)** | **4 (28.6%)** | 14 (100.0%) | 13 (92.9%) | 12 (85.7%) | 77.9% | 11 of 14 |
| Consumer loan | 13 | 8 (61.5%) | **4 (30.8%)** | **1 (7.7%)** | **1 (7.7%)** | **6 (46.2%)** | **6 (46.2%)** | 46.5% | 7 of 13 |
| Money transfer or service † | 9 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | -15.0% (cannot be missed) | 0 of 9 |
| All tickets | 79 | 49 (62.0%) | 30 (38.0%) | 28 (35.4%) | 16 (20.3%) | 46 (58.2%) | 44 (55.7%) | 52.0% (minus 10 points) | 42 of 79 |

† **Fewer than 10 tickets:** Debt collection (8 tickets, one ticket is 12.5 points); Credit card (9 tickets, one ticket is 11.1 points); Money transfer or service (9 tickets, one ticket is 11.1 points). One ticket moves each of these by more than 10 points, so the 15-point limit there turns on one or two tickets and is not a fair test on its own.

Source: `total` and `correct` in each `per_category.csv` (the same figures are in `summary.json` under `per_category`). The full confusion matrix for each configuration is in its `confusion_matrix.csv`.

## 3. Which configurations pass both limits

| Configuration | Overall limit | Per-category limit | Categories below their limit | Passes both |
|---|---|---|---|---|
| Llama 3B alone | reference | reference | – | reference (sets the limits) |
| Llama 1B alone | below (30 < 42) | below in 3 of 7 | Debt collection: 2 of 8, 50.0 points below Llama 3B, needs 5 †; Bank account or service: 2 of 14, 78.6 points below Llama 3B, needs 11; Consumer loan: 4 of 13, 30.8 points below Llama 3B, needs 7 | No |
| Qwen 1.7B alone | below (28 < 42) | below in 4 of 7 | Debt collection: 3 of 8, 37.5 points below Llama 3B, needs 5 †; Mortgage: 3 of 10, 20.0 points below Llama 3B, needs 4; Bank account or service: 4 of 14, 64.3 points below Llama 3B, needs 11; Consumer loan: 1 of 13, 53.8 points below Llama 3B, needs 7 | No |
| Qwen 0.6B alone | below (16 < 42) | below in 4 of 7 | Credit reporting: 0 of 16, 100.0 points below Llama 3B, needs 14; Debt collection: 0 of 8, 75.0 points below Llama 3B, needs 5 †; Mortgage: 0 of 10, 50.0 points below Llama 3B, needs 4; Consumer loan: 1 of 13, 53.8 points below Llama 3B, needs 7 | No |
| Cascade, Setting A (T = 223) | meets (46 ≥ 42) | below in 1 of 7 | Consumer loan: 6 of 13, 15.4 points below Llama 3B, needs 7 | No |
| Cascade, Setting B (T = 142) | meets (44 ≥ 42) | below in 2 of 7 | Debt collection: 4 of 8, 25.0 points below Llama 3B, needs 5 †; Consumer loan: 6 of 13, 15.4 points below Llama 3B, needs 7 | No |

**Pass both limits:** Llama 3B alone (the reference); no other configuration.

- Cascade, Setting A (T = 223) meets the overall limit and misses the per-category limit in: Consumer loan (6 of 13, 1 short of the 7 needed).
- Cascade, Setting B (T = 142) meets the overall limit and misses the per-category limit in: Debt collection (4 of 8, 1 short of the 5 needed), Consumer loan (6 of 13, 1 short of the 7 needed).

† Category with fewer than 10 tickets (see section 2).

Source: sections 1 and 2.

## 4. Cascade: tickets escalated, and accuracy of each group

| Configuration | Tickets answered (status 201) | Escalated to Llama 3B | Not escalated (Llama 1B's answer kept) | Escalated: correct | Not escalated: correct | All: correct |
|---|---:|---:|---:|---:|---:|---:|
| Cascade, Setting A (T = 223) | 79 | 53 of 79 (67.1%) | 26 of 79 (32.9%) | 31 of 53 (58.5%) | 15 of 26 (57.7%) | 46 of 79 (58.2%) |
| Cascade, Setting B (T = 142) | 79 | 41 of 79 (51.9%) | 38 of 79 (48.1%) | 25 of 41 (61.0%) | 19 of 38 (50.0%) | 44 of 79 (55.7%) |

`final_model` on the same lines:

| Configuration | `final_model` = `llama3.2:1b-instruct-q4_K_M` | `final_model` = `llama3.2:3b-instruct-q4_K_M` |
|---|---:|---:|
| Cascade, Setting A (T = 223) | 26 | 53 |
| Cascade, Setting B (T = 142) | 38 | 41 |

Every escalated line has `first_category` = `Credit reporting` and `narrative_words` at or below T, and every other line does not, so the logged decisions match the frozen rule. On every ticket the cascade's answer is the same category the answering model gave in its own single-model run (Llama 3B if escalated, Llama 1B if not).

Source: `escalated` and `final_model` on the `POST /tickets` lines with status 201 in each `service-logs/requests.jsonl`, joined to `predictions.csv` on `request_id` (all 79 request IDs matched in both cascades). Both models were loaded after each run: `ollama-ps-after-run.txt` in each cascade folder.

## 5. Request errors and timeouts

| Configuration | Tickets sent | Status 201 | Other status or no response | Timeouts | Tickets stored in the run's database | Source |
|---|---:|---:|---:|---:|---:|---|
| Llama 3B alone | 79 | 79 | 0 | 0 | 79 | `accuracy/results/a2-test-llama3.2-3b/predictions.csv`, `service-logs/requests.jsonl`, `service-data/tickets.sqlite3` |
| Llama 1B alone | 79 | 79 | 0 | 0 | 79 | `accuracy/results/a2-test-llama3.2-1b/predictions.csv`, `service-logs/requests.jsonl`, `service-data/tickets.sqlite3` |
| Qwen 1.7B alone | 79 | 79 | 0 | 0 | 79 | `accuracy/results/a2-test-qwen3-1.7b/predictions.csv`, `service-logs/requests.jsonl`, `service-data/tickets.sqlite3` |
| Qwen 0.6B alone | 79 | 79 | 0 | 0 | 79 | `accuracy/results/a2-test-qwen3-0.6b/predictions.csv`, `service-logs/requests.jsonl`, `service-data/tickets.sqlite3` |
| Cascade, Setting A (T = 223) | 79 | 79 | 0 | 0 | 79 | `accuracy/results/a2-test-cascade-a/predictions.csv`, `service-logs/requests.jsonl`, `service-data/tickets.sqlite3` |
| Cascade, Setting B (T = 142) | 79 | 79 | 0 | 0 | 79 | `accuracy/results/a2-test-cascade-b/predictions.csv`, `service-logs/requests.jsonl`, `service-data/tickets.sqlite3` |

No configuration had a request error or timeout: every ticket returned status 201 in `predictions.csv`, and each service log has 79 `POST /tickets` lines, all status 201.

## 6. Run record

| Configuration | Output directory | `model_tag` in `manifest.json` | `model_digest` in `manifest.json` | Started (UTC) | Finished (UTC) |
|---|---|---|---|---|---|
| Llama 3B alone | `accuracy/results/a2-test-llama3.2-3b` | `llama3.2:3b-instruct-q4_K_M` | `sha256:a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72` | 2026-11-19T12:02:46.407802Z | 2026-11-19T12:08:54.952002Z |
| Llama 1B alone | `accuracy/results/a2-test-llama3.2-1b` | `llama3.2:1b-instruct-q4_K_M` | `sha256:22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02` | 2026-11-19T12:09:18.932120Z | 2026-11-19T12:11:37.762328Z |
| Qwen 1.7B alone | `accuracy/results/a2-test-qwen3-1.7b` | `qwen3:1.7b-q4_K_M` | `sha256:8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7` | 2026-11-19T12:11:56.198858Z | 2026-11-19T12:15:13.377279Z |
| Qwen 0.6B alone | `accuracy/results/a2-test-qwen3-0.6b` | `qwen3:0.6b-q4_K_M` | `sha256:7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435` | 2026-11-19T12:15:30.919874Z | 2026-11-19T12:17:04.222013Z |
| Cascade, Setting A (T = 223) | `accuracy/results/a2-test-cascade-a` | `cascade[small=llama3.2:1b-instruct-q4_K_M;large=llama3.2:3b-instruct-q4_K_M;min_words=223]` | `sha256:22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02` | 2026-11-19T12:17:24.908547Z | 2026-11-19T12:23:00.094105Z |
| Cascade, Setting B (T = 142) | `accuracy/results/a2-test-cascade-b` | `cascade[small=llama3.2:1b-instruct-q4_K_M;large=llama3.2:3b-instruct-q4_K_M;min_words=142]` | `sha256:22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02` | 2026-11-19T12:23:21.140432Z | 2026-11-19T12:27:36.341093Z |

- Repository HEAD for every run: `560eb5508351383cd27e6af2f2b3c6774f8067e9`.
- Frozen prediction commit checked by the runner: `67297532b0de647745d83f398e0b262b646603da`.
- Golden CSV SHA-256: `d1632a30c54637d11119226f6795133d416c98773a9cff296308c748a47fd6c7`.

## 7. How the runs were made

- Before each run the Ollama container was restarted (same container and settings: Ollama 0.11.11, `OLLAMA_NUM_PARALLEL=1`) so that no model was loaded at the start. The service container was then recreated from the unchanged image with `OLLAMA_TIMEOUT_SECONDS=120`, bound to `127.0.0.1:18000`, with new empty `service-data` and `service-logs` folders inside the output directory.
- The digests Ollama reported for the models were checked against `docs/member4-model-manifest.json` before each run. For the cascades, `model_digest` in `manifest.json` is the small model's digest; the large model's digest is in `large-model-digest.txt` in the same folder.
- Each service log has 81 lines: two `GET /stats` lines (a check before the run that the database was empty and the configuration label was the expected one, then the runner's own check), followed by the 79 `POST /tickets` lines.
- The service was stopped after each run so that nothing else is appended to that run's log or database.
- Each configuration was run once and no run needed `--resume`. The first attempt to start the service for the Llama 3B run failed because Docker could not bind port 18000; the service did not start and no ticket was sent. The Llama 3B run was then started once.
