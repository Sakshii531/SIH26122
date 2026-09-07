"""
Pipeline Orchestration & Decision Recommendation Module for SIH26122.

Provides the ReportPipeline orchestrator for executing the multi-modal AI processing 
flow (Input Processing / OCR / ASR -> Extraction -> Matching -> Confidence Scoring -> Conflict Detection -> AISuggestion)
and generating structured, explainable AISuggestion outputs.
"""

from ai.pipeline.report_pipeline import (
    PipelineResult,
    RecommendedAction,
    ReportPipeline,
)
from ai.pipeline.suggestion_engine import (
    AISuggestion,
    build_ai_suggestion,
)

__all__ = [
    "RecommendedAction",
    "PipelineResult",
    "ReportPipeline",
    "AISuggestion",
    "build_ai_suggestion",
]
