# Workload model

## Scope

This workload model is for the Group 10 synchronous, CPU-only ticket-triage baseline. It uses public CFPB complaint volume as a scale proxy. It does not claim that the laboratory service is a production CFPB deployment.

## Public workload evidence

The CFPB received 6,635,400 complaints in 2025. More than 5.8 million, or 88%, concerned credit or consumer reporting. The annual total is a count of complaint records rather than unique consumers.

Using 365 days:

| Measure | Calculation | Result |
|---|---:|---:|
| Complaints per day | 6,635,400 / 365 | 18,179.2 |
| Complaints per hour | 18,179.2 / 24 | 757.5 |
| Complaints per minute | 757.5 / 60 | 12.62 |
| Mean inter-arrival time | 60 / 12.62 | 4.75 seconds |

The report does not provide an hour-of-day arrival curve. The peak profile below is therefore a team assumption.

## Peak and non-peak assumptions

Assume 16 active hours and eight overnight hours per day. Overnight traffic is 10% of the active-hour average. Four active hours form a peak window at twice the active-hour average. The rates are normalized so their daily total remains 18,179.2 tickets.

| Period | Hours/day | POST `/tickets` rate | Tickets/day |
|---|---:|---:|---:|
| Peak | 4 | 36.07/min | 8,656.7 |
| Normal | 12 | 12.02/min | 8,656.7 |
| Overnight | 8 | 1.80/min | 865.8 |
| Total | 24 | n.a. | 18,179.2 |

The peak multiplier is an assumption, not an observed CFPB statistic.

## Endpoint mix

No public usage ratio exists for this proposed service. Use this repeatable team assumption:

- 1.00 POST `/tickets` per complaint;
- 0.20 GET `/search` requests per complaint;
- 0.05 GET `/stats` requests per complaint.

This gives an 80% POST, 16% search, and 4% stats request mix.

| Period | POST/min | Search/min | Stats/min | Total/min |
|---|---:|---:|---:|---:|
| Peak | 36.07 | 7.21 | 1.80 | 45.09 |
| Normal | 12.02 | 2.40 | 0.60 | 15.03 |
| Overnight | 1.80 | 0.36 | 0.09 | 2.25 |

## Ticket length

The frozen 175-ticket Golden Set contains no blank narratives or duplicate row identifiers. Lengths use Unicode characters and whitespace-delimited words.

| Statistic | Characters | Words |
|---|---:|---:|
| Minimum | 207 | 39 |
| Mean | 850.8 | 151.7 |
| p50 | 709 | 124 |
| p75 | 1,218 | 218 |
| p90 | 1,732 | 297 |
| p95 | 1,871 | 330 |
| p99 | 1,983 | 348 |
| Maximum | 1,991 | 362 |

A whitespace word is not a model token. JMeter should use real Group 10 narratives rather than identical synthetic strings. If the full 1,000-ticket file becomes available, recalculate this distribution because a Golden Set chosen for category coverage may not represent the natural workload mix.

## Load configurations

Generate open-loop traffic from a separate machine. Exclude a two-minute warm-up from reported results and execute three runs per configuration.

| Configuration | Measured duration | POST/min | Search/min | Stats/min |
|---|---:|---:|---:|---:|
| Normal sustained | 15 min | 12.0 | 2.4 | 0.6 |
| Peak sustained | 10 min | 36.0 | 7.2 | 1.8 |
| Read-heavy sensitivity | 10 min | 12.0 | 4.8 | 1.2 |

Randomize narrative order using a recorded seed. Retain the seed, raw `.jtl`, matching service logs, model tag and digest, machine specifications, and Git revision.

For stress testing, start at 6 POST requests/minute and increase by 6 POST requests/minute every five minutes while preserving the 80/16/4 endpoint mix. The system limit is the highest completed step before any of these conditions occurs:

- achieved POST throughput falls below 95% of offered POST load;
- POST errors exceed 1%;
- POST p95 exceeds 30 seconds;
- the service becomes unresponsive or its backlog keeps growing after the step.

## Limitations

- The CFPB annual volume is a scale proxy, not a forecast for this prototype.
- The hourly profile and endpoint ratios are assumptions.
- Current CFPB products do not map perfectly to the assignment's seven legacy categories.
- The Golden Set length distribution may differ from the natural 1,000-ticket population.
- The single-threaded service can make GET requests wait behind model inference. Use JMeter latency as the end-to-end measure.
