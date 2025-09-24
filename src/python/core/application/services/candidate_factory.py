import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path

from ...domain.entities.candidate_record import (
    CandidateRecord, GeneralInfo, Skill, KeywordCoverage, Language,
    Scores, Relevance, ClarityAndFormatting
)
from ...domain.entities.candidate import Candidate
from ...domain.enums.seniority_level import SeniorityLevel as SeniorityLevelEnum
from ...domain.enums.language_proficiency import LanguageProficiency as LanguageProficiencyEnum
from ...domain.enums.overall_fit_level import OverallFitLevel as OverallFitLevelEnum
from .schema_validation_service import SchemaValidationService


class CandidateFactory:

    def __init__(self, validate_schema: bool = True):
        self.validate_schema = validate_schema
        if validate_schema:
            self.validator = SchemaValidationService()
    
    def from_json(self, data: Dict[str, Any]) -> CandidateRecord:
        if self.validate_schema:
            if not self.validator.validate_json(data):
                errors = self.validator.get_validation_errors(data)
                raise ValueError(f"JSON data doesn't match schema: {errors}")
        
        return CandidateRecord(
            Summary=data.get('Summary', ''),
            schemaVersion=data.get('schemaVersion', '1.0'),
            generatedAt=self._parse_datetime(data.get('generatedAt')),
            source=data.get('source'),
            GeneralInfo=self._parse_general_info(data.get('GeneralInfo')),
            SkillMatrix=self._parse_skill_matrix(data.get('SkillMatrix')),
            KeywordCoverage=self._parse_keyword_coverage(data.get('KeywordCoverage')),
            Languages=self._parse_languages(data.get('Languages')),
            Scores=self._parse_scores(data.get('Scores')),
            Relevance=self._parse_relevance(data.get('Relevance')),
            ClarityAndFormatting=self._parse_clarity_formatting(data.get('ClarityAndFormatting')),
            Strengths=data.get('Strengths'),
            AreasToImprove=data.get('AreasToImprove'),
            Tips=data.get('Tips'),
            CleanedResumeText=data.get('CleanedResumeText')
        )
    
    def from_json_file(self, file_path: Union[str, Path]) -> CandidateRecord:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return self.from_json(data)
    
    def create_candidate(self, candidate_record: CandidateRecord, candidate_id: str, raw_data: Optional[Dict[str, Any]] = None) -> Candidate:
        return Candidate.from_candidate_record(candidate_record, candidate_id, raw_data)
    
    def from_json_to_candidate(self, data: Dict[str, Any], candidate_id: str) -> Candidate:
        candidate_record = self.from_json(data)
        return self.create_candidate(candidate_record, candidate_id, data)
    
    def from_json_file_to_candidate(self, file_path: Union[str, Path], candidate_id: str) -> Candidate:
        candidate_record = self.from_json_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        return self.create_candidate(candidate_record, candidate_id, raw_data)
    
    def to_json(self, resume_result: CandidateRecord) -> Dict[str, Any]:
        if self.validate_schema:
            if not self.validator.validate_candidate_record(resume_result):
                raise ValueError("CandidateRecord instance doesn't match schema")

        return self.validator._to_dict(resume_result) if self.validate_schema else resume_result.to_dict()
    
    def to_json_file(self, resume_result: CandidateRecord, file_path: Union[str, Path]):
        data = self.to_json(resume_result)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            if value.endswith('Z'):
                value = value[:-1] + '+00:00'
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    
    def _parse_general_info(self, data: Optional[Dict[str, Any]]) -> Optional[GeneralInfo]:
        if not data:
            return None

        return GeneralInfo(
            CandidateId=data.get('CandidateId'),
            Fullname=data.get('Fullname'),
            TitleDetected=data.get('TitleDetected'),
            TitlePredicted=data.get('TitlePredicted'),
            SeniorityLevel=self._parse_enum(data.get('SeniorityLevel'), SeniorityLevelEnum),
            YearsExperience=data.get('YearsExperience'),
            RelevantYears=data.get('RelevantYears'),
            IndustryMatch=data.get('IndustryMatch'),
            TrajectoryPattern=data.get('TrajectoryPattern'),
            MainIndustry=data.get('MainIndustry'),
            EnglishLevel=data.get('EnglishLevel'),
            OtherLanguages=self._parse_languages(data.get('OtherLanguages')),
            Location=data.get('Location')
        )
    
    def _parse_skill_matrix(self, data: Optional[List[Dict[str, Any]]]) -> Optional[List[Skill]]:
        if not data:
            return None

        return [
            Skill(
                SkillName=skill.get('SkillName', ''),
                SkillLevel=skill.get('SkillLevel'),
                Years=skill.get('Years'),
                Evidence=skill.get('Evidence')
            )
            for skill in data
        ]
    
    def _parse_keyword_coverage(self, data: Optional[Dict[str, Any]]) -> Optional[KeywordCoverage]:
        if not data:
            return None

        return KeywordCoverage(
            KeywordsDetected=data.get('KeywordsDetected'),
            KeywordsMissing=data.get('KeywordsMissing'),
            Density=data.get('Density'),
            Context=data.get('Context')
        )
    
    def _parse_languages(self, data: Optional[List[Dict[str, Any]]]) -> Optional[List[Language]]:
        if not data:
            return None

        return [
            Language(
                Language=lang.get('Language'),
                Proficiency=self._parse_enum(lang.get('Proficiency'), LanguageProficiencyEnum),
                Evidence=lang.get('Evidence')
            )
            for lang in data
        ]
    
    def _parse_scores(self, data: Optional[Dict[str, Any]]) -> Optional[Scores]:
        if not data:
            return None

        return Scores(
            GeneralScore=data.get('GeneralScore'),
            ATSCompatibility=data.get('ATSCompatibility'),
            ClarityScore=data.get('ClarityScore'),
            FormattingScore=data.get('FormattingScore'),
            KeywordDensity=data.get('KeywordDensity'),
            EnglishProficiency=data.get('EnglishProficiency'),
            SeniorityMatch=data.get('SeniorityMatch'),
            SkillCoverage=data.get('SkillCoverage'),
            AchievementsQuantification=data.get('AchievementsQuantification'),
            SoftSkillsCoverage=data.get('SoftSkillsCoverage')
        )
    
    def _parse_relevance(self, data: Optional[Dict[str, Any]]) -> Optional[Relevance]:
        if not data:
            return None

        overall_fit = data.get('OverallFit')
        if isinstance(overall_fit, str):
            overall_fit = self._parse_enum(overall_fit, OverallFitLevelEnum)

        return Relevance(
            TitleMatch=data.get('TitleMatch'),
            ResponsibilityMatch=data.get('ResponsibilityMatch'),
            OverallFit=overall_fit
        )
    
    def _parse_clarity_formatting(self, data: Optional[Dict[str, Any]]) -> Optional[ClarityAndFormatting]:
        if not data:
            return None

        return ClarityAndFormatting(
            ClarityScore=data.get('ClarityScore'),
            FormattingScore=data.get('FormattingScore'),
            SpellingErrors=data.get('SpellingErrors')
        )
    
    def _parse_enum(self, value: Optional[str], enum_class) -> Optional[Any]:
        if value is None:
            return None
        try:
            return enum_class(value)
        except (ValueError, TypeError):
            return None