from typing import List, Optional
from ...domain.entities.candidate_record import CandidateRecord
from ...domain.enums.skill_level import SkillLevel
from ...domain.configuration.vector_metadata_config import VectorMetadataConfig


class PrimarySkillsExtractor:
    def __init__(self, config: VectorMetadataConfig):
        self.config = config
    
    def extract(self, candidate: CandidateRecord) -> List[str]:
        if not candidate.SkillMatrix:
            return []
        
        primary_skills = []
        
        for skill in candidate.SkillMatrix:
            if not skill.SkillName:
                continue
            
            if skill.SkillLevel in self.config.strong_skill_levels:
                primary_skills.append(skill.SkillName)
        
        return primary_skills[:self.config.primary_skills_max_count]
