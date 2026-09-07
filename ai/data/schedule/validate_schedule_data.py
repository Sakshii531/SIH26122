#!/usr/bin/env python3
"""
Validation script for synthetic schedule dataset in ai/data/schedule/

Validates:
1. File existence & UTF-8 formatting
2. Column schema alignment with database schema
3. Foreign key integrity (wbs -> schedules, activities -> wbs, wbs -> parent_wbs)
4. Primary key uniqueness (schedule_id, wbs_id, activity_id)
5. WBS hierarchy consistency (L1 to L6, no circular parent links)
6. Activity levels (L5 or L6)
7. Discipline validity (Civil, Structural, Piping, Mechanical, Electrical, Instrumentation)
8. Status values (Not Started, In Progress, Completed)
9. Date validity and start <= finish chronological constraints
10. Duration consistency (finish_date - start_date + 1 == duration)
11. Absence of forbidden columns (e.g., location, actual dates)
"""

import csv
import datetime
import sys
from pathlib import Path

# Base path setup
SCHEDULE_DIR = Path(__file__).resolve().parent

EXPECTED_FILES = {
    "schedules.csv": [
        "schedule_id",
        "project_id",
        "name",
        "source_type",
        "baseline_date",
        "created_at",
    ],
    "wbs.csv": [
        "wbs_id",
        "schedule_id",
        "parent_wbs_id",
        "code",
        "name",
        "level",
        "created_at",
    ],
    "activities.csv": [
        "activity_id",
        "wbs_id",
        "activity_code",
        "name",
        "level",
        "discipline",
        "planned_start",
        "planned_finish",
        "duration",
        "status",
        "created_at",
    ],
}

FORBIDDEN_COLUMNS = {
    "activities.csv": [
        "location",
        "actual_start",
        "actual_finish",
        "progress_value",
        "confidence_score",
        "match_status",
        "report_id",
        "event_id",
    ]
}

VALID_DISCIPLINES = {
    "Civil",
    "Structural",
    "Piping",
    "Mechanical",
    "Electrical",
    "Instrumentation",
}

VALID_STATUSES = {"Not Started", "In Progress", "Completed"}
VALID_ACTIVITY_LEVELS = {"L5", "L6"}
VALID_WBS_LEVELS = {"L1", "L2", "L3", "L4", "L5", "L6"}

LEVEL_ORDER = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}


