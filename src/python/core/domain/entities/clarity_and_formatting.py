from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ClarityAndFormatting:
    ClarityScore: Optional[float] = None
    FormattingScore: Optional[float] = None
    SpellingErrors: Optional[int] = None