# ICT3113 Assignment 1 — Group 10 Project Kickoff Guide

## 1. Project Overview

**Module:** ICT3113 Performance Optimisation and Design  
**Assignment:** Assignment 1 — Performance Requirements & Testing  
**Group:** 10  
**Team Size:** 5 members  
**Submission Deadline:** Friday, 9 October 2026, 23:59

The goal of this assignment is to:

1. Build a baseline ticket triage service.
2. Construct a reliable golden test set.
3. Model the client's workload.
4. Select candidate Ollama models and define measurable requirements.
5. Perform accuracy, load, and stress testing.
6. Recommend a model based on the team's own requirements and measurements.

---

## 2. Group 10 Dataset

Group 10 uses:

**Rows 10,000 to 10,999**

This gives us exactly **1,000 complaint tickets**.

The provided dataset contains:

- `row` — ticket row identifier
- `source_label` — original source category
- `narrative` — complaint text

### Important

The `source_label` must **not** be treated as the final correct label for accuracy testing.

The assignment states that the original dataset labels are noisy. We therefore need to manually build our own **golden test set** before evaluating the models.

---

# 3. Recommended Team Split

| Member | Main Responsibility |
|---|---|
| Member 1 | Baseline Service / Docker / Ollama Integration |
| Member 2 | Golden Test Set Lead |
| Member 3 | Workload Model + Requirements |
| Member 4 | Candidate Models + Accuracy Testing |
| Member 5 | JMeter + Load / Stress Testing |

Everyone should still understand the overall workflow and help review the final results and presentation.

---

# 4. Member Responsibilities

## Member 1 — Baseline Service Lead

### Main Tasks

- Build the ticket triage service.
- Implement:
  - `POST /tickets`
  - `GET /search`
  - `GET /stats`
- Integrate the service with Ollama.
- Add local storage/database.
- Add request logging.
- Containerise the service with Docker.
- Prepare Docker Compose if needed.
- Document how to run the system.
- Help document the test environment.

### Baseline Rules

The Assignment 1 baseline should remain simple:

- synchronous classification
- sequential processing
- no caching
- no queuing
- no premature optimisation

Optimisation belongs to Assignment 2.

### Week 1 Output

- Working project skeleton
- Docker setup
- Basic endpoint implementations
- Ollama connection confirmed
- Logging format decided
- README setup instructions

---

## Member 2 — Golden Test Set Lead

### Main Tasks

- Draft the labelling protocol.
- Help select the golden-set tickets.
- Act as **Annotator A**.
- Maintain:
  - labelling protocol
  - disagreement records
  - final agreed labels
  - agreement statistic
- Prepare the golden-set evidence for the final slides.

### Recommended Golden-Set Size

Use approximately:

**175 tickets**

This gives roughly:

**25 tickets × 7 categories = 175 tickets**

This keeps the sample within the required range of 150–200 tickets.

### Important

Member 2 must label independently from Member 3.

Do not compare answers until both annotators have finished their first-pass labels.

---

## Member 3 — Workload Model + Requirements Lead

### Main Tasks

- Act as **Annotator B** for the golden set.
- Research publicly available complaint workload information.
- Estimate:
  - tickets per relevant time period
  - expected tickets per hour
  - peak vs non-peak periods
  - search request rates
  - ticket length distribution
- Record sources for every externally sourced figure.
- Clearly mark assumptions and estimates.
- Define measurable:
  - response-time requirements
  - throughput requirements
  - accuracy requirements

### Requirement Format

Requirements should be testable.

Example structure:

> Under an arrival rate of X tickets per minute, POST `/tickets` shall maintain a p95 response time of no more than Y seconds.

Avoid vague requirements such as:

> The system should be fast.

### Week 1 Output

- Workload research notes
- Initial workload assumptions
- Sources / references
- First draft of performance and accuracy requirements
- Independent golden-set labels

---

## Member 4 — Candidate Models + Accuracy Testing Lead

### Main Tasks

- Research candidate Ollama models.
- Select **3–5 candidate models**.
- Ensure models span at least **two parameter-size classes**.
- Record the exact:
  - Ollama tag
  - digest
- Explain why each candidate was selected.
- Prepare the prediction record together with the team.
- Later run accuracy testing against the golden set.
- Produce:
  - overall accuracy
  - per-category accuracy
  - confusion matrices
  - classification error analysis

