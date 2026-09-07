"""
Schedule Data Loader & Normalization Module for SIH26122.

Provides schema validation, date/datetime normalization, object-oriented 
WBS tree building, and relationship linking from schedules.csv, wbs.csv,
and activities.csv.
"""

from dataclasses import dataclass, field
import csv
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Set


class ScheduleValidationError(Exception):
    """Raised when schedule dataset files fail schema, foreign key, date, or hierarchy validation."""
    pass


# Schema expectations aligned with finalized database schema
EXPECTED_SCHED_HEADERS = [
    "schedule_id",
    "project_id",
    "name",
    "source_type",
    "baseline_date",
    "created_at",
]

EXPECTED_WBS_HEADERS = [
    "wbs_id",
    "schedule_id",
    "parent_wbs_id",
    "code",
    "name",
    "level",
    "created_at",
]

EXPECTED_ACT_HEADERS = [
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
]

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


def _parse_date(date_str: str, field_name: str, context: str) -> datetime.date:
    """Parse ISO date string (YYYY-MM-DD) into datetime.date."""
    if not date_str or not date_str.strip():
        raise ScheduleValidationError(f"Missing required date field '{field_name}' in {context}")
    clean_str = date_str.strip()
    try:
        return datetime.date.fromisoformat(clean_str)
    except ValueError:
        try:
            return datetime.datetime.strptime(clean_str, "%Y-%m-%d").date()
        except ValueError:
            raise ScheduleValidationError(
                f"Invalid date format '{date_str}' for field '{field_name}' in {context}. Expected YYYY-MM-DD."
            )


def _parse_datetime(dt_str: str, field_name: str, context: str) -> datetime.datetime:
    """Parse ISO datetime string into datetime.datetime."""
    if not dt_str or not dt_str.strip():
        raise ScheduleValidationError(f"Missing required datetime field '{field_name}' in {context}")
    clean_str = dt_str.strip()
    try:
        iso_str = clean_str[:-1] + "+00:00" if clean_str.endswith("Z") else clean_str
        return datetime.datetime.fromisoformat(iso_str)
    except ValueError:
        try:
            return datetime.datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ScheduleValidationError(
                f"Invalid datetime format '{dt_str}' for field '{field_name}' in {context}."
            )


@dataclass
class Schedule:
    """In-memory representation of schedule metadata."""
    schedule_id: str
    project_id: str
    name: str
    source_type: str
    baseline_date: datetime.date
    created_at: datetime.datetime


@dataclass
class Activity:
    """In-memory representation of a schedule activity."""
    activity_id: str
    wbs_id: str
    activity_code: str
    name: str
    level: str
    discipline: str
    planned_start: datetime.date
    planned_finish: datetime.date
    duration: int
    status: str
    created_at: datetime.datetime
    wbs_node: Optional["WBSNode"] = field(default=None, repr=False)


@dataclass
class WBSNode:
    """In-memory representation of a Work Breakdown Structure (WBS) node."""
    wbs_id: str
    schedule_id: str
    parent_wbs_id: Optional[str]
    code: str
    name: str
    level: str
    created_at: datetime.datetime
    children: List["WBSNode"] = field(default_factory=list, repr=False)
    parent: Optional["WBSNode"] = field(default=None, repr=False)
    activities: List[Activity] = field(default_factory=list, repr=False)


