from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json

from ..enums.language_proficiency import LanguageProficiency as LanguageProficiencyEnum


@dataclass_json
@dataclass
class Language:
    Language: Optional[str] = None
    Proficiency: Optional[LanguageProficiencyEnum] = None
    Evidence: Optional[str] = None