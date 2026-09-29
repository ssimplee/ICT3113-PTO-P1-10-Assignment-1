# ICT3113 Assignment 1 — Group 10 Golden Test Set Labelling Protocol

## 1. Purpose

This protocol defines how Group 10 will manually label the golden test set for ICT3113 Assignment 1.

The golden test set will be used as the reference truth when measuring the classification accuracy of the candidate Ollama models.

The original `source_label` in the provided dataset must not be treated as the final ground truth because the assignment states that the source labels are noisy.

## 2. Dataset Scope

Group 10 uses dataset rows **10000 to 10999**.

Only tickets from this allocated range should be used for golden-set construction, labelling, accuracy testing, and load-test traffic.

## 3. Golden Test Set Size

Target size: **175 tickets**

Recommended sampling approach:
- randomly select approximately 25 tickets from each of the seven `source_label` groups;
- use `source_label` only to obtain broad category coverage;
- do not show `source_label` to annotators while they label.

The seven categories are:
1. Credit reporting
2. Debt collection
3. Mortgage
4. Credit card
5. Bank account or service
6. Consumer loan
7. Money transfer or service

## 4. Independent Labelling

Two team members must label every selected ticket independently.

For Group 10:
- **Annotator A:** Member 2
- **Annotator B:** Member 3

Rules:
- both annotators receive the same 175 narratives;
- annotators must not see each other's labels during first-pass labelling;
- annotators must not discuss individual tickets before both first-pass label sheets are complete;
- annotators should not be shown the original `source_label`;
- annotators should not use Ollama or another model to decide a label;
- each ticket must receive exactly one category.

## 5. General Labelling Principle

Read the complete narrative and identify the **main financial product or service involved in the consumer's primary complaint**.

When more than one issue or product appears:
1. identify the main problem the consumer is complaining about;
2. identify which product or service that problem belongs to;
3. assign the category that best represents that main problem;
4. do not choose a category merely because it is mentioned somewhere in the narrative.

If the case is unclear, assign the best-supported category and mark confidence as `Low`.

## 6. Category Definitions

These are Group 10's operational rules for consistent labelling.

### 6.1 Credit reporting

Choose **Credit reporting** when the main complaint concerns information appearing in, missing from, or being handled in a consumer's credit report or credit history.

Typical indicators:
- incorrect credit-report information;
- accounts that do not belong to the consumer;
- disputes with credit bureaus or reporting agencies;
- information not corrected after a dispute;
- incorrect payment/account-status reporting.

Do not choose this category merely because another financial problem affected the consumer's credit score.

### 6.2 Debt collection

Choose **Debt collection** when the main complaint concerns attempts to collect a debt.

Typical indicators:
- collection calls or messages;
- debt collector behaviour;
- attempts to collect a disputed debt;
- attempts to collect a debt the consumer says is not theirs;
- collection notices or threats.

Use the original product category instead when the main complaint is about the product itself rather than collection activity.

### 6.3 Mortgage

Choose **Mortgage** when the main complaint concerns a mortgage or home loan.

Typical indicators:
- mortgage repayments;
- mortgage servicing;
- foreclosure;
- escrow;
- loan modification;
- refinancing;
- mortgage fees.

### 6.4 Credit card

Choose **Credit card** when the main complaint concerns a credit-card account or credit-card transaction.

Typical indicators:
- unauthorised or disputed card transactions;
- billing;
- fees or interest;
- credit limits;
- card account closure;
- card payment processing.

**Credit card vs Debt collection**
- issue is with the card account, charges, billing, or fees → **Credit card**
- issue is with collection of an unpaid card debt → **Debt collection**

### 6.5 Bank account or service

Choose **Bank account or service** when the main complaint concerns a bank account or ordinary banking service.

Typical indicators:
- checking or savings account;
- deposits or withdrawals;
- account fees;
- account closure or freezing;
- overdraft;
- access to funds;
- account servicing.

