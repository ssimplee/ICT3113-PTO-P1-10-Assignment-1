# Golden-set inter-annotator agreement

## Frozen pre-adjudication agreement

The two independent label columns in
`golden_tickets_175_baseline_audit_trail.xlsx` contain 175 labels each. These
figures are calculated before using the adjudicated final label:

- Initial agreements: **95 of 175**
- Initial disagreements: **80 of 175**
- Raw percentage agreement: **54.29%**
- Chance-expected agreement: **14.89%**
- Cohen's kappa: **0.4629**

Using the common Landis-Koch descriptive bands, a kappa of 0.4629 falls in the
`moderate` range. That descriptor is only an interpretation aid; the raw counts,
percentage and exact kappa above are the primary reported evidence.

## Annotator distributions

| Category | Member 3 | Thaddeus |
|---|---:|---:|
| Bank account or service | 29 | 45 |
| Consumer loan | 21 | 20 |
| Credit card | 22 | 20 |
| Credit reporting | 40 | 30 |
| Debt collection | 17 | 31 |
| Money transfer or service | 23 | 16 |
| Mortgage | 23 | 13 |
| **Total** | **175** | **175** |

## Reproducibility and integrity checks

The workbook was pulled in Git commit `957e43b`. The validator confirms that:

- all 175 rows have both independent labels and a supported final label;
- rows 10329 and 10440 now contain genuine second labels and adjudication notes;
- 95 agreement rows and 80 disagreement rows use consistent resolution fields;
- all disagreement rows contain an adjudication reason;
- the workbook's Golden Set and Audit Trail sheets match
  `golden_tickets_175_baseline.csv` after normalising CRLF/LF line endings;
- workbook summary totals and per-category counts recompute exactly.

Run the independent standard-library validator from the repository root:

```powershell
python accuracy/validate_golden_audit.py
```

The validator exits non-zero for missing labels, unsupported categories,
duplicate IDs, inconsistent resolution records, changed narrative text, CSV /
workbook mismatches, or incorrect summary figures.
