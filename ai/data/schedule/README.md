# Synthetic Schedule Dataset (AI/ML Step 4.2)

## Overview & Disclaimer

> [!IMPORTANT]
> **SYNTHETIC / SAMPLE DATASET NOTICE**
> - This dataset consists of **synthetic sample data** created explicitly for AI/ML development and testing.
> - Primavera P6 / MS Project software access is currently unavailable for the project team.
> - The project team has explicitly approved the use of this realistic synthetic schedule dataset as a temporary working dataset.
> - **DO NOT** claim or present this data as exported directly from Primavera P6 or MS Project.
> - **DO NOT** fabricate real project data or replace this with unverified external files.
> - This dataset will eventually be replaced with real Primavera P6 / MS Project exports without requiring changes to downstream AI/ML models or extraction concepts.

---

## Schema Alignment & Structure

The dataset structure strictly adheres to the finalized database schema for schedule entities (`schedules`, `wbs`, and `activities`).

### 1. `schedules.csv`
Contains high-level metadata for project baseline schedules.

| Column Field | Type | Description |
| :--- | :--- | :--- |
| `schedule_id` | String (PK) | Unique schedule identifier (e.g. `SCH-001`) |
| `project_id` | String | Associated project identifier (e.g. `PROJ-001`) |
| `name` | String | Baseline schedule title |
| `source_type` | String | Source designation (`synthetic_sample`) |
| `baseline_date` | Date (YYYY-MM-DD) | Project baseline approval date |
| `created_at` | Datetime (ISO 8601) | Timestamp of dataset creation |

### 2. `wbs.csv`
Contains the multi-level Work Breakdown Structure (WBS) representing a greenfield industrial refinery and infrastructure project across levels **L1 to L6**.

| Column Field | Type | Description |
| :--- | :--- | :--- |
| `wbs_id` | String (PK) | Unique WBS node identifier (e.g. `WBS-311-1`) |
| `schedule_id` | String (FK) | References `schedules.csv` (`schedule_id`) |
| `parent_wbs_id` | String (FK/Nullable)| References parent `wbs_id` (empty for root L1) |
| `code` | String | Hierarchical WBS code (e.g. `1.3.1.1.1`) |
| `name` | String | Description of WBS node / work package |
| `level` | String | Hierarchy level (`L1`, `L2`, `L3`, `L4`, `L5`, `L6`) |
| `created_at` | Datetime (ISO 8601) | Timestamp of record creation |

#### Hierarchy Breakdown:
- **L1**: Greenfield Project Root
- **L2**: Major Project Phases (Engineering, Procurement, Process Plant Construction, Utilities, Pre-Commissioning)
- **L3**: Process Units & Infrastructure Areas (CDU-100, DHT-200, Cooling Towers, Substation)
- **L4**: Engineering & Construction Discipline Work Packages
- **L5**: Major Execution Work Packages (e.g. Foundation Packages, Piping Modules, Cable Tray Racks)
- **L6**: Detailed Execution Tasks (e.g. Excavation, Rebar Shuttering, Spool Welding)

### 3. `activities.csv`
Contains 160 realistic synthetic activities primarily focused on **L5** and **L6** schedule activity nodes for future AI/ML activity matching experiments.

| Column Field | Type | Description |
| :--- | :--- | :--- |
| `activity_id` | String (PK) | Unique activity identifier (e.g. `ACT-001`) |
| `wbs_id` | String (FK) | References `wbs.csv` (`wbs_id`) |
| `activity_code` | String | Unique schedule activity code (e.g. `CIV-001`) |
| `name` | String | Detailed activity description with equipment tags & spools |
| `level` | String | Activity level designation (`L5` or `L6`) |
| `discipline` | String | Engineering discipline (`Civil`, `Structural`, `Piping`, `Mechanical`, `Electrical`, `Instrumentation`) |
| `planned_start` | Date (YYYY-MM-DD) | Planned start date |
| `planned_finish` | Date (YYYY-MM-DD) | Planned finish date |
| `duration` | Integer | Calendar duration in days (`planned_finish - planned_start + 1`) |
| `status` | String | Execution status (`Not Started`, `In Progress`, `Completed`) |
| `created_at` | Datetime (ISO 8601) | Timestamp of record creation |

> [!NOTE]
> **Strict Schema Compliance Note on `location`:**
> `location` is deliberately **NOT** included in `activities.csv` in accordance with the finalized ER diagram and database schema. Location is handled downstream in extracted progress event tables (`extracted_progress_events`).

---

## Intended AI/ML Usage & Preparation for Step 4.3+

The realistic terminology, equipment tags (e.g., `Column C-101`, `Pump P-101A`, `Reactor R-201`, `Spool 24-CDU-001`), discipline contexts, and action verbs in `activities.csv` are designed to support upcoming AI/ML workflows:
1. **Activity Matching**: Matching unstructured natural language field report logs (e.g., *"Civil crew finished rebar shuttering for C-101 foundation"*) against schedule activities (`ACT-004`).
2. **Schedule Understanding**: Building semantic embeddings and graph structures based on the L1–L6 WBS hierarchy.

---

## Validation & Dataset Integrity

Run the programmatic validation script inside `ai/data/schedule/`:

```bash
python ai/data/schedule/validate_schedule_data.py
```

The script verifies:
- Header schema alignment with finalized database entities.
- Absence of forbidden columns (e.g. `location`, `actual_start`).
- Foreign key integrity (`wbs` -> `schedules`, `activities` -> `wbs`, `wbs` -> `parent_wbs`).
- WBS level hierarchy rules (L1–L6) and circular reference detection.
- Activity levels (`L5`/`L6`), valid disciplines, and statuses.
- Chronological integrity (`planned_start <= planned_finish`) and exact duration calculations (`duration == finish - start + 1`).
