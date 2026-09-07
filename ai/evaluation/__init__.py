"""
AI/ML Pipeline Evaluation Module for SIH26122 (Phase 10).

Provides automated dataset-wide evaluation scripts and benchmark reporting for
evaluating extraction, activity matching, confidence scoring, conflict detection,
and multi-modal pipeline execution on synthetic schedule and field report datasets.
"""

from ai.evaluation.evaluator import PipelineEvaluator, run_evaluation

__all__ = [
    "PipelineEvaluator",
    "run_evaluation",
]
