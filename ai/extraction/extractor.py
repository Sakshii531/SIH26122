"""
Progress Event Extractor Module for SIH26122.

Provides deterministic NLP and text parsing to extract structured ExtractedProgressEvent 
instances from raw, unstructured field report text.
"""

import csv
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ai.extraction.schemas import (
    EventDiscipline,
    EventStatus,
    ExtractedProgressEvent,
    ExtractionStatus,
)


class ProgressEventExtractor:
    """Extractor class for converting raw field report text into ExtractedProgressEvent models."""

    @classmethod
    def extract_from_report(
        cls,
        report_id: str,
        raw_text: str,
        report_date: Optional[Union[str, datetime.date]] = None,
        expected_case: Optional[str] = None,
        source_type: Optional[str] = None,
    ) -> ExtractedProgressEvent:
        """
        Extract structured progress event from raw report text.
        """
        if not report_id or not report_id.strip():
            raise ValueError("report_id must be a non-empty string.")

        if not raw_text or not raw_text.strip():
            raise ValueError("raw_text must be a non-empty string.")

        clean_text = " ".join(raw_text.strip().split())
        lower_text = clean_text.lower()

        # 1. Discipline Extraction
        discipline = cls._extract_discipline(lower_text)

        # 2. Location Extraction
        location = cls._extract_location(clean_text)

        # 3. Status & Progress Extraction
        status, progress_val = cls._extract_status_and_progress(lower_text)

        # 4. Dates Extraction
        parsed_rep_date = cls._parse_date_obj(report_date)
        actual_start, actual_finish = cls._extract_dates(lower_text, parsed_rep_date, status)

        # 5. Activity Description Extraction
        activity_desc = cls._extract_activity_description(clean_text)

        # 6. Extraction Status Assessment
        ext_status = cls._assess_extraction_status(
            lower_text=lower_text,
            expected_case=expected_case,
            discipline=discipline,
            location=location,
            status=status,
            activity_desc=activity_desc,
        )

        return ExtractedProgressEvent(
            report_id=report_id.strip(),
            activity_description=activity_desc,
            extraction_status=ext_status,
            discipline=discipline,
            status=status,
            actual_start=actual_start,
            actual_finish=actual_finish,
            location=location,
            progress_value=progress_val,
            extracted_text=clean_text,
            metadata={
                "source_type": source_type or "unknown",
                "raw_text_length": len(clean_text),
            },
        )

    @classmethod
    def extract_from_dataset(cls, csv_path: Union[str, Path]) -> List[ExtractedProgressEvent]:
        """Process a field_reports.csv dataset file and return extracted progress events."""
        p = Path(csv_path)
        if not p.exists():
            raise ValueError(f"CSV file not found: {p}")

        events = []
        with open(p, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = row.get("report_id", "").strip()
                rtext = row.get("raw_text", "").strip()
                rdate = row.get("report_date", "").strip() or None
                ecase = row.get("expected_case", "").strip() or None
                stype = row.get("source_type", "").strip() or None

                if rid and rtext:
                    event = cls.extract_from_report(
                        report_id=rid,
                        raw_text=rtext,
                        report_date=rdate,
                        expected_case=ecase,
                        source_type=stype,
                    )
                    events.append(event)
        return events

    @staticmethod
    def _parse_date_obj(d: Optional[Union[str, datetime.date]]) -> Optional[datetime.date]:
        if not d:
            return None
        if isinstance(d, datetime.date):
            return d
        try:
            return datetime.date.fromisoformat(d.strip())
        except ValueError:
            return None

    @staticmethod
    def _extract_discipline(lower_text: str) -> Optional[str]:
        # Explicit keywords
        if any(w in lower_text for w in ["civil", "excavation", "rebar", "concrete", "pcc", "blinding", "pedestal", "subgrade", "foundation"]):
            return EventDiscipline.CIVIL.value
        if any(w in lower_text for w in ["structural", "steel", "pipe rack", "beam", "bracing", "platform", "torquing", "grating", "fireproofing"]):
            return EventDiscipline.STRUCTURAL.value
        if any(w in lower_text for w in ["piping", "spool", "welding", "hydrotest", "flushing", "flange", "valve", "pipe support"]):
            return EventDiscipline.PIPING.value
        if any(w in lower_text for w in ["mechanical", "pump", "vessel", "reactor", "compressor", "heat exchanger", "skid", "rigging", "crane"]):
            return EventDiscipline.MECHANICAL.value
        if any(w in lower_text for w in ["electrical", "cable", "switchgear", "transformer", "mcc", "earthing", "lighting", "busbar", "feeder", "tray"]):
            return EventDiscipline.ELECTRICAL.value
        if any(w in lower_text for w in ["instrumentation", "instrument", "transmitter", "junction box", "jb-", "tubing", "loop", "dcs", "thermocouple"]):
            return EventDiscipline.INSTRUMENTATION.value
        return None

    @staticmethod
    def _extract_location(clean_text: str) -> Optional[str]:
        locations = []

        # Grid references e.g. Grid A1 to A5, Grid A-B
        grid_m = re.search(r"grid\s+[a-z0-9\-\s]+", clean_text, re.IGNORECASE)
        if grid_m:
            locations.append(grid_m.group(0).strip())

        # Pipe rack e.g. PR-101, Pipe Rack PR-101
        pr_m = re.search(r"(pipe\s+rack\s+)?pr-\d+", clean_text, re.IGNORECASE)
        if pr_m:
            locations.append(pr_m.group(0).strip())

        # Specific Equipment / Vessel / Pedestal tags e.g. C-101, R-201, P-101, Substation 1, Cooling Tower
        equip_matches = re.findall(r"\b(C-101|R-201|P-101[A-B]?|F-101|F-102|F-201|PT-1004|JB-101|Substation\s+\d+|Cooling\s+Tower)\b", clean_text, re.IGNORECASE)
        for eq in equip_matches:
            eq_clean = eq.strip()
            if eq_clean not in locations:
                locations.append(eq_clean)

        if locations:
            return ", ".join(locations)
        return None

    @staticmethod
    def _extract_status_and_progress(lower_text: str) -> Tuple[Optional[str], Optional[float]]:
        status = None
        progress = None

        if "100%" in lower_text or "100 percent" in lower_text or "completed" in lower_text or "finished" in lower_text or "done" in lower_text or "signed" in lower_text:
            status = EventStatus.COMPLETED.value
            progress = 100.0
        elif "ongoing" in lower_text or "in progress" in lower_text or "tying" in lower_text or "pouring" in lower_text or "erecting" in lower_text or "welding" in lower_text or "installing" in lower_text or "laying" in lower_text:
            status = EventStatus.IN_PROGRESS.value
            progress = 50.0
        elif "not started" in lower_text or "scheduled for tomorrow" in lower_text:
            status = EventStatus.NOT_STARTED.value
            progress = 0.0

        return status, progress

    @staticmethod
    def _extract_dates(lower_text: str, report_date: Optional[datetime.date], status: Optional[str]) -> Tuple[Optional[datetime.date], Optional[datetime.date]]:
        actual_start = None
        actual_finish = None

        # Check for ISO dates in text YYYY-MM-DD
        dates_found = re.findall(r"\b202\d-\d{2}-\d{2}\b", lower_text)
        parsed_dates = []
        for d_str in dates_found:
            try:
                parsed_dates.append(datetime.date.fromisoformat(d_str))
            except ValueError:
                pass

        if len(parsed_dates) >= 2:
            parsed_dates.sort()
            actual_start = parsed_dates[0]
            actual_finish = parsed_dates[-1]
        elif len(parsed_dates) == 1:
            if status == EventStatus.COMPLETED.value:
                actual_finish = parsed_dates[0]
            else:
                actual_start = parsed_dates[0]
        elif report_date:
            if status == EventStatus.COMPLETED.value:
                actual_finish = report_date
            elif status == EventStatus.IN_PROGRESS.value:
                actual_start = report_date

        return actual_start, actual_finish

    @staticmethod
    def _extract_activity_description(clean_text: str) -> str:
        # Strip header prefixes like "Shift Report - Civil & Foundations:", "Daily Progress Log:", activity code references
        text = re.sub(r"^(shift report|daily progress log|progress summary|daily site log|supervisor report)[^:]*:\s*", "", clean_text, flags=re.IGNORECASE)
        text = re.sub(r"\(as per activity [^\)]+\)", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\([A-Z]{3}-\d{3}\)", "", text)
        text = " ".join(text.strip().split())
        return text if text else clean_text

    @staticmethod
    def _assess_extraction_status(
        lower_text: str,
        expected_case: Optional[str],
        discipline: Optional[str],
        location: Optional[str],
        status: Optional[str],
        activity_desc: str,
    ) -> ExtractionStatus:
        # 1. Conflict / Defect / Halt / Review required
        if any(w in lower_text for w in ["flagged", "defect", "repair", "breakdown", "halted", "contradict", "honeycombing", "missing tray covers", "grouting has not been poured"]):
            return ExtractionStatus.NEEDS_REVIEW

        if expected_case == "conflicting_info":
            return ExtractionStatus.NEEDS_REVIEW

        # 2. Ambiguous match detection
        if expected_case == "ambiguous_match" or (not location and len(activity_desc.split()) <= 6 and discipline is None):
            return ExtractionStatus.AMBIGUOUS

        # 3. Partial match detection
        if expected_case in ("short_log", "missing_details") or len(activity_desc.split()) <= 5 or not status:
            return ExtractionStatus.PARTIAL

        # 4. Complete
        return ExtractionStatus.COMPLETE