**Bank account vs Money transfer**
- main problem is the bank account itself → **Bank account or service**
- main problem is sending/receiving/transferring money → **Money transfer or service**

### 6.6 Consumer loan

Choose **Consumer loan** when the main complaint concerns a non-mortgage consumer loan.

Typical indicators:
- personal loans;
- instalment loans;
- vehicle loans;
- loan repayment;
- loan interest or fees;
- loan servicing.

**Consumer loan vs Debt collection**
- issue concerns the loan itself → **Consumer loan**
- issue concerns collection activity for unpaid loan debt → **Debt collection**

### 6.7 Money transfer or service

Choose **Money transfer or service** when the main complaint concerns sending or receiving money through a transfer service.

Typical indicators:
- failed transfers;
- delayed transfers;
- missing transferred funds;
- transfer cancellation;
- remittance;
- recipient not receiving funds;
- transfer fees.

## 7. Edge Cases

### More than one category appears

Choose the category representing the consumer's **main complaint**.

### Credit reporting appears only as a consequence

Do not automatically choose Credit reporting because the consumer mentions that something affected their credit score.

Choose Credit reporting only when the reporting itself is the main issue.

### Debt is mentioned but no collection activity occurs

Do not choose Debt collection merely because money is owed.

### Ambiguous narrative

If two categories seem similarly plausible:
1. reread the full narrative;
2. identify what the consumer wants corrected;
3. choose the category most directly connected to that issue;
4. mark confidence as `Low`;
5. write a short note.

Do not discuss the case with the other annotator until both first-pass label sheets are complete.

## 8. Annotation File Format

Recommended columns:

```text
row,narrative,label,confidence,notes
```

Allowed `label` values:
- Credit reporting
- Debt collection
- Mortgage
- Credit card
- Bank account or service
- Consumer loan
- Money transfer or service

Allowed `confidence` values:
- High
- Medium
- Low

## 9. Confidence Guidance

**High:** clearly fits one category.

**Medium:** another category is mentioned, but the main complaint is still reasonably clear.

**Low:** two categories are plausible, the narrative is vague, or important information is missing.

## 10. Comparing Annotators

After both annotators complete all 175 tickets:
1. combine the two label sheets;
2. compare the labels;
3. mark each ticket as `Agreement` or `Disagreement`;
4. keep the original label sheets unchanged;
5. calculate agreement before resolving disagreements.

Recommended statistics:
- raw percentage agreement;
- Cohen's kappa.

## 11. Disagreement Resolution

For every disagreement:
1. both annotators reread the ticket;
2. each explains the reason for the original label;
3. consult this protocol;
4. agree on one final label;
5. record the final label and reason;
6. update the protocol if the disagreement revealed an unclear rule.

Recommended columns:

```text
row,annotator_A_label,annotator_B_label,final_label,resolution_reason,protocol_updated
```

A third member may be consulted if the two annotators cannot agree, but this is optional.

## 12. Protocol Revisions

Do not silently edit the protocol.

Record revisions, for example:

```text
Version 1.0
Initial protocol before labelling.

Version 1.1
Added clarification for Credit card vs Debt collection after disagreements.
```

## 13. Final Golden Set

After all disagreements are resolved, create:

```text
golden_final.csv
```

Recommended columns:

```text
row,narrative,golden_label
```

The final label must come from the team's human labelling process, not from the original `source_label`.

## 14. Freezing the Golden Set

Before the first formal benchmark run:
- complete all independent labelling;
- calculate agreement;
- resolve every disagreement;
- finalise protocol revisions;
- create `golden_final.csv`;
- commit the golden set and protocol to Git.

Suggested commit message:

```text
Freeze Group 10 golden test set before benchmarking
```

After this commit, do not change golden labels simply because a model predicts something different.

## 15. Revision History

| Version | Description | Date |
|---|---|---|
| 1.0 | Initial protocol created before independent labelling | TBD |
