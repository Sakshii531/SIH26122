"""
Pipeline Orchestration & Decision Recommendation Module for SIH26122.

Provides the ReportPipeline orchestrator for executing the complete AI processing 
flow (Extraction -> Matching -> Confidence Scoring -> Conflict Detection -> Decision Recommendation)
and generating structured, explainable PipelineResult outputs.
"""

from ai.pipeline.report_pipeline import (
    PipelineResult,
    RecommendedAction,
    ReportPipeline,
)

__all__ = [
    "RecommendedAction",
    "PipelineResult",
    "ReportPipeline",
]