### Prediction Record Must Include

Before benchmarking:

- expected bottleneck and why
- expected accuracy for each model
- expected single-request latency for each model
- categories expected to be hardest to classify and why

### Important

The prediction record must be committed **before the first benchmark run**.

---

## Member 5 — Performance Testing Lead

### Main Tasks

- Set up Apache JMeter.
- Build the JMeter test plan.
- Configure open-loop traffic.
- Use ticket narratives from Group 10's allocated rows.
- Run load tests at multiple arrival rates.
- Run three tests per configuration.
- Record:
  - p50 latency
  - p95 latency
  - p99 latency
  - achieved throughput
  - error rate
- Design one meaningful stress test.
- Identify the system limit or bottleneck.
- Keep all raw `.jtl` files.

### Important Testing Rule

The load generator and the system under test must run on **different machines**.

Example:

```text
Machine A
Service + Ollama
        ↑
        |
     Network
        |
        ↓
Machine B
JMeter
```

### Week 1 Output

Member 5 does not need to benchmark immediately.

Instead:

- install JMeter
- understand open-loop configuration
- prepare an initial test-plan skeleton
- confirm a second machine is available
- agree on result-file naming conventions

---

# 5. Golden Test Set Workflow

Members 2 and 3 will independently label the same golden-set tickets.

## Recommended Process

```text
Select ~175 tickets
        ↓
Write labelling protocol
        ↓
Member 2 labels independently
        ↓
Member 3 labels independently
        ↓
Compare labels
        ↓
Agreements → keep
        ↓
Disagreements → discuss
        ↓
Agree on final label
        ↓
Record why disagreement happened
        ↓
Update protocol if needed
        ↓
Calculate inter-annotator agreement
        ↓
Freeze golden set
        ↓
Commit to Git
```

### Third Reviewer

A third reviewer is **optional**, not required.

If Members 2 and 3 cannot resolve a difficult ticket, another team member can provide a third opinion.

---

# 6. Golden-Set Selection

Recommended target:

**175 tickets**

A practical approach is to sample approximately **25 tickets from each of the seven source-label groups**.

The `source_label` is only being used to help obtain broad category coverage.

It is **not** automatically accepted as the correct final label.

The seven categories are:

1. Credit reporting
2. Debt collection
3. Mortgage
4. Credit card
5. Bank account or service
6. Consumer loan
7. Money transfer or service

---

# 7. Things the Team Must Decide Before Starting

## Required First-Meeting Decisions

- [ ] Confirm everyone agrees that Group 10 uses rows 10,000–10,999.
- [ ] Confirm Member 1–5 role ownership.
- [ ] Confirm Member 2 and Member 3 as the two independent annotators.
- [ ] Agree on golden-set size.
- [ ] Agree on golden-set sampling method.
- [ ] Agree on backend technology stack.
- [ ] Confirm which machine will run the service + Ollama.
- [ ] Confirm which separate machine will run JMeter.
- [ ] Create the GitHub repository.
- [ ] Agree on Git branch / pull-request workflow.
- [ ] Agree on internal deadlines.
- [ ] Agree on log and results naming conventions.

---

# 8. Recommended Technology Stack

This is a recommendation and can be changed by the team.

## Suggested Stack

- **Backend:** Python
- **Web Framework:** FastAPI or Flask
- **Model Backend:** Ollama
- **Database:** SQLite
- **Containerisation:** Docker
- **Orchestration:** Docker Compose
- **Load Testing:** Apache JMeter
- **Version Control:** GitHub

Keep the baseline simple.

Do not add optimisation-oriented components such as:

- Redis caching
- asynchronous job queues
- load balancers
- batching systems

unless required later in Assignment 2.

---

# 9. Recommended Repository Structure

```text
ict3113-assignment1/
│
├── service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
│
├── data/
│   └── group10_tickets.csv
│
├── golden-set/
│   ├── labelling_protocol.md
│   ├── annotator_A.csv
│   ├── annotator_B.csv
│   ├── disagreements.csv
│   ├── agreement.md
│   └── golden_final.csv
│
├── predictions/
│   └── prediction_record.md
│
├── accuracy/
│   ├── scripts/
│   └── results/
│
├── jmeter/
│   ├── test-plan.jmx
│   └── results/
│
├── logs/
│
├── docs/
│   ├── workload_model.md
│   ├── requirements.md
│   └── references.md
│
└── README.md
```

