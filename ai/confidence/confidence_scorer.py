"""
Confidence Scoring Module for SIH26122.

Evaluates how reliable an extracted field report event -> L5/L6 schedule activity 
match decision is, computing an explainable confidence_score in [0.0, 1.0] and 
confidence_level (HIGH, MEDIUM, LOW) based on multi-signal evidence, penalties, and caps.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from ai.extraction.schemas import ExtractedProgressEvent, ExtractionStatus
from ai.matching.matcher import MatchResult, MatchStatus


class ConfidenceLevel(str, Enum):
    """Categorical confidence level."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ConfidenceResult:
    """
    Structured result of confidence evaluation for an activity match decision.
    """
    confidence_score: float
    confidence_level: ConfidenceLevel
    match_status: MatchStatus
    matched_activity_id: Optional[str]
    matched_activity_code: Optional[str]
    signal_breakdown: Dict[str, float]
    confidence_reasons: List[str] = field(default_factory=list)
    match_result: Optional[MatchResult] = field(default=None, repr=False)


class ConfidenceScorer:
    """
    Local, deterministic multi-signal confidence scorer for AI activity matching.
    """

    HIGH_THRESHOLD: float = 0.80
    MEDIUM_THRESHOLD: float = 0.50

    DEFAULT_WEIGHTS: Dict[str, float] = {
        "match_score": 0.30,
        "semantic_similarity": 0.20,
        "discipline_match": 0.15,
        "explicit_code": 0.15,
        "location_wbs": 0.10,
        "extraction_quality": 0.10,
    }

    @classmethod
    def calculate_confidence(
        cls,
        event: ExtractedProgressEvent,
        match_result: MatchResult,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> ConfidenceResult:
        """
        Calculate explainable confidence score and level for a match result.
        
        Args:
            event: Extracted progress event.
            match_result: MatchResult object from ActivityMatcher.
            custom_weights: Optional dictionary overriding signal weights.
        """
        weights = custom_weights or cls.DEFAULT_WEIGHTS

        # Edge Case 1: MatchStatus.NO_MATCH strictly returns 0.0 confidence and LOW level
        if match_result.match_status == MatchStatus.NO_MATCH:
            return ConfidenceResult(
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.LOW,
                match_status=MatchStatus.NO_MATCH,
                matched_activity_id=None,
                matched_activity_code=None,
                signal_breakdown={k: 0.0 for k in weights},
                confidence_reasons=["no_matched_activity_candidate"],
                match_result=match_result,
            )

        signal_breakdown: Dict[str, float] = {}
        reasons: List[str] = list(match_result.match_reasons)
        raw_score = 0.0

        # Signal 1: Match score from MatchResult
        match_score_norm = max(0.0, min(1.0, match_result.match_score))
        signal_breakdown["match_score"] = round(match_score_norm, 4)
        raw_score += weights.get("match_score", 0.30) * match_score_norm

        # Signal 2: Semantic similarity
        sem_sim_val = 0.0
        for r in match_result.match_reasons:
            if r.startswith("semantic_similarity:"):
                try:
                    sem_sim_val = float(r.split(":")[1])
                except ValueError:
                    pass
        signal_breakdown["semantic_similarity"] = round(sem_sim_val, 4)
        raw_score += weights.get("semantic_similarity", 0.20) * sem_sim_val

        # Signal 3: Discipline agreement
        disc_score = 0.5  # Neutral default if event discipline is missing
        if event.discipline and match_result.matched_discipline:
            if event.discipline.lower() == match_result.matched_discipline.lower():
                disc_score = 1.0
                reasons.append(f"discipline_agreement:{event.discipline}")
            else:
                disc_score = 0.0
                reasons.append(f"discipline_mismatch:{event.discipline}_vs_{match_result.matched_discipline}")
        signal_breakdown["discipline_match"] = disc_score
        raw_score += weights.get("discipline_match", 0.15) * disc_score

        # Signal 4: Explicit activity code evidence
        has_code_evidence = any("explicit_code_match" in r for r in match_result.match_reasons)
        code_score = 1.0 if has_code_evidence else 0.0
        signal_breakdown["explicit_code"] = code_score
        if has_code_evidence:
            reasons.append("explicit_code_evidence_present")
        raw_score += weights.get("explicit_code", 0.15) * code_score

        # Signal 5: Location / WBS path consistency
        has_location_match = any("location_wbs_match_bonus" in r for r in match_result.match_reasons)
        loc_score = 1.0 if has_location_match else (0.5 if not event.location else 0.2)
        signal_breakdown["location_wbs"] = loc_score
        raw_score += weights.get("location_wbs", 0.10) * loc_score

        # Signal 6: Extraction quality status
        if event.extraction_status == ExtractionStatus.COMPLETE:
            ext_score = 1.0
        elif event.extraction_status == ExtractionStatus.PARTIAL:
            ext_score = 0.70
        elif event.extraction_status == ExtractionStatus.AMBIGUOUS:
            ext_score = 0.40
        else:  # NEEDS_REVIEW
            ext_score = 0.20
        signal_breakdown["extraction_quality"] = ext_score
        raw_score += weights.get("extraction_quality", 0.10) * ext_score

        # Apply Penalties
        penalties = 0.0

        # Penalty 1: Ambiguity penalty
        if match_result.match_status == MatchStatus.AMBIGUOUS:
            penalties += 0.25
            reasons.append("ambiguity_penalty_applied")

        # Penalty 2: Needs Review / Conflict penalty
        if event.extraction_status == ExtractionStatus.NEEDS_REVIEW:
            penalties += 0.30
            reasons.append("conflict_needs_review_penalty_applied")

        calculated_confidence = max(0.0, min(1.0, raw_score - penalties))

        # Apply Hard Caps for Safety
        final_confidence = calculated_confidence
        if match_result.match_status == MatchStatus.AMBIGUOUS:
            final_confidence = min(final_confidence, 0.45)
            reasons.append("confidence_capped_due_to_ambiguity")

        if event.extraction_status == ExtractionStatus.NEEDS_REVIEW:
            final_confidence = min(final_confidence, 0.40)
            reasons.append("confidence_capped_due_to_conflict")

        final_confidence = round(final_confidence, 4)

        # Determine Categorical Confidence Level
        if final_confidence >= cls.HIGH_THRESHOLD:
            level = ConfidenceLevel.HIGH
        elif final_confidence >= cls.MEDIUM_THRESHOLD:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return ConfidenceResult(
            confidence_score=final_confidence,
            confidence_level=level,
            match_status=match_result.match_status,
            matched_activity_id=match_result.matched_activity_id,
            matched_activity_code=match_result.matched_activity_code,
            signal_breakdown=signal_breakdown,
            confidence_reasons=reasons,
            match_result=match_result,
        )
