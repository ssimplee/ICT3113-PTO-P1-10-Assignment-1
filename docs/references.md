# Workload references

## External sources

1. Consumer Financial Protection Bureau. 2025 Consumer Response Annual Report [Internet]. Washington (DC): Consumer Financial Protection Bureau; 2026 Mar 31 [cited 2026 Sep 30]. Available from: https://www.consumerfinance.gov/data-research/research-reports/2025-consumer-response-annual-report/

2. Consumer Financial Protection Bureau. Consumer Response Annual Report: January 1-December 31, 2025 [Internet]. Washington (DC): Consumer Financial Protection Bureau; 2026 Mar [cited 2026 Sep 30]. 83 p. Available from: https://files.consumerfinance.gov/f/documents/cfpb_2025-cr-annual-report_2026-03.pdf

3. Consumer Financial Protection Bureau. Consumer Complaint Database [Internet]. Washington (DC): Consumer Financial Protection Bureau; [cited 2026 Sep 30]. Available from: https://www.consumerfinance.gov/data-research/consumer-complaints/

4. Consumer Financial Protection Bureau. How we share complaint data [Internet]. Washington (DC): Consumer Financial Protection Bureau; [cited 2026 Sep 30]. Available from: https://www.consumerfinance.gov/complaint/data-use/

Reference 2, particularly pages 3-7 and 16-17, is the primary source for the complaint-volume calculations. Reference 3 describes the database's coverage and limitations. Reference 4 defines the published complaint fields and publication process.

## Repository evidence

- `golden-set/golden_tickets_175_baseline.csv`: ticket-length distribution and frozen final-label counts.
- `golden-set/golden_tickets_175_baseline_audit_trail.xlsx`: annotator audit trail and final labels.
- Git commit `abe7e5e`: Golden Set freeze commit.
- `README.md` and `docs/member1-handoff.md`: baseline architecture and measurement interpretation.

## Team assumptions

These are modelling decisions, not externally sourced facts:

- 16 active hours and eight overnight hours per day;
- overnight traffic at 10% of the active-hour average;
- a four-hour peak at twice the active-hour average;
- 0.20 searches and 0.05 stats requests per ticket;
- response-time, throughput, accuracy, and error thresholds;
- warm-up, duration, and stress-step sizes.