---

# 10. Week 1 Parallel Work

Once the kickoff decisions are made, work can proceed in parallel.

```text
                    PROJECT KICKOFF
                          │
       ┌──────────────────┼──────────────────┐
       ↓                  ↓                  ↓
  Member 1           Members 2 + 3       Member 3
  Baseline             Golden Set         Workload
  Service              Labelling           Model
       │                  │                  │
       │                  │                  │
       ↓                  ↓                  ↓
 Working Service     Frozen Golden      Requirements
       │              Test Set             Draft
       │                  │                  │
       └───────────┬──────┴──────────┬──────┘
                   ↓                 ↓
               Member 4         Prediction
              Model Selection      Record
                   │                 │
                   └────────┬────────┘
                            ↓
                     COMMIT / FREEZE
                            ↓
                  ┌─────────┴─────────┐
                  ↓                   ↓
             Member 4            Member 5
             Accuracy            JMeter Load
              Tests              / Stress Tests
                  └─────────┬─────────┘
                            ↓
                        Analysis
                            ↓
                    Recommendation
                            ↓
                         Slides
```

---

# 11. Critical Dependency

Do **not** start the real benchmark runs too early.

Before the first benchmark run, the team should have:

- [ ] completed the golden test set
- [ ] resolved labelling disagreements
- [ ] calculated inter-annotator agreement
- [ ] frozen the golden set
- [ ] selected candidate models
- [ ] written the prediction record
- [ ] committed the golden set
- [ ] committed the prediction record

Only then should the formal benchmark results begin.

---

# 12. Suggested Week 1 Deliverables by Member

| Member | End-of-Week Target |
|---|---|
| Member 1 | Baseline service skeleton running in Docker and communicating with Ollama |
| Member 2 | Labelling protocol + Annotator A labels in progress/completed |
| Member 3 | Annotator B labels + initial workload research |
| Member 4 | Candidate-model shortlist + justification draft |
| Member 5 | JMeter installed + open-loop test skeleton + test-machine arrangement |

---

# 13. Shared Team Responsibilities

These should **not** belong to only one member.

## Everyone Should Help With

- reviewing requirements
- reviewing candidate-model choices
- checking whether measurements make sense
- validating charts and tables
- reconciling reported numbers against raw logs
- discussing the final recommendation
- reviewing slides
- understanding the complete system

The final recommendation should follow this logic:

```text
Workload Model
      ↓
Requirements
      ↓
Candidate Models
      ↓
Measurements
      ↓
Compare Results Against Requirements
      ↓
Recommendation
```

---

# 14. Final Submission Awareness

The final submission contains a maximum of **12 PowerPoint slides** plus supporting files.

Supporting evidence includes:

- golden test set
- prediction record
- labelling protocol and revisions
- independent label sheets
- agreement statistic

The repository should also retain:

- raw JMeter `.jtl` files
- service logs
- source code
- files necessary to reproduce the reported measurements

---

# 15. First Team Meeting Checklist

Before ending the first meeting, make sure the team can answer all of these:

- [ ] What rows belong to Group 10?
- [ ] Who is Member 1, 2, 3, 4 and 5?
- [ ] Who are the two independent annotators?
- [ ] How many tickets will be in our golden set?
- [ ] How will those tickets be selected?
- [ ] What backend stack are we using?
- [ ] Which machine runs Ollama + the service?
- [ ] Which separate machine runs JMeter?
- [ ] Where is the GitHub repository?
- [ ] What is our repository structure?
- [ ] When will the golden set be frozen?
- [ ] When will the prediction record be frozen?
- [ ] When will benchmarking begin?
- [ ] When will the first complete set of results be ready?
- [ ] When will the slide deck be assembled?

---

## Recommended Immediate Next Step

Once the roles are assigned:

1. Member 1 starts the baseline service.
2. Members 2 and 3 finalise the labelling protocol and begin independent labelling.
3. Member 3 begins workload research.
4. Member 4 begins candidate-model research.
5. Member 5 sets up JMeter and the separate load-generator machine.

These activities can proceed in parallel.
