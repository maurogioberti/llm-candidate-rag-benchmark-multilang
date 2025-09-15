from dataclasses import dataclass
from typing import Optional, List
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class KeywordCoverage:
    KeywordsDetected: Optional[List[str]] = None
    KeywordsMissing: Optional[List[str]] = None
    Density: Optional[float] = None
    Context: Optional[str] = None