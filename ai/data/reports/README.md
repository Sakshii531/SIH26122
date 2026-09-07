# Synthetic Field Report Dataset (AI/ML Step 5.1)

## Overview

This directory contains a synthetic dataset of field reports, site logs, supervisor notes, and daily progress summaries designed to test downstream AI/ML modules (NLP extraction, activity matching, vector search, confidence scoring, and conflict detection).

All field reports correspond to work packages and execution tasks defined in the synthetic schedule activities dataset ([`ai/data/schedule/activities.csv`](file:///c:/Users/Sanskruti/Desktop/SIH26122/ai/data/schedule/activities.csv)).

---

## Dataset Schema (`field_reports.csv`)

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `report_id` | String (PK) | Unique field report identifier (e.g. `REP-001`) |
| `report_date` | Date (YYYY-MM-DD) | Date of site report (may be empty for missing detail test cases) |
| `source_type` | String | Source designation (e.g. `synthetic_site_log`, `synthetic_shift_report`, `synthetic_supervisor_report`) |
| `raw_text` | String | Unstructured natural language text representing site log entry |
| `referenced_activity_id` | String (FK/Nullable) | References schedule `activity_id` from `activities.csv` if known |
| `referenced_activity_code` | String (FK/Nullable) | References schedule `activity_code` from `activities.csv` if known |
| `expected_case` | String | Test category classification (see list below) |

---

## Test Categories (`expected_case`)

The dataset incorporates 36 synthetic field reports categorized into 7 distinct cases:

1. **`clear_exact_match`**: Explicit mention of activity code/name and clear progress notes.
2. **`paraphrased_match`**: Natural language variation describing identical technical scope without using exact schedule activity title wording.
3. **`short_log`**: Brief 1-line site supervisor logs.
4. **`detailed_report`**: Comprehensive multi-sentence shift report detailing crew size, equipment, elevations, and tolerances.
5. **`missing_details`**: Site entries missing specific dates, tags, or completion metrics.
6. **`ambiguous_match`**: Broad site entries that could match multiple WBS activities in the schedule.
7. **`conflicting_info`**: Contradictory reports (e.g., supervisor claiming 100% completion while QC flags defects or delays).

---

## Discipline Coverage

The reports cover all 6 primary engineering & construction disciplines:
- **Civil**: Excavation, rebar binding, formwork, PCC blinding, concrete pouring.
- **Structural**: Anchor bolt setting, baseplate levelling, pipe rack steel column erection, transverse beam assembly.
- **Mechanical**: Heavy lift crane setup, vessel vertical alignment, pump skid placement, reactor setting.
- **Piping**: Support fabrication, spool erection, root pass welding, receiving inspection.
- **Electrical**: Switchgear panel placement, busbar torque check, cable tray bracket welding.
- **Instrumentation**: Junction box wall mounting, transmitter stanchion mounting, impulse tubing erection.
