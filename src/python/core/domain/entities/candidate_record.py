from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from dataclasses_json import dataclass_json

from .general_info import GeneralInfo
from .skill import Skill
from .keyword_coverage import KeywordCoverage
from .language import Language
from .scores import Scores
from .relevance import Relevance
from .clarity_and_formatting import ClarityAndFormatting


@dataclass_json
@dataclass
class CandidateRecord:
    Summary: str
    schemaVersion: str = "1.0"
    generatedAt: Optional[datetime] = None
    source: Optional[str] = None
    GeneralInfo: Optional[GeneralInfo] = None
    SkillMatrix: Optional[List[Skill]] = None
    KeywordCoverage: Optional[KeywordCoverage] = None
    Languages: Optional[List[Language]] = None
    Scores: Optional[Scores] = None
    Relevance: Optional[Relevance] = None
    ClarityAndFormatting: Optional[ClarityAndFormatting] = None
    Strengths: Optional[List[str]] = None
    AreasToImprove: Optional[List[str]] = None
    Tips: Optional[List[str]] = None
    CleanedResumeText: Optional[str] = None