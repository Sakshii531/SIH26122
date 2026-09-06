# SIH26122 — Planning-to-Execution Bridge

> An AI-powered bridge that converts heterogeneous field progress reports into validated L5/L6 schedule updates.

## Overview

SIH26122 is an AI-powered **Planning-to-Execution Bridge** for infrastructure projects.

Infrastructure projects are planned using structured schedules in systems such as Primavera P6 or MS Project. However, actual site progress is reported through DPRs, Excel files, site notes, voice updates, and other field sources.

Our system connects these two worlds by transforming field execution data into structured, validated progress events and linking them to the appropriate L5/L6 schedule activities.

The system is designed as an intelligence layer that works alongside existing project planning systems rather than replacing them.

---

## Problem

Infrastructure project schedules contain detailed planned activities across multiple engineering disciplines.

During execution, actual progress is reported through fragmented and inconsistent sources such as:

* Daily Progress Reports (DPRs)
* Excel sheets
* Site diaries
* Text/notes
* Voice updates
* Scanned documents
* Photos/evidence

Field reports often use terminology that differs from the official schedule, making it difficult to reliably identify the corresponding L5/L6 activity.

This leads to:

* Fragmented progress information
* Inconsistent terminology
* Manual reconciliation
* Delayed schedule updates
* Conflicting or incomplete information
* Difficulty maintaining execution history

### Core Problem

> The project plan knows what was planned, while field reports describe what actually happened — but reliably connecting actual field progress to the correct L5/L6 schedule activities is difficult, manual, and error-prone.

---

## Solution

We propose an AI-powered Planning-to-Execution Bridge that:

1. Ingests baseline schedule data.
2. Accepts heterogeneous field progress reports.
3. Extracts structured information from field reports.
4. Semantically matches reported work to L5/L6 schedule activities.
5. Generates confidence scores for AI-generated matches.
6. Detects uncertain, unmatched, or conflicting information.
7. Routes cases requiring validation to a human planner.
8. Records planner decisions.
9. Updates validated actual progress.
10. Maintains an auditable execution history.
11. Provides a project progress dashboard.

The system follows a **human-in-the-loop** approach so that AI recommendations do not directly modify validated schedule data without appropriate verification.

---

## Key Features

### Schedule Ingestion

Import baseline project schedules containing:

* Project information
* WBS hierarchy
* L5/L6 activities
* Activity IDs
* Activity descriptions
* Disciplines
* Planned dates
* Locations
* Other relevant schedule information

### Multi-Format Field Reporting

Support field progress through:

* Text/notes
* DPR documents
* Excel/CSV files
* Voice reports
* Supporting evidence

### AI Progress Extraction

Extract structured information such as:

* Activity/work description
* Status
* Actual start/end information
* Date/time
* Discipline
* Location
* Progress information

### Intelligent L5/L6 Matching

Use semantic understanding to identify the most relevant planned activity for a field report.

### Confidence Scoring

Every AI-generated match receives a confidence score.

Low-confidence cases can be routed to the planner instead of being automatically accepted.

### Human-in-the-Loop Review

The planner can:

* Approve
* Reject
* Correct
* Select another activity
* Resolve conflicts

### Conflict Detection

Identify potentially conflicting progress information from different reports or sources.

### Evidence

Attach supporting evidence such as:

* Images
* Documents
* Audio
* Other relevant files

Evidence acts as an additional verification signal rather than being treated as absolute proof.

### Actual Progress Tracking

Validated information can update the actual status and dates associated with schedule activities.

### Audit Trail

Maintain traceability of important actions:

```text
Field Report
    ↓
AI Extraction
    ↓
AI Match
    ↓
Confidence
    ↓
Planner Decision
    ↓
Validated Progress
```

### Progress Dashboard

Provide visibility into:

* Overall project progress
* Activity status
* Discipline-level progress
* Delays
* Items requiring review
* Other project indicators

---

## How It Works

```text
                    SUPERVISOR
                        │
            ┌───────────┼───────────┐
            │           │           │
          Voice       Text       Files
                                    │
                              DPR / Excel
                                    │
                                    ▼
                         MOBILE-FIRST WEB APP
                                    │
                                    ▼
                               FASTAPI
                                  BACKEND
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
               AI ENGINE                       DATABASE
                    │                         PostgreSQL
                    │                         + pgvector
                    │
                    ▼
             Structured Event
                    │
                    ▼
              L5/L6 Matching
                    │
                    ▼
             Confidence Check
                    │
              ┌─────┴─────┐
              │           │
           Reliable    Uncertain /
              │         Conflict
              │           │
              │           ▼
              │      PLANNER REVIEW
              │           │
              │     Approve / Correct /
              │      Reject / Resolve
              │           │
              └─────┬─────┘
                    ▼
             VALIDATED PROGRESS
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
       Dashboard          Audit Trail
```

