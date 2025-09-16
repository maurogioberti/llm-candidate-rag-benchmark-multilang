from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Scores:
    GeneralScore: Optional[float] = None
    ATSCompatibility: Optional[float] = None
    ClarityScore: Optional[float] = None
    FormattingScore: Optional[float] = None
    KeywordDensity: Optional[float] = None
    EnglishProficiency: Optional[float] = None
    SeniorityMatch: Optional[float] = None
    SkillCoverage: Optional[float] = None
    AchievementsQuantification: Optional[float] = None
    SoftSkillsCoverage: Optional[float] = None