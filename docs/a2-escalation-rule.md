# Assignment 2 escalation rule

**Status:** FROZEN

Frozen on 15 November 2026, before any Assignment 2 test-set or speed run. The
rule and both settings were chosen from the 96 tuning tickets only
(`golden-set/split/golden_tuning_odd_rows.csv`, odd row numbers).

## Cascade

| Stage | Exact Ollama tag | Digest |
|---|---|---|
| Small model, answers every ticket | `llama3.2:1b-instruct-q4_K_M` | `sha256:22bc6b92eb0160c4629782fca05a9032c59d306ab2058b7dacc8a4644fbafa02` |
| Large model, answers escalated tickets | `llama3.2:3b-instruct-q4_K_M` | `sha256:a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72` |

Both models use the unchanged Assignment 1 classification prompt and inference
settings. Both stay loaded together on the test machine; the `ollama ps`
evidence is in `logs/a2-memory-check/`.

## The rule

For each ticket sent to `POST /tickets`:

1. The small model classifies the ticket.
2. Count the ticket's words: the number of whitespace-separated pieces of the
   narrative exactly as received (Python `len(narrative.split())`).
3. If the small model's category is anything other than `Credit reporting`,
   that category is final.
4. If the small model's category is `Credit reporting` and the ticket has more
   than T words, `Credit reporting` is final.
5. Otherwise (the category is `Credit reporting` and the ticket has T words or
   fewer), the large model classifies the same ticket and its category is final.

```text
first = small_model(narrative)
if first != "Credit reporting" or word_count(narrative) > T:
    return first
return large_model(narrative)
```

The rule uses only the small model's category and the word count. It adds no
model call beyond the escalation itself, so a ticket costs one or two calls.

If either model call fails or returns an invalid category, the request fails
with the Assignment 1 error response and no ticket is stored. An escalated
ticket never falls back to the small model's answer.

## Settings tested

| Setting | T | How T was fixed |
|---|---:|---|
| A | 223 words | Upper quartile of tuning-set length: 72 of the 96 tuning tickets have 223 words or fewer |
| B | 142 words | Median of tuning-set length: 48 of the 96 tuning tickets have 142 words or fewer |

T is a fixed quantile of ticket length, not a cut-off searched for the best
accuracy. Setting A escalates more tickets than Setting B.

## Why this rule

All figures below are from the tuning runs in `accuracy/results/a2-tuning-*`,
made on the Assignment 2 test machine.

**Llama 1B is the small model.** Qwen 0.6B's answers were too poor to accept
(14 of its 80 `Bank account or service` answers were correct, against 37 for
Llama 3B on the same tickets). Qwen 1.7B was no more accurate than Llama 1B
(34 against 36 of 96) and about 40% slower.

**Llama 1B's answer is reliable except when it says `Credit reporting`.**

| Llama 1B answered | Tickets | Llama 1B correct | Llama 3B correct on the same tickets |
|---|---:|---:|---:|
| Any category except `Credit reporting` | 23 | 16 | 12 |
| `Credit reporting` | 73 | 20 | 35 |

Accepting only the first group keeps accuracy (51 of 96) but escalates 76% of
tickets, which is about 16% slower than Llama 3B alone. A second condition is
needed to accept some `Credit reporting` answers.

**Short tickets are the ones worth escalating.** Llama 3B's time grows with
ticket length, but its advantage over Llama 1B is largest on short tickets.

| Words | Tickets | Llama 1B mean time | Llama 3B mean time | Llama 1B correct | Llama 3B correct |
|---|---:|---:|---:|---:|---:|
| 43–97 | 24 | 1.2 s | 2.8 s | 9 | 15 |
| 105–142 | 24 | 1.7 s | 4.3 s | 12 | 11 |
| 144–223 | 24 | 2.5 s | 6.3 s | 9 | 11 |
| 230–362 | 23 | 3.6 s | 9.3 s | 6 | 10 |

Among the 73 `Credit reporting` answers at the median length, escalating a
short ticket costs 3.5 s of Llama 3B time on average and a long one 8.2 s,
while Llama 3B corrects a larger share of the short ones (20 against 11 correct
of 36) than of the long ones (15 against 9 of 37). The rule therefore escalates
short tickets and keeps the small model's answer on long ones. This is the
opposite direction to a "long tickets go to the large model" rule; that
direction, at the same median cut-off, was only 7% faster than Llama 3B alone
and scored 42 of 96.

## Expected trade-off on the tuning set

