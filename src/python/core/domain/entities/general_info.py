from dataclasses import dataclass
from typing import Optional, List
from dataclasses_json import dataclass_json

from ..enums.seniority_level import SeniorityLevel as SeniorityLevelEnum
from .language import Language


@dataclass_json
@dataclass
class GeneralInfo:
    CandidateId: Optional[str] = None
    Fullname: Optional[str] = None
    TitleDetected: Optional[str] = None
    TitlePredicted: Optional[str] = None
    SeniorityLevel: Optional[SeniorityLevelEnum] = None
    YearsExperience: Optional[float] = None
    RelevantYears: Optional[float] = None
    IndustryMatch: Optional[str] = None
    TrajectoryPattern: Optional[str] = None
    MainIndustry: Optional[str] = None
    EnglishLevel: Optional[str] = None
    OtherLanguages: Optional[List[Language]] = None
    Location: Optional[str] = None