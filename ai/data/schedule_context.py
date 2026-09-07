"""
Schedule Context Preparation Module for SIH26122.

Transforms schedule dataset objects (ScheduleDataset, Activity, WBSNode) into
structured, AI-friendly ActivityContext objects containing full WBS hierarchy
breadcrumbs and deterministic textual representations for downstream matching algorithms.
"""

from dataclasses import dataclass, field
import datetime
from typing import Dict, List, Optional

from ai.data.schedule_loader import Activity, ScheduleDataset, WBSNode


@dataclass
class ActivityContext:
    """
    Structured, AI-friendly representation of a schedule activity, combining
    raw activity fields, WBS parent hierarchy breadcrumbs, and a deterministic
    searchable text representation.
    """
    activity_id: str
    activity_code: str
    name: str
    level: str
    discipline: str
    planned_start: datetime.date
    planned_finish: datetime.date
    duration: int
    status: str

    # WBS hierarchy metadata
    wbs_id: str
    wbs_code: str
    wbs_name: str
    wbs_level: str
    wbs_path: List[str]            # Ancestor WBS node names from L1 down to current node
    wbs_path_str: str        # Formatted string: "[L1] Name > [L2] Name > ..."
    wbs_code_path: List[str]       # Ancestor WBS codes
    wbs_code_path_str: str        # Formatted code string: "1 > 1.3 > 1.3.1..."

    # Combined searchable text representation for AI context windows
    context_text: str

    # Reference to original Activity object
    raw_activity: Optional[Activity] = field(default=None, repr=False)


class ScheduleContextBuilder:
    """Builder class for preparing structured ActivityContext records from ScheduleDataset objects."""

    @classmethod
    def build_activity_context(cls, activity: Activity) -> ActivityContext:
        """Build structured context representation for a single Activity."""
        wbs_node = activity.wbs_node

        wbs_path_names: List[str] = []
        wbs_path_codes: List[str] = []

        # Traverse WBS hierarchy upwards from current node to root
        curr = wbs_node
        ancestors: List[WBSNode] = []
        while curr:
            ancestors.append(curr)
            curr = curr.parent

        # Reverse to get top-down order (L1 -> L2 -> ... -> current)
        ancestors.reverse()

        for node in ancestors:
            wbs_path_names.append(f"[{node.level}] {node.name}")
            wbs_path_codes.append(node.code)

        if wbs_path_names:
            wbs_path_str = " > ".join(wbs_path_names)
            wbs_code_path_str = " > ".join(wbs_path_codes)
        elif wbs_node:
            wbs_path_str = f"[{wbs_node.level}] {wbs_node.name}"
            wbs_code_path_str = wbs_node.code
        else:
            wbs_path_str = "N/A"
            wbs_code_path_str = "N/A"

        wbs_id = wbs_node.wbs_id if wbs_node else "N/A"
        wbs_code = wbs_node.code if wbs_node else "N/A"
        wbs_name = wbs_node.name if wbs_node else "N/A"
        wbs_level = wbs_node.level if wbs_node else "N/A"

        # Construct deterministic searchable context text
        context_text_lines = [
            f"Activity Code: {activity.activity_code}",
            f"Activity ID: {activity.activity_id}",
            f"Activity Name: {activity.name}",
            f"Level: {activity.level}",
            f"Discipline: {activity.discipline}",
            f"Status: {activity.status}",
            f"Planned Dates: {activity.planned_start} to {activity.planned_finish} ({activity.duration} days)",
            f"WBS Hierarchy: {wbs_path_str}",
            f"WBS Code Path: {wbs_code_path_str}",
        ]
        context_text = "\n".join(context_text_lines)

        return ActivityContext(
            activity_id=activity.activity_id,
            activity_code=activity.activity_code,
            name=activity.name,
            level=activity.level,
            discipline=activity.discipline,
            planned_start=activity.planned_start,
            planned_finish=activity.planned_finish,
            duration=activity.duration,
            status=activity.status,
            wbs_id=wbs_id,
            wbs_code=wbs_code,
            wbs_name=wbs_name,
            wbs_level=wbs_level,
            wbs_path=wbs_path_names,
            wbs_path_str=wbs_path_str,
            wbs_code_path=wbs_path_codes,
            wbs_code_path_str=wbs_code_path_str,
            context_text=context_text,
            raw_activity=activity,
        )

    @classmethod
    def build_schedule_context(cls, dataset: ScheduleDataset) -> List[ActivityContext]:
        """Build structured context list for all activities in a ScheduleDataset."""
        return [cls.build_activity_context(act) for act in dataset.activities.values()]

    @classmethod
    def build_context_index(cls, dataset: ScheduleDataset) -> Dict[str, ActivityContext]:
        """Build dictionary index mapping activity_id -> ActivityContext for fast lookup."""
        return {
            act_id: cls.build_activity_context(act)
            for act_id, act in dataset.activities.items()
        }