| Configuration | Escalated | Correct of 96 | Not escalated: correct | Escalated: correct | Estimated mean time | Estimated median time |
|---|---:|---:|---:|---:|---:|---:|
| Llama 3B alone | – | 47 (49.0%) | – | – | 5.6 s | 4.9 s |
| Llama 1B alone | – | 36 (37.5%) | – | – | 2.2 s | 1.9 s |
| Cascade, Setting A (T = 223) | 52 (54.2%) | 48 (50.0%) | 21 of 44 | 27 of 52 | 4.6 s (19% lower than 3B) | 4.0 s |
| Cascade, Setting B (T = 142) | 36 (37.5%) | 45 (46.9%) | 25 of 60 | 20 of 36 | 3.5 s (37% lower than 3B) | 3.3 s |

Correct answers per category on the tuning set:

| Category | Tickets | Llama 3B | Llama 1B | Setting A | Setting B |
|---|---:|---:|---:|---:|---:|
| Credit reporting | 23 | 22 | 20 | 20 | 20 |
| Debt collection | 10 | 5 | 2 | 4 | 3 |
| Mortgage | 13 | 5 | 5 | 7 | 6 |
| Credit card | 13 | 3 | 0 | 3 | 3 |
| Bank account or service | 15 | 7 | 4 | 8 | 8 |
| Consumer loan | 8 | 3 | 2 | 3 | 2 |
| Money transfer or service | 14 | 2 | 3 | 3 | 3 |

Against tuning-set stand-ins for the limits (Llama 3B minus 10 points overall,
minus 15 points per category), Setting A meets all of them. Setting B meets the
overall one and misses Debt collection by one ticket (3 of 10, needing 4).

Times are estimates, not measurements under load. A ticket's cascade time is
its Llama 1B time plus, if escalated, its Llama 3B time, taken from the
sequential tuning runs. The first ticket of each run is excluded because it
includes model loading.

## Wrong answers that slip through

The rule accepts a wrong small-model answer in two ways:

- **A wrong category other than `Credit reporting`:** 7 of the 23 such answers
  on the tuning set.
- **A wrong `Credit reporting` answer on a long ticket:** 16 of 21 at Setting A
  and 28 of 37 at Setting B. Llama 3B would also have been wrong on most of
  these (13 of 21 and 22 of 37).

## Alternatives considered

| Approach | Tuning-set result | Decision |
|---|---|---|
| Category only (accept everything except `Credit reporting`) | 51 of 96, 76% escalated, about 16% slower than Llama 3B alone | Rejected: slower than the top model |
| Long tickets to the large model | 42 of 96, 39% escalated, about 7% faster | Rejected: escalates the most expensive tickets |
| Agreement between Llama 1B and Qwen 1.7B | 38 of 96, 30% escalated, about 27% slower | Rejected: two small calls cost 5.4 s before any escalation |
| Self-reported confidence | Not tested | Rejected: needs a second model call per ticket, because the classification prompt cannot change |

## Configuration and logging

The cascade runs inside `POST /tickets` (`service/app/__init__.py`).

| Setting | Value for the cascade |
|---|---|
| `OLLAMA_MODEL` | `llama3.2:1b-instruct-q4_K_M` |
| `CASCADE_LARGE_MODEL` | `llama3.2:3b-instruct-q4_K_M` |
| `CASCADE_MIN_WORDS` | `223` for Setting A, `142` for Setting B |

Leaving `CASCADE_LARGE_MODEL` empty runs `OLLAMA_MODEL` alone, as in
Assignment 1.

The response and the stored ticket carry one fixed label for the whole
configuration, for example
`cascade[small=llama3.2:1b-instruct-q4_K_M;large=llama3.2:3b-instruct-q4_K_M;min_words=223]`,
so a caller cannot tell which model answered a ticket.

Each `POST /tickets` line in the request log records:

| Field | Meaning |
|---|---|
| `narrative_words` | Word count used by the rule |
| `first_category` | The small model's category |
| `escalated` | `true` if the ticket was passed to the large model |
| `final_model` | Tag of the model whose category was returned |
| `first_model_ms`, `second_model_ms` | Time spent in each model call |

The escalation fraction of a run is the number of `POST /tickets` lines with
status 201 and `escalated` true, divided by all `POST /tickets` lines with
status 201.

## Limits of this evidence

- The tuning set has 96 tickets and some categories have 8 to 10, so one ticket
  moves a category by 10 points or more.
- The rule was tuned on these tickets. The test set may behave differently.
- The escalation fraction depends on ticket length, so it will differ between
  the accuracy test and the speed-test workload.
