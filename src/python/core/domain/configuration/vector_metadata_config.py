from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class VectorMetadataConfig:
    FIELD_TYPE: str = "type"
    FIELD_CANDIDATE_ID: str = "candidate_id"
    FIELD_FULLNAME: str = "fullname"
    FIELD_ENGLISH_LEVEL: str = "english_level"
    FIELD_ENGLISH_LEVEL_NUM: str = "english_level_num"
    FIELD_SENIORITY_LEVEL: str = "seniority_level"
    FIELD_YEARS_EXPERIENCE: str = "years_experience"
    FIELD_RELEVANT_YEARS: str = "relevant_years"
    FIELD_MAIN_INDUSTRY: str = "main_industry"
    FIELD_PRIMARY_SKILLS: str = "primary_skills"
    FIELD_SKILL_NAME: str = "skill_name"
    FIELD_SKILL_LEVEL: str = "skill_level"

    TYPE_CANDIDATE: str = "candidate"
    TYPE_SKILL: str = "skill"
    TYPE_LLM_INSTRUCTION: str = "llm_instruction"
    
    primary_skills_max_count: int = 5
    strong_skill_levels: List[str] = None
    
    def __post_init__(self):
        if self.strong_skill_levels is None:
            object.__setattr__(self, 'strong_skill_levels', ["High", "Very High"])


DEFAULT_VECTOR_METADATA_CONFIG = VectorMetadataConfig()