def run_validation():
    print("=" * 60)
    print("STARTING SCHEDULE DATASET VALIDATION")
    print("=" * 60)

    errors = []
    warnings = []

    # 1. Check file existence & load CSVs
    data = {}
    for filename, expected_cols in EXPECTED_FILES.items():
        filepath = SCHEDULE_DIR / filename
        if not filepath.exists():
            errors.append(f"Missing required file: {filename}")
            continue

        try:
            with open(filepath, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if not headers:
                    errors.append(f"{filename} is empty or has no header.")
                    continue

                # Check headers
                if headers != expected_cols:
                    errors.append(
                        f"{filename} headers mismatch.\nExpected: {expected_cols}\nActual:   {headers}"
                    )

                # Check forbidden columns
                if filename in FORBIDDEN_COLUMNS:
                    for forbidden in FORBIDDEN_COLUMNS[filename]:
                        if forbidden in headers:
                            errors.append(
                                f"{filename} contains forbidden column '{forbidden}'."
                            )

                rows = list(reader)
                data[filename] = rows
                print(f"Loaded {filename}: {len(rows)} rows.")

        except Exception as e:
            errors.append(f"Failed to read {filename}: {e}")

    if errors:
        print("\n[FAIL] File structure check failed:")
        for err in errors:
            print(f"  - {err}")
        return False

    schedules_rows = data["schedules.csv"]
    wbs_rows = data["wbs.csv"]
    activities_rows = data["activities.csv"]

    # 2. Validate schedules.csv
    schedule_ids = set()
    for i, row in enumerate(schedules_rows, start=2):
        sid = row.get("schedule_id", "").strip()
        if not sid:
            errors.append(f"schedules.csv line {i}: Empty schedule_id")
        elif sid in schedule_ids:
            errors.append(f"schedules.csv line {i}: Duplicate schedule_id '{sid}'")
        else:
            schedule_ids.add(sid)

        # Check required fields
        for field in ["project_id", "name", "source_type", "baseline_date", "created_at"]:
            if not row.get(field, "").strip():
                errors.append(f"schedules.csv line {i}: Missing required field '{field}'")

    # 3. Validate wbs.csv
    wbs_ids = set()
    wbs_dict = {}
    for i, row in enumerate(wbs_rows, start=2):
        wid = row.get("wbs_id", "").strip()
        sid = row.get("schedule_id", "").strip()
        parent_id = row.get("parent_wbs_id", "").strip()
        lvl = row.get("level", "").strip()

        if not wid:
            errors.append(f"wbs.csv line {i}: Empty wbs_id")
        elif wid in wbs_ids:
            errors.append(f"wbs.csv line {i}: Duplicate wbs_id '{wid}'")
        else:
            wbs_ids.add(wid)
            wbs_dict[wid] = row

        # FK to schedule
        if sid not in schedule_ids:
            errors.append(f"wbs.csv line {i}: Foreign key error. schedule_id '{sid}' not in schedules.csv")

        # Level check
        if lvl not in VALID_WBS_LEVELS:
            errors.append(f"wbs.csv line {i}: Invalid level '{lvl}'. Must be L1-L6.")

        # Root check
        if lvl == "L1" and parent_id:
            errors.append(f"wbs.csv line {i}: Root L1 node '{wid}' should have empty parent_wbs_id.")

    # Validate parent_wbs_id existence & parent level hierarchy & circular ref check
    for wid, row in wbs_dict.items():
        parent_id = row.get("parent_wbs_id", "").strip()
        lvl = row.get("level", "").strip()

        if parent_id:
            if parent_id not in wbs_ids:
                errors.append(f"wbs.csv WBS '{wid}': Parent WBS ID '{parent_id}' does not exist.")
            else:
                parent_row = wbs_dict[parent_id]
                parent_lvl = parent_row.get("level", "").strip()
                if LEVEL_ORDER.get(lvl, 0) <= LEVEL_ORDER.get(parent_lvl, 0):
                    errors.append(
                        f"wbs.csv WBS '{wid}' ({lvl}) level is not deeper than parent '{parent_id}' ({parent_lvl})."
                    )

            # Circular dependency check
            curr = parent_id
            visited = {wid}
            while curr:
                if curr in visited:
                    errors.append(f"wbs.csv WBS '{wid}': Circular parent reference detected involving '{curr}'.")
                    break
                visited.add(curr)
                curr = wbs_dict.get(curr, {}).get("parent_wbs_id", "").strip()

    # 4. Validate activities.csv
    activity_ids = set()
    activity_codes = set()

    for i, row in enumerate(activities_rows, start=2):
        aid = row.get("activity_id", "").strip()
        wid = row.get("wbs_id", "").strip()
        acode = row.get("activity_code", "").strip()
        name = row.get("name", "").strip()
        lvl = row.get("level", "").strip()
        discipline = row.get("discipline", "").strip()
        p_start_str = row.get("planned_start", "").strip()
        p_finish_str = row.get("planned_finish", "").strip()
        dur_str = row.get("duration", "").strip()
        status = row.get("status", "").strip()

        # Unique activity_id
        if not aid:
            errors.append(f"activities.csv line {i}: Empty activity_id")
        elif aid in activity_ids:
            errors.append(f"activities.csv line {i}: Duplicate activity_id '{aid}'")
        else:
            activity_ids.add(aid)

        # Unique activity_code
        if acode in activity_codes:
            errors.append(f"activities.csv line {i}: Duplicate activity_code '{acode}'")
        else:
            activity_codes.add(acode)

        # FK to WBS
        if wid not in wbs_ids:
            errors.append(f"activities.csv line {i}: Foreign key error. wbs_id '{wid}' not found in wbs.csv")

        # Level check
        if lvl not in VALID_ACTIVITY_LEVELS:
            errors.append(f"activities.csv line {i}: Invalid activity level '{lvl}'. Expected L5 or L6.")

        # Discipline check
        if discipline not in VALID_DISCIPLINES:
            errors.append(f"activities.csv line {i}: Invalid discipline '{discipline}'. Allowed: {VALID_DISCIPLINES}")

        # Status check
        if status not in VALID_STATUSES:
            errors.append(f"activities.csv line {i}: Invalid status '{status}'. Allowed: {VALID_STATUSES}")

        # Date & Duration logic
        try:
            p_start = datetime.datetime.strptime(p_start_str, "%Y-%m-%d").date()
            p_finish = datetime.datetime.strptime(p_finish_str, "%Y-%m-%d").date()

            if p_start > p_finish:
                errors.append(
                    f"activities.csv line {i} ('{aid}'): planned_start ({p_start_str}) > planned_finish ({p_finish_str})"
                )

            expected_duration = (p_finish - p_start).days + 1
            dur = int(dur_str)

            if dur != expected_duration:
                errors.append(
                    f"activities.csv line {i} ('{aid}'): Duration {dur} mismatch with dates ({p_start_str} to {p_finish_str} = {expected_duration} days)"
                )
        except ValueError as ve:
            errors.append(f"activities.csv line {i} ('{aid}'): Date/duration parsing error: {ve}")

    # Summary
    print("-" * 60)
    if errors:
        print(f"Validation completed with {len(errors)} ERROR(S):")
        for err in errors:
            print(f" [ERROR] {err}")
        return False
    else:
        print("PASS:")
        print(" - schedules.csv valid")
        print(" - wbs.csv valid")
        print(" - activities.csv valid")
        print(" - foreign-key relationships valid")
        print(" - hierarchy valid")
        print(" - dates valid")
        print(" - no duplicate IDs")
        print(" - no missing required fields")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
