from typing import List, Dict, Any
from langchain_core.documents import Document

from ...domain.entities.candidate_record import CandidateRecord
from ...domain.enums.skill_level import SkillLevel
from ...domain.configuration.vector_metadata_config import VectorMetadataConfig


class SkillDocumentBuilder:
    def __init__(self, config: VectorMetadataConfig):
        self._config = config
    
    def build_skill_documents(
        self,
        candidate: CandidateRecord,
        candidate_id: str,
        seniority_level: str,
        years_experience: int
    ) -> List[Document]:
        documents = []
        
        if not candidate.SkillMatrix:
            return documents
        
        for skill in candidate.SkillMatrix:
            if not skill.SkillName or not skill.SkillLevel:
                continue
            
            skill_level_enum = SkillLevel.from_string(skill.SkillLevel)
            
            if not skill_level_enum.is_strong():
                continue
            
            metadata = self._build_skill_metadata(
                candidate_id=candidate_id,
                skill_name=skill.SkillName,
                skill_level=skill.SkillLevel,
                seniority_level=seniority_level,
                years_experience=years_experience
            )
            
            page_content = self._build_skill_content(
                skill_name=skill.SkillName,
                skill_level=skill.SkillLevel,
                evidence=skill.Evidence
            )
            
            documents.append(Document(
                page_content=page_content,
                metadata=metadata
            ))
        
        return documents
    
    def _build_skill_metadata(
        self,
        candidate_id: str,
        skill_name: str,
        skill_level: str,
        seniority_level: str,
        years_experience: int
    ) -> Dict[str, Any]:
        return {
            self._config.FIELD_TYPE: self._config.TYPE_SKILL,
            self._config.FIELD_CANDIDATE_ID: candidate_id,
            self._config.FIELD_SKILL_NAME: skill_name,
            self._config.FIELD_SKILL_LEVEL: skill_level,
            self._config.FIELD_SENIORITY_LEVEL: seniority_level,
            self._config.FIELD_YEARS_EXPERIENCE: years_experience
        }
    
    def _build_skill_content(
        self,
        skill_name: str,
        skill_level: str,
        evidence: str = None
    ) -> str:
        content = f"{skill_name} ({skill_level})"
        
        if evidence:
            content += f": {evidence}"
        
        return content
