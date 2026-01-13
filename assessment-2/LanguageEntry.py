from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LanguageEntry:
    language_ID: str
    language: str
    latitude: float
    longitude: float
    links: str
    speaker_number_raw: str
    speaker_number_numeric: float
    speaker_number_type: str
    speaker_number_min: Optional[float]
    speaker_number_max: Optional[float]
    vitality_status: Optional[str]
    vitality_certainty: Optional[str]
    speaker_number_year: Optional[int]
    speaker_source: Optional[str]
    source_category: Optional[str]
    source_type: Optional[str]
    access_route: Optional[str]
    source_confidence: Optional[float]
    source_urls: List[str]
    plotting_data: Optional[float]
    bar_chart_tooltip_value: Optional[float]