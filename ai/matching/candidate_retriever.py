"""
L5/L6 Candidate Retrieval Module for SIH26122.

Performs deterministic candidate retrieval for extracted progress events (ExtractedProgressEvent)
against normalized schedule activities (ScheduleDataset / ActivityContext). Filters strictly to
L5 and L6 schedule activities and produces explainable retrieval signals.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Set, Union

from ai.data.schedule_context import ActivityContext, ScheduleContextBuilder
from ai.data.schedule_loader import ScheduleDataset
from ai.extraction.schemas import ExtractedProgressEvent


@dataclass
class RetrievedCandidate:
    """
    Structured candidate activity retrieved for a progress event.
    """
    activity_id: str
    activity_code: str
    name: str
    level: str  # Must be L5 or L6
    discipline: str
    retrieval_score: float
    retrieval_reasons: List[str] = field(default_factory=list)
    activity_context: Optional[ActivityContext] = field(default=None, repr=False)


class CandidateRetriever:
    """Deterministic retriever for finding L5/L6 candidate schedule activities."""

    STOP_WORDS: Set[str] = {
        "and", "the", "for", "in", "on", "at", "to", "a", "an", "of", "with", "as",
        "by", "is", "was", "are", "were", "be", "been", "completed", "done", "finished",
        "today", "per", "activity", "under", "team", "crew", "log", "report", "completed"
    }

    @classmethod
    def retrieve_candidates(
        cls,
        event: ExtractedProgressEvent,
        schedule_target: Union[ScheduleDataset, List[ActivityContext], Dict[str, ActivityContext]],
        top_k: int = 5,
        min_score_threshold: float = 0.05,
    ) -> List[RetrievedCandidate]:
        """
        Retrieve top-K L5/L6 candidate activities for an extracted progress event.
        
        Args:
            event: Extracted progress event.
            schedule_target: ScheduleDataset, list of ActivityContexts, or dict of ActivityContexts.
            top_k: Maximum number of candidates to return.
            min_score_threshold: Minimum score cutoff for candidates.
        """
        # Resolve target to List[ActivityContext]
        if isinstance(schedule_target, ScheduleDataset):
            contexts = ScheduleContextBuilder.build_schedule_context(schedule_target)
        elif isinstance(schedule_target, dict):
            contexts = list(schedule_target.values())
        else:
            contexts = schedule_target

        candidates: List[RetrievedCandidate] = []

        # Tokenize event text and activity description
        event_text = f"{event.activity_description} {event.extracted_text or ''} {event.location or ''}"
        event_tokens = cls._tokenize(event_text)

        # Check explicit activity code in event text (e.g. CIV-001, PIP-081, etc.)
        explicit_codes = set(re.findall(r"\b[A-Z]{3}-\d{3}\b", event_text.upper()))

        for ctx in contexts:
            # STRICT FILTER 1: Only L5 and L6 activities can be candidates!
            if ctx.level not in ("L5", "L6"):
                continue

            score = 0.0
            reasons: List[str] = []

            # Signal 1: Explicit activity code match
            if ctx.activity_code in explicit_codes or ctx.activity_id in explicit_codes:
                score += 0.60
                reasons.append(f"explicit_code_match:{ctx.activity_code}")

            # Signal 2: Discipline match
            if event.discipline:
                if event.discipline.lower() == ctx.discipline.lower():
                    score += 0.25
                    reasons.append(f"discipline_match:{ctx.discipline}")
                else:
                    # Penalty for discipline mismatch when discipline is explicitly specified
                    score -= 0.20
                    reasons.append(f"discipline_mismatch:{event.discipline}_vs_{ctx.discipline}")

            # Signal 3: Keyword overlap with activity name
            act_name_tokens = cls._tokenize(ctx.name)
            wbs_tokens = cls._tokenize(ctx.wbs_path_str)

            name_overlap = event_tokens.intersection(act_name_tokens)
            if name_overlap:
                overlap_ratio = len(name_overlap) / max(len(act_name_tokens), 1)
                overlap_score = min(0.35, overlap_ratio * 0.35)
                score += overlap_score
                reasons.append(f"name_keyword_overlap:{','.join(sorted(name_overlap))}")

            # Signal 4: Location / WBS path overlap
            wbs_overlap = (event_tokens.intersection(wbs_tokens)) - name_overlap
            if wbs_overlap:
                score += 0.10
                reasons.append(f"wbs_path_overlap:{','.join(sorted(wbs_overlap))}")

            # Filter candidates below threshold
            if score >= min_score_threshold:
                candidates.append(
                    RetrievedCandidate(
                        activity_id=ctx.activity_id,
                        activity_code=ctx.activity_code,
                        name=ctx.name,
                        level=ctx.level,
                        discipline=ctx.discipline,
                        retrieval_score=round(score, 4),
                        retrieval_reasons=reasons,
                        activity_context=ctx,
                    )
                )

        # Sort deterministically by score descending, then activity_id ascending
        candidates.sort(key=lambda c: (-c.retrieval_score, c.activity_id))

        return candidates[:top_k]

    @classmethod
    def _tokenize(cls, text: str) -> Set[str]:
        """Normalize text and return set of clean tokens."""
        if not text:
            return set()
        clean = re.sub(r"[^\w\s-]", " ", text.lower())
        tokens = clean.split()
        return {t for t in tokens if len(t) > 1 and t not in cls.STOP_WORDS}
