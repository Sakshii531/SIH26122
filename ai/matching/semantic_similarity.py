"""
Local Semantic Similarity Module for SIH26122.

Provides deterministic, offline, lightweight text normalization and semantic similarity
calculation for activity descriptions using scikit-learn TF-IDF character/word n-grams
and difflib sequence matching without requiring external API keys or cloud services.
"""

import difflib
import math
import re
from typing import Dict, List, Optional, Set

from sklearn.feature_extraction.text import TfidfVectorizer


class SemanticSimilarityCalculator:
    """
    Local, deterministic semantic similarity calculator for engineering & construction
    activity descriptions.
    """

    SYNONYM_MAP: Dict[str, str] = {
        "poured": "pour",
        "pouring": "pour",
        "cast": "pour",
        "casting": "pour",
        "welded": "weld",
        "welding": "weld",
        "erected": "erect",
        "erection": "erect",
        "erecting": "erect",
        "assembled": "assemble",
        "assembly": "assemble",
        "assembling": "assemble",
        "tied": "tie",
        "tying": "tie",
        "excavated": "excavate",
        "excavation": "excavate",
        "excavating": "excavate",
        "installed": "install",
        "installation": "install",
        "installing": "install",
        "rebar": "reinforcement",
        "shuttering": "formwork",
        "rcc": "concrete",
        "pcc": "concrete",
        "spool": "piping",
        "spools": "piping",
        "c-101": "c101",
        "r-201": "r201",
        "p-101": "p101",
        "pr-101": "pr101",
    }

    STOP_WORDS: Set[str] = {
        "a", "an", "and", "are", "as", "at", "be", "been", "by", "completed", "done",
        "finished", "for", "in", "is", "of", "on", "or", "the", "to", "was", "were",
        "with", "today", "per", "activity", "under", "team", "crew", "log", "report"
    }

    @classmethod
    def normalize_text(cls, text: Optional[str]) -> str:
        """
        Normalize text for similarity calculation: lowercase, strip punctuation,
        apply canonical synonym mapping, and remove stop words.
        """
        if not text:
            return ""

        clean = re.sub(r"[^\w\s-]", " ", text.lower())
        tokens = clean.split()

        normalized_tokens = []
        for t in tokens:
            t_clean = t.strip("-")
            if not t_clean or t_clean in cls.STOP_WORDS:
                continue
            canonical = cls.SYNONYM_MAP.get(t_clean, t_clean)
            normalized_tokens.append(canonical)

        return " ".join(normalized_tokens)

    @classmethod
    def calculate_similarity(cls, text1: Optional[str], text2: Optional[str]) -> float:
        """
        Calculate bounded, deterministic semantic similarity score in [0.0, 1.0]
        between two text strings.
        """
        norm1 = cls.normalize_text(text1)
        norm2 = cls.normalize_text(text2)

        if not norm1 or not norm2:
            return 0.0

        if norm1 == norm2:
            return 1.0

        # Component 1: Character N-Gram TF-IDF Cosine Similarity
        tfidf_sim = cls._tfidf_cosine_similarity(norm1, norm2)

        # Component 2: difflib Sequence Matching Ratio
        seq_sim = difflib.SequenceMatcher(None, norm1, norm2).ratio()

        # Component 3: Token Jaccard Overlap
        t1 = set(norm1.split())
        t2 = set(norm2.split())
        jaccard_sim = len(t1.intersection(t2)) / max(len(t1.union(t2)), 1)

        # Weighted combination of local similarity signals
        combined = (0.50 * tfidf_sim) + (0.30 * jaccard_sim) + (0.20 * seq_sim)

        # Ensure bounded [0.0, 1.0] output rounded deterministically
        bounded_score = max(0.0, min(1.0, combined))
        return round(bounded_score, 4)

    @classmethod
    def _tfidf_cosine_similarity(cls, norm1: str, norm2: str) -> float:
        """Compute cosine similarity using TF-IDF character n-grams."""
        try:
            vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4))
            tfidf_matrix = vectorizer.fit_transform([norm1, norm2])
            dense = tfidf_matrix.toarray()

            vec1 = dense[0]
            vec2 = dense[1]

            dot_product = float(sum(v1 * v2 for v1, v2 in zip(vec1, vec2)))
            norm_a = math.sqrt(sum(v * v for v in vec1))
            norm_b = math.sqrt(sum(v * v for v in vec2))

            if norm_a == 0.0 or norm_b == 0.0:
                return 0.0

            return dot_product / (norm_a * norm_b)
        except Exception:
            return 0.0
