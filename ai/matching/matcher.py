"""
L5/L6 Activity Matching & Ranking Module for SIH26122.

Ranks L5/L6 schedule activity candidates retrieved by CandidateRetriever and selects
the best match for an ExtractedProgressEvent, producing explainable MatchResult outputs
with clear statuses ('matched', 'no_match', 'ambiguous').
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Dict, List, Optional, Set, Tuple, Union

from ai.data.schedule_context import ActivityContext, ScheduleContextBuilder
from ai.data.schedule_loader import ScheduleDataset
from ai.extraction.schemas import ExtractedProgressEvent
from ai.matching.candidate_retriever import CandidateRetriever, RetrievedCandidate


class MatchStatus(str, Enum):
    """Match decision status."""
    MATCHED = "matched"
    NO_MATCH = "no_match"
    AMBIGUOUS = "ambiguous"


@dataclass
class MatchResult:
    """
    Structured result of activity matching and candidate ranking.
    """
    matched_activity_id: Optional[str]
    matched_activity_code: Optional[str]
    matched_activity_name: Optional[str]
    matched_level: Optional[str]
    matched_discipline: Optional[str]
    match_score: float
    match_status: MatchStatus
    ranked_candidates: List[RetrievedCandidate]
    match_reasons: List[str] = field(default_factory=list)
    matched_context: Optional[ActivityContext] = field(default=None, repr=False)


class ActivityMatcher:
    """Matcher class for ranking L5/L6 activity candidates and determining match status."""

    MATCH_THRESHOLD: float = 0.35
    AMBIGUITY_DELTA: float = 0.08

    @classmethod
    def match_event(
        cls,
        event: ExtractedProgressEvent,
        schedule_target: Union[ScheduleDataset, List[ActivityContext], Dict[str, ActivityContext]],
        top_k: int = 5,
        match_threshold: Optional[float] = None,
        ambiguity_delta: Optional[float] = None,
    ) -> MatchResult:
        """
        Rank candidates and perform activity selection for an extracted progress event.
        
        Args:
            event: ExtractedProgressEvent object.
            schedule_target: ScheduleDataset, list of ActivityContexts, or dict of ActivityContexts.
            top_k: Maximum candidate pool size.
            match_threshold: Score threshold required for a match (default: MATCH_THRESHOLD).
            ambiguity_delta: Score delta threshold below which top 2 candidates are ambiguous (default: AMBIGUITY_DELTA).
        """
        threshold = match_threshold if match_threshold is not None else cls.MATCH_THRESHOLD
        delta = ambiguity_delta if ambiguity_delta is not None else cls.AMBIGUITY_DELTA

        # Step 1: Retrieve candidate pool using Step 6.1 CandidateRetriever
        retrieved_candidates = CandidateRetriever.retrieve_candidates(
            event=event,
            schedule_target=schedule_target,
            top_k=top_k,
            min_score_threshold=0.01,
        )

        if not retrieved_candidates:
            return MatchResult(
                matched_activity_id=None,
                matched_activity_code=None,
                matched_activity_name=None,
                matched_level=None,
                matched_discipline=None,
                match_score=0.0,
                match_status=MatchStatus.NO_MATCH,
                ranked_candidates=[],
                match_reasons=["no_candidates_retrieved"],
                matched_context=None,
            )

        # Step 2: Re-rank candidates with detailed similarity scoring
        rescored_candidates: List[RetrievedCandidate] = []
        for cand in retrieved_candidates:
            ctx = cand.activity_context
            score, reasons = cls._calculate_match_score(event, cand, ctx)

            rescored_candidates.append(
                RetrievedCandidate(
                    activity_id=cand.activity_id,
                    activity_code=cand.activity_code,
                    name=cand.name,
                    level=cand.level,
                    discipline=cand.discipline,
                    retrieval_score=round(score, 4),
                    retrieval_reasons=reasons,
                    activity_context=ctx,
                )
            )

        # Sort rescored candidates descending by score, then activity_id ascending
        rescored_candidates.sort(key=lambda c: (-c.retrieval_score, c.activity_id))

        top_cand = rescored_candidates[0]
        top_score = top_cand.retrieval_score

        # Check threshold
        if top_score < threshold:
            return MatchResult(
                matched_activity_id=None,
                matched_activity_code=None,
                matched_activity_name=None,
                matched_level=None,
                matched_discipline=None,
                match_score=top_score,
                match_status=MatchStatus.NO_MATCH,
                ranked_candidates=rescored_candidates,
                match_reasons=[f"top_score_{top_score:.4f}_below_threshold_{threshold}"],
                matched_context=None,
            )

        # Check explicit code match override for ambiguity
        has_explicit_code = any("explicit_code_match" in r for r in top_cand.retrieval_reasons)

        # Check ambiguity against second candidate
        if len(rescored_candidates) > 1 and not has_explicit_code:
            second_cand = rescored_candidates[1]
            score_diff = top_score - second_cand.retrieval_score
            if score_diff < delta:
                return MatchResult(
                    matched_activity_id=None,
                    matched_activity_code=None,
                    matched_activity_name=None,
                    matched_level=None,
                    matched_discipline=None,
                    match_score=top_score,
                    match_status=MatchStatus.AMBIGUOUS,
                    ranked_candidates=rescored_candidates,
                    match_reasons=[
                        f"top_two_candidates_too_close_diff_{score_diff:.4f}_below_delta_{delta}",
                        f"competing_candidate_1:{top_cand.activity_id}",
                        f"competing_candidate_2:{second_cand.activity_id}",
                    ],
                    matched_context=None,
                )

        # Successful match
        return MatchResult(
            matched_activity_id=top_cand.activity_id,
            matched_activity_code=top_cand.activity_code,
            matched_activity_name=top_cand.name,
            matched_level=top_cand.level,
            matched_discipline=top_cand.discipline,
            match_score=top_score,
            match_status=MatchStatus.MATCHED,
            ranked_candidates=rescored_candidates,
            match_reasons=top_cand.retrieval_reasons,
            matched_context=top_cand.activity_context,
        )

    @classmethod
    def _calculate_match_score(
        cls,
        event: ExtractedProgressEvent,
        candidate: RetrievedCandidate,
        ctx: Optional[ActivityContext],
    ) -> Tuple[float, List[str]]:
        """Calculate fine-grained match score and reasons for a candidate."""
        reasons = list(candidate.retrieval_reasons)
        score = candidate.retrieval_score

        # Text similarity bonus between extracted activity_description and candidate name
        if event.activity_description and candidate.name:
            sim = cls._calculate_text_similarity(event.activity_description, candidate.name)
            if sim > 0.4:
                bonus = min(0.20, sim * 0.20)
                score += bonus
                reasons.append(f"name_similarity_bonus:{sim:.2f}")

        # WBS / Location match bonus
        if event.location and ctx and ctx.wbs_path_str:
            loc_tokens = cls._tokenize(event.location)
            wbs_tokens = cls._tokenize(ctx.wbs_path_str)
            if loc_tokens.intersection(wbs_tokens):
                score += 0.10
                reasons.append("location_wbs_match_bonus")

        # Cap score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, score))
        return final_score, reasons

    @staticmethod
    def _calculate_text_similarity(s1: str, s2: str) -> float:
        """Calculate Jaccard token similarity between two strings."""
        t1 = set(re.findall(r"\w+", s1.lower()))
        t2 = set(re.findall(r"\w+", s2.lower()))
        if not t1 or not t2:
            return 0.0
        intersection = t1.intersection(t2)
        union = t1.union(t2)
        return len(intersection) / len(union)

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        if not text:
            return set()
        clean = re.sub(r"[^\w\s-]", " ", text.lower())
        tokens = clean.split()
        return {t for t in tokens if len(t) > 1}