@dataclass
class ScheduleDataset:
    """
    Container class for a complete loaded schedule dataset, providing fast lookups,
    WBS tree hierarchy traversal, and discipline/status filtering.
    """
    schedules: Dict[str, Schedule]
    wbs_nodes: Dict[str, WBSNode]
    root_wbs_nodes: List[WBSNode]
    activities: Dict[str, Activity]

    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Fetch schedule metadata by schedule_id."""
        return self.schedules.get(schedule_id)

    def get_wbs(self, wbs_id: str) -> Optional[WBSNode]:
        """Fetch WBS node by wbs_id."""
        return self.wbs_nodes.get(wbs_id)

    def get_activity(self, activity_id: str) -> Optional[Activity]:
        """Fetch activity by activity_id."""
        return self.activities.get(activity_id)

    def get_activities_for_wbs(self, wbs_id: str, recursive: bool = False) -> List[Activity]:
        """
        Get activities assigned to a WBS node.
        If recursive is True, includes activities belonging to child WBS sub-trees.
        """
        wbs = self.get_wbs(wbs_id)
        if not wbs:
            return []

        if not recursive:
            return list(wbs.activities)

        result = []
        stack = [wbs]
        while stack:
            curr = stack.pop()
            result.extend(curr.activities)
            stack.extend(curr.children)
        return result

    def get_activities_by_discipline(self, discipline: str) -> List[Activity]:
        """Filter activities by engineering discipline."""
        return [act for act in self.activities.values() if act.discipline == discipline]

    def get_activities_by_status(self, status: str) -> List[Activity]:
        """Filter activities by schedule status."""
        return [act for act in self.activities.values() if act.status == status]


class ScheduleLoader:
    """Loader class responsible for reading CSV dataset files, validating schema/data, and returning a ScheduleDataset."""

    @classmethod
    def load_from_directory(cls, dir_path: Union[str, Path]) -> ScheduleDataset:
        """Load schedule dataset from directory containing schedules.csv, wbs.csv, and activities.csv."""
        folder = Path(dir_path)
        schedules_file = folder / "schedules.csv"
        wbs_file = folder / "wbs.csv"
        activities_file = folder / "activities.csv"

        return cls.load_from_files(
            schedules_path=schedules_file,
            wbs_path=wbs_file,
            activities_path=activities_file
        )

    @classmethod
    def load_from_files(
        cls,
        schedules_path: Union[str, Path],
        wbs_path: Union[str, Path],
        activities_path: Union[str, Path],
    ) -> ScheduleDataset:
        """Load schedule dataset from explicit CSV file paths."""
        s_path = Path(schedules_path)
        w_path = Path(wbs_path)
        a_path = Path(activities_path)

        for p, label in [(s_path, "schedules.csv"), (w_path, "wbs.csv"), (a_path, "activities.csv")]:
            if not p.exists():
                raise ScheduleValidationError(f"Missing required schedule file '{label}' at path: {p}")

        schedules = cls._load_schedules(s_path)
        wbs_nodes, root_wbs_nodes = cls._load_wbs(w_path, set(schedules.keys()))
        activities = cls._load_activities(a_path, wbs_nodes)

        return ScheduleDataset(
            schedules=schedules,
            wbs_nodes=wbs_nodes,
            root_wbs_nodes=root_wbs_nodes,
            activities=activities,
        )

    @classmethod
    def _read_csv(cls, path: Path, expected_headers: List[str], filename_label: str) -> List[dict]:
        """Read CSV file, validate non-empty and matching headers."""
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                if not headers:
                    raise ScheduleValidationError(f"{filename_label} is empty or missing header line.")
                
                if headers != expected_headers:
                    raise ScheduleValidationError(
                        f"Schema header mismatch in {filename_label}.\n"
                        f"Expected: {expected_headers}\n"
                        f"Actual:   {headers}"
                    )
                return list(reader)
        except ScheduleValidationError:
            raise
        except Exception as e:
            raise ScheduleValidationError(f"Error reading {filename_label}: {e}")

    @classmethod
    def _load_schedules(cls, path: Path) -> Dict[str, Schedule]:
        rows = cls._read_csv(path, EXPECTED_SCHED_HEADERS, "schedules.csv")
        schedules: Dict[str, Schedule] = {}

        for i, row in enumerate(rows, start=2):
            sid = row.get("schedule_id", "").strip()
            if not sid:
                raise ScheduleValidationError(f"schedules.csv line {i}: Empty schedule_id")
            if sid in schedules:
                raise ScheduleValidationError(f"schedules.csv line {i}: Duplicate schedule_id '{sid}'")

            pid = row.get("project_id", "").strip()
            name = row.get("name", "").strip()
            stype = row.get("source_type", "").strip()

            if not pid or not name or not stype:
                raise ScheduleValidationError(f"schedules.csv line {i}: Missing required text field(s)")

            b_date = _parse_date(row.get("baseline_date", ""), "baseline_date", f"schedules.csv line {i}")
            c_at = _parse_datetime(row.get("created_at", ""), "created_at", f"schedules.csv line {i}")

            schedules[sid] = Schedule(
                schedule_id=sid,
                project_id=pid,
                name=name,
                source_type=stype,
                baseline_date=b_date,
                created_at=c_at,
            )

        return schedules

    @classmethod
    def _load_wbs(cls, path: Path, valid_schedule_ids: Set[str]) -> (Dict[str, WBSNode], List[WBSNode]):
        rows = cls._read_csv(path, EXPECTED_WBS_HEADERS, "wbs.csv")
        wbs_nodes: Dict[str, WBSNode] = {}
        root_nodes: List[WBSNode] = []

        # Pass 1: Parse & instantiate WBSNode objects
        for i, row in enumerate(rows, start=2):
            wid = row.get("wbs_id", "").strip()
            sid = row.get("schedule_id", "").strip()
            parent_id = row.get("parent_wbs_id", "").strip() or None
            code = row.get("code", "").strip()
            name = row.get("name", "").strip()
            level = row.get("level", "").strip()

            if not wid:
                raise ScheduleValidationError(f"wbs.csv line {i}: Empty wbs_id")
            if wid in wbs_nodes:
                raise ScheduleValidationError(f"wbs.csv line {i}: Duplicate wbs_id '{wid}'")
            if sid not in valid_schedule_ids:
                raise ScheduleValidationError(f"wbs.csv line {i}: Foreign key error. schedule_id '{sid}' not found.")
            if level not in VALID_WBS_LEVELS:
                raise ScheduleValidationError(f"wbs.csv line {i}: Invalid WBS level '{level}' for WBS '{wid}'")
            if not code or not name:
                raise ScheduleValidationError(f"wbs.csv line {i}: Missing required code/name for WBS '{wid}'")

            c_at = _parse_datetime(row.get("created_at", ""), "created_at", f"wbs.csv line {i}")

            node = WBSNode(
                wbs_id=wid,
                schedule_id=sid,
                parent_wbs_id=parent_id,
                code=code,
                name=name,
                level=level,
                created_at=c_at,
            )
            wbs_nodes[wid] = node

        # Pass 2: Link parent-child relationships & validate hierarchy
        for wid, node in wbs_nodes.items():
            if node.parent_wbs_id:
                parent_node = wbs_nodes.get(node.parent_wbs_id)
                if not parent_node:
                    raise ScheduleValidationError(
                        f"wbs.csv WBS '{wid}': Referenced parent_wbs_id '{node.parent_wbs_id}' does not exist."
                    )
                node.parent = parent_node
                parent_node.children.append(node)
            else:
                root_nodes.append(node)

        return wbs_nodes, root_nodes

    @classmethod
    def _load_activities(cls, path: Path, wbs_nodes: Dict[str, WBSNode]) -> Dict[str, Activity]:
        rows = cls._read_csv(path, EXPECTED_ACT_HEADERS, "activities.csv")
        activities: Dict[str, Activity] = {}

        for i, row in enumerate(rows, start=2):
            aid = row.get("activity_id", "").strip()
            wid = row.get("wbs_id", "").strip()
            acode = row.get("activity_code", "").strip()
            name = row.get("name", "").strip()
            level = row.get("level", "").strip()
            discipline = row.get("discipline", "").strip()
            dur_str = row.get("duration", "").strip()
            status = row.get("status", "").strip()

            if not aid:
                raise ScheduleValidationError(f"activities.csv line {i}: Empty activity_id")
            if aid in activities:
                raise ScheduleValidationError(f"activities.csv line {i}: Duplicate activity_id '{aid}'")

            wbs_node = wbs_nodes.get(wid)
            if not wbs_node:
                raise ScheduleValidationError(f"activities.csv line {i}: Foreign key error. wbs_id '{wid}' not found in wbs.csv")

            if level not in VALID_ACTIVITY_LEVELS:
                raise ScheduleValidationError(f"activities.csv line {i}: Invalid activity level '{level}'. Expected L5 or L6.")
            if discipline not in VALID_DISCIPLINES:
                raise ScheduleValidationError(f"activities.csv line {i}: Invalid discipline '{discipline}'.")
            if status not in VALID_STATUSES:
                raise ScheduleValidationError(f"activities.csv line {i}: Invalid status '{status}'.")
            if not acode or not name:
                raise ScheduleValidationError(f"activities.csv line {i}: Missing required code or name for activity '{aid}'.")

            p_start = _parse_date(row.get("planned_start", ""), "planned_start", f"activities.csv line {i}")
            p_finish = _parse_date(row.get("planned_finish", ""), "planned_finish", f"activities.csv line {i}")

            if p_start > p_finish:
                raise ScheduleValidationError(
                    f"activities.csv line {i} ('{aid}'): planned_start ({p_start}) > planned_finish ({p_finish})"
                )

            try:
                duration = int(dur_str)
            except ValueError:
                raise ScheduleValidationError(f"activities.csv line {i} ('{aid}'): Invalid non-integer duration '{dur_str}'")

            expected_duration = (p_finish - p_start).days + 1
            if duration != expected_duration:
                raise ScheduleValidationError(
                    f"activities.csv line {i} ('{aid}'): Duration {duration} mismatch with planned dates ({p_start} to {p_finish} = {expected_duration} days)"
                )

            c_at = _parse_datetime(row.get("created_at", ""), "created_at", f"activities.csv line {i}")

            act = Activity(
                activity_id=aid,
                wbs_id=wid,
                activity_code=acode,
                name=name,
                level=level,
                discipline=discipline,
                planned_start=p_start,
                planned_finish=p_finish,
                duration=duration,
                status=status,
                created_at=c_at,
                wbs_node=wbs_node,
            )

            activities[aid] = act
            wbs_node.activities.append(act)

        return activities
