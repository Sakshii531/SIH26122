# AI/ML Final Audit Correction: Field Report Dataset Count Clarification

## 1. Overview & Context

This document provides a formal, tracked clarification for PR reviewers regarding the synthetic field report dataset count in the SIH26122 AI/ML module.

Earlier draft audit wording and preliminary work notes incorrectly stated `"41 synthetic field reports"`. This document clarifies that the standardized synthetic dataset contains **36 field reports**, matching the Phase 10 dataset-wide evaluation and all active implementation files.

---

## 2. Verification of Correct Counts

1. **Source Dataset (`ai/data/reports/field_reports.csv`)**:
   - Total rows: **36 field reports** (plus header row).
   - FK References: All reports reference L5/L6 activities in `activities.csv`.

2. **Phase 10 Benchmark Evaluator (`ai/evaluation/evaluator.py`)**:
   - Total Reports Evaluated: **36 field reports**.
   - Evaluable Reports Subset: **27 field reports** (reports with non-null `referenced_activity_id` ground truth).
   - Excluded Non-Evaluable Cases: 9 reports (5 `ambiguous_match`, 4 `conflicting_info`).

3. **Phase 10 Benchmark Report (`ai/evaluation/evaluation_report.md`)**:
   - Total Field Reports Evaluated: **36**.
   - Top-1 Match Accuracy: `48.15% (13/27)`.
   - Top-3 Candidate Recall: `77.78% (21/27)`.
   - Ambiguity Rejection Rate: `60.0% (3/5)`.
   - Conflict Detection Recall: `50.0% (2/4)`.

---

## 3. Key Summary Points for Reviewers

- **Nature of Discrepancy**: The mention of 41 was an outdated audit/documentation statement, **NOT** an ML implementation or dataset issue.
- **Corrected Project Baseline**: The true and canonical count of synthetic field reports across all phases of the SIH26122 AI/ML pipeline is **36**.
- **Scope of Change**: No ML algorithms, extraction logic, matching logic, confidence scoring, conflict detection, OCR, ASR, multi-modal pipeline routing, evaluation metrics, or schedule CSV datasets were altered.
- **Dataset Immutability**: All four source CSV files (`schedules.csv`, `wbs.csv`, `activities.csv`, `field_reports.csv`) remain 100% SHA-256 byte-identical.
