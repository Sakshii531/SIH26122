"""
Conflict Detection Module for SIH26122.

Provides offline, deterministic conflict detection for evaluating single field reports 
and multi-report activity streams to detect progress contradictions, date inversions, 
status mismatches, defects, and cross-report inconsistencies.
"""

from ai.conflict.conflict_detector import (
    ConflictDetail,
    ConflictDetector,
    ConflictResult,
    ConflictSeverity,
    ConflictType,
)

__all__ = [
    "ConflictType",
    "ConflictSeverity",
    "ConflictDetail",
    "ConflictResult",
    "ConflictDetector",
]
