from dataclasses import dataclass, field
from typing import List
@dataclass
class Result:
    language: str = None
    speaker_number_raw: str = None # e.g., "about 1,000"
    speaker_number_numeric: int = None # cleaned
    speaker_number_type: str = None # estimate, range
    speaker_number_min: int = None
    speaker_number_max: int = None
    vitality_status: str = None #endangered, vulnerable, threatened
    vitality_certainty: int = None # percentage
    speaker_number_year: int = None #year that number was last updated
    speaker_source: str = None #domain name
    source_category: str = None #eg. primary, secondary, tertiary
    source_type: str = None # eg. expert-curated, community-curated, automated
    access_route: str = None # direct, indirect, unverifiable
    source_confidence: int = None # number
    notes: str = None 
    source_urls: List[str] = field(default_factory= list) # list of urls
    

