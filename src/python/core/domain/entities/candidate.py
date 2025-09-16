from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json, re

from .candidate_record import CandidateRecord
from ..enums.seniority_level import SeniorityLevel as SeniorityLevelEnum
from ..enums.language_proficiency import LanguageProficiency as LanguageProficiencyEnum

ENGLISH_LEVEL_MAP = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
    "BASIC": 2,
    "CONVERSATIONAL": 3,
    "FLUENT": 5,
    "NATIVE": 6,
    "ADVANCED": 5
}

MIN_PREPARED_SCORE = 60
BACKEND_TITLE_KEYWORDS = ("backend", ".net", "c#", "asp.net")
FRONTEND_TITLE_KEYWORDS = ("frontend", "react")
REGEX_ENGLISH_LEVEL = r"\b([ABC][12])\b"
REGEX_DOTNET = r"\b\.net\b"
REGEX_CSHARP = r"\bc#\b"
REGEX_ASPNET = r"\basp\.net\b"
REGEX_ENTITY_FRAMEWORK = r"\bentity framework\b"
REGEX_SQL_SERVER = r"\bsql server\b"
REGEX_AZURE = r"\bazure\b"
KEYWORD_PATTERNS = [
    (REGEX_DOTNET, ".NET"),
    (REGEX_CSHARP, "C#"),
    (REGEX_ASPNET, "ASP.NET"),
    (REGEX_ENTITY_FRAMEWORK, "Entity Framework"),
    (REGEX_SQL_SERVER, "SQL Server"),
    (REGEX_AZURE, "Azure"),
]


@dataclass
class CandidateRecord:
    candidate_id: str
    raw: Dict[str, Any]
    summary: str
    
    schema_version: Optional[str] = None
    generated_at: Optional[str] = None
    source: Optional[str] = None
    
    general_info: Optional[Any] = None
    skill_matrix: List[Any] = field(default_factory=list)
    keyword_coverage: Optional[Any] = None
    languages: List[Any] = field(default_factory=list)
    scores: Optional[Any] = None
    relevance: Optional[Any] = None
    clarity_and_formatting: Optional[Any] = None
    
    strengths: List[str] = field(default_factory=list)
    areas_to_improve: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)
    cleaned_resume_text: Optional[str] = None

    @property
    def prepared(self) -> bool:
        general_score = self.scores.GeneralScore if self.scores else 0
        seniority_level = self.general_info.SeniorityLevel if self.general_info else None
        
        return (general_score and general_score >= MIN_PREPARED_SCORE) or \
               (seniority_level in [
                   SeniorityLevelEnum.MID,
                   SeniorityLevelEnum.SENIOR, 
                   SeniorityLevelEnum.LEAD,
                   SeniorityLevelEnum.PRINCIPAL,
                   SeniorityLevelEnum.STAFF
               ])

    @property
    def english_level(self) -> str:
        return self._detect_english_level()

    @property
    def english_level_num(self) -> int:
        return ENGLISH_LEVEL_MAP.get(self.english_level.upper(), 0)

    def _detect_english_level(self) -> str:
        if self.languages:
            english_language = next(
                (lang for lang in self.languages 
                 if lang.Language and lang.Language.lower() == "english"), 
                None
            )
            if english_language and english_language.Proficiency:
                return english_language.Proficiency.value if hasattr(english_language.Proficiency, 'value') else str(english_language.Proficiency)
        
        if self.general_info and self.general_info.EnglishLevel:
            return self.general_info.EnglishLevel
            
        if self.cleaned_resume_text:
            return self._extract_english_level_from_text(self.cleaned_resume_text)
        
        return "UNKNOWN"

    def _extract_english_level_from_text(self, text: str) -> str:
        text_lower = text.lower()
        
        match = re.search(REGEX_ENGLISH_LEVEL, text_lower, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        if "advanced" in text_lower:
            return "C1"
        elif "upper" in text_lower:
            return "B2"
        elif "intermediate" in text_lower:
            return "B1"
        elif "basic" in text_lower:
            return "A2"
        
        return "UNKNOWN"

    def to_text_blocks(self) -> List[str]:
        blocks = []
        
        title_hint = self._get_title_hint()
        
        candidate_summary = f"[Candidate] {self.candidate_id} {title_hint}\nSummary:\n{self.summary}"
        blocks.append(candidate_summary)
        
        if self.skill_matrix:
            skills_summary = ", ".join([
                skill.SkillName for skill in self.skill_matrix 
                if skill.SkillName
            ])
            blocks.append(f"Skills: {skills_summary}")
        
        derived_keywords = self._get_derived_keywords()
        if derived_keywords:
            blocks.append(f"DerivedKeywords: {', '.join(sorted(derived_keywords))}")
        
        blocks.append(json.dumps(self.raw, ensure_ascii=False))
        
        return blocks

    def _get_title_hint(self) -> str:
        if not self.general_info:
            return ""
            
        title_detected = self.general_info.TitleDetected or ""
        title_predicted = self.general_info.TitlePredicted or ""
        combined_titles = f"{title_detected} {title_predicted}".lower()
        
        if any(keyword in combined_titles for keyword in BACKEND_TITLE_KEYWORDS):
            return "[HINT] backend-dotnet"
        elif any(keyword in combined_titles for keyword in FRONTEND_TITLE_KEYWORDS):
            return "[HINT] frontend"
        
        return ""

    def _get_derived_keywords(self) -> set[str]:
        combined_text = f"{self.cleaned_resume_text or ''} {self.summary}"
        derived_keywords = set()
        
        for regex_pattern, keyword_name in KEYWORD_PATTERNS:
            if re.search(regex_pattern, combined_text, re.IGNORECASE):
                derived_keywords.add(keyword_name)
        
        return derived_keywords

    def _create_base_metadata(self) -> Dict[str, Any]:
        return {
            "type": "candidate",
            "candidate_id": self.candidate_id,
            "prepared": self.prepared,
            "english_level": self.english_level,
            "english_level_num": self.english_level_num,
            "general_score": self.scores.GeneralScore if self.scores else 0,
            "seniority_level": self.general_info.SeniorityLevel.value if self.general_info and self.general_info.SeniorityLevel else "Unknown",
            "skills_count": len(self.skill_matrix),
            "years_experience": self.general_info.YearsExperience if self.general_info else 0
        }
