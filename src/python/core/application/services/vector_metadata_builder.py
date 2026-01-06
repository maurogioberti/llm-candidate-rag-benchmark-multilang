from typing import Dict, Any, Optional
from ...domain.entities.candidate_record import CandidateRecord
from ...domain.configuration.vector_metadata_config import VectorMetadataConfig
from .primary_skills_extractor import PrimarySkillsExtractor


class VectorMetadataBuilder:
    def __init__(self, config: VectorMetadataConfig):
        self.config = config
        self.skills_extractor = PrimarySkillsExtractor(config)
    
    def build_candidate_metadata(
        self,
        candidate: CandidateRecord,
        candidate_id: str,
        english_level: str,
        english_level_num: int
    ) -> Dict[str, Any]:
        metadata = {
            self.config.FIELD_TYPE: self.config.TYPE_CANDIDATE,
            self.config.FIELD_CANDIDATE_ID: candidate_id,
            self.config.FIELD_ENGLISH_LEVEL: english_level,
            self.config.FIELD_ENGLISH_LEVEL_NUM: english_level_num,
        }
        
        if candidate.GeneralInfo:
            metadata[self.config.FIELD_SENIORITY_LEVEL] = (
                candidate.GeneralInfo.SeniorityLevel or None
            )
            metadata[self.config.FIELD_YEARS_EXPERIENCE] = (
                candidate.GeneralInfo.YearsExperience if candidate.GeneralInfo.YearsExperience is not None else None
            )
            metadata[self.config.FIELD_RELEVANT_YEARS] = (
                candidate.GeneralInfo.RelevantYears if candidate.GeneralInfo.RelevantYears is not None else None
            )
            metadata[self.config.FIELD_MAIN_INDUSTRY] = (
                candidate.GeneralInfo.MainIndustry or None
            )
        
        metadata[self.config.FIELD_PRIMARY_SKILLS] = self.skills_extractor.extract(candidate)
        
        return metadata
