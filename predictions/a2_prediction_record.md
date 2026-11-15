# Group 10 Assignment 2 prediction record

**Status:** FROZEN

Frozen on 15 November 2026, before any Assignment 2 test-set or speed run. No
test-set ticket had been sent to any model on the Assignment 2 machine when
this record was frozen, and the top model's test-set accuracy, which sets the
limits, had not been measured.

## What was known at the freeze

- The Assignment 1 results for all four models on the full golden set, run on
  the earlier 4 GB host.
- The Assignment 2 tuning runs: all four models on the 96 tuning tickets, on
  the test machine (`accuracy/results/a2-tuning-*`).
- The escalation rule and its two settings (`docs/a2-escalation-rule.md`), with
  cascade figures simulated from those tuning runs.

Configurations: each of the four models alone, and one cascade
(`llama3.2:1b-instruct-q4_K_M` then `llama3.2:3b-instruct-q4_K_M`) at Setting A
(T = 223 words) and Setting B (T = 142 words).

## 1. Fastest configuration within the accuracy limits

**Prediction: the cascade at Setting A.**

- Setting A will pass the overall limit and every per-category limit, and will
  be faster than Llama 3B alone. On the tuning set it scored one ticket more
  than Llama 3B and its estimated mean time was 19% lower.
- Setting B will be the fastest configuration tested but will not qualify. It
  will pass the overall limit and fail the per-category limit in Debt
  collection, as it did by one ticket against the tuning-set stand-in.
- No small model alone will pass. Llama 1B, Qwen 1.7B and Qwen 0.6B will each
  fall more than 10 points below Llama 3B on the test set.

## 2. Accuracy test on the 79 test tickets

| Configuration | Overall accuracy | Tickets escalated |
|---|---:|---:|
| Llama 3B alone | 62% (49 of 79) | – |
| Llama 1B alone | 38% (30 of 79) | – |
| Qwen 1.7B alone | 35% (28 of 79) | – |
| Qwen 0.6B alone | 20% (16 of 79) | – |
| Cascade, Setting A | 59% (47 of 79) | 53% (42 of 79) |
| Cascade, Setting B | 54% (43 of 79) | 38% (30 of 79) |

- The overall limit will therefore be about 52%.
- The cascade will lose more accuracy against Llama 3B on the test set than it
  did on the tuning set (about 3 points at Setting A and 8 at Setting B), because
  the Assignment 1 results show a wider gap between Llama 1B and Llama 3B on
  the even rows than the tuning runs show on the odd rows.
- At both settings the escalated tickets will score higher than the tickets
  that were not escalated.
- No accuracy run will produce a request error or timeout on this machine.

## 3. Speed test

S, the middle of three warm Llama 3B timings, will be about 5 seconds. That
gives one ticket every 10 seconds (6 per minute) and 5-minute runs of about 30
tickets, well below the Assignment 1 peak rate of 36 per minute.

| Configuration | p50 latency, mean of three runs | Against Llama 3B alone | Tickets escalated |
|---|---:|---:|---:|
| Llama 3B alone | 5.5 s | – | – |
| Cascade, Setting A | 4.3 s | about 20% lower | 45% |
| Cascade, Setting B | 3.5 s | about 35% lower | 30% |

- The escalation fraction under load will be lower than in the accuracy test,
  because the speed-test workload deliberately includes long tickets and the
  rule does not escalate long tickets.
- Every run will complete with no errors and no unfinished requests.
- Both models will stay loaded throughout every cascade run.

## 4. Categories expected to lose the most accuracy

When the small model's answer is accepted, the loss against Llama 3B is
expected to be, largest first:

1. **Debt collection.** Llama 1B labels most of these tickets `Credit
   reporting` (2 of 10 correct on the tuning set, against 5 for Llama 3B), and
   long debt-collection narratives that mention a credit report are accepted
   unescalated. Expected loss: one ticket at Setting A and two at Setting B, of
   the 8 test tickets.
2. **Credit reporting.** Llama 3B is almost always right here, so every
   credit-reporting ticket that Llama 1B gives another category is a loss.
   Expected loss: one or two of the 16 test tickets at both settings.
3. **Consumer loan.** Expected loss: one of the 13 test tickets at Setting B,
   none at Setting A.

Mortgage, Bank account or service, and Money transfer or service are expected
to hold or gain a ticket. Credit card is expected to stay poor and unchanged,
because both models misclassify most of it.

## Freeze rule

Do not revise this record after the first Assignment 2 benchmark run.
Differences between these predictions and the measurements belong in the final
analysis.