---

## Architecture

The MVP contains two user roles:

### Supervisor

Responsible for reporting actual field execution.

Supervisor capabilities include:

* Submit voice reports
* Submit text/notes
* Upload DPR/Excel files
* Attach supporting evidence
* View submitted reports

### Planner

Responsible for validating and managing reported progress.

Planner capabilities include:

* View extracted events
* Review AI activity matches
* View confidence scores
* Approve/reject matches
* Correct activity matches
* Resolve conflicts
* View validated progress
* View audit history
* Monitor project progress

### Architectural Principle

The AI engine does **not** directly modify validated schedule data.

```text
AI Suggestion
      ↓
Matching
      ↓
Confidence / Rules
      ↓
Planner Review when required
      ↓
Validated Event
      ↓
Progress Update
```

---

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI

### Database

* PostgreSQL
* pgvector

### Storage

* S3-compatible object storage / Supabase Storage

### AI

* Automatic Speech Recognition (ASR)
* Large Language Models (LLMs)
* Embeddings
* Semantic matching
* Confidence scoring
* Conflict detection
* OCR/vision where required

### Development

* Git
* GitHub

---

## Project Structure

```text
SIH26122/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   ├── hooks/
│   ├── types/
│   └── public/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/
│   │   └── main.py
│   └── tests/
│
├── ai/
│   ├── extraction/
│   ├── matching/
│   ├── confidence/
│   ├── conflict/
│   ├── asr/
│   ├── prompts/
│   └── tests/
│
├── database/
│   ├── migrations/
│   ├── schema/
│   └── seed/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── product/
│   └── research/
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── test-data/
│
├── .env.example
├── .gitignore
└── README.md
```

---

## MVP Workflow

The primary MVP demonstration follows this workflow:

```text
1. Import baseline L5/L6 schedule
             ↓
2. Supervisor submits field report
             ↓
3. AI extracts progress information
             ↓
4. AI identifies candidate L5/L6 activity
             ↓
5. Confidence score generated
             ↓
6. Uncertain/conflicting cases go to Planner
             ↓
7. Planner approves/corrects/rejects
             ↓
8. Actual progress is updated
             ↓
9. Audit trail is recorded
             ↓
10. Dashboard reflects updated progress
```

---

## Development Principles

### MVP First

Build and validate the core workflow before adding advanced capabilities.

### Human-in-the-Loop

AI recommendations must be distinguishable from human-validated information.

### Auditability

Important actions and decisions must remain traceable.

### Modular Architecture

AI services, frontend, backend and data services should remain loosely coupled so individual components can be improved or replaced.

### Existing Systems

The system is designed to work alongside existing planning/scheduling systems rather than replacing them.

### Evidence-Aware

Supporting evidence can strengthen confidence and verification but should not automatically be treated as definitive proof.

---

## Project Status

**Current Stage:** MVP Development

### MVP Scope

* [ ] Project setup
* [ ] Authentication
* [ ] Schedule ingestion
* [ ] L5/L6 activity management
* [ ] Field report ingestion
* [ ] AI extraction
* [ ] L5/L6 semantic matching
* [ ] Confidence scoring
* [ ] Planner review
* [ ] Conflict detection
* [ ] Actual progress update
* [ ] Audit trail
* [ ] Progress dashboard

### Future Enhancements

* [ ] Multilingual voice reporting
* [ ] Advanced OCR
* [ ] Visual evidence analysis
* [ ] Institutional memory / RAG
* [ ] Advanced analytics
* [ ] Predictive schedule insights
* [ ] Deeper Primavera/MS Project integration
* [ ] Dedicated mobile application

---

## Team

| Member    | Responsibility            |
| --------- | ------------------------- |
| Sarvesh   | Team Lead / Product       |
| Yash      | Frontend Developer        |
| Parth     | Backend Developer         |
| Sanskruti | AI/ML Engineer            |
| Tanuja    | Database & Security       |
| Sakshi    | DevOps / Integration / QA |

---

## Project Goal

> Build a trustworthy bridge between planned project schedules and actual field execution by intelligently converting fragmented field information into validated, auditable L5/L6 progress data.

---

## Disclaimer

This project is developed as a prototype for **Smart India Hackathon 2026 — SIH26122** using synthetic/sample project data where real project data is unavailable.
