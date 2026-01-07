from typing import List, Dict, Any, Optional
from ...domain.entities.parsed_query import ParsedQuery
from ...domain.enums.seniority_level import SeniorityLevel


class MetadataFilterBuilder:
    def __init__(
        self,
        candidate_id_field: str,
        seniority_field: str,
        years_experience_field: str,
        skill_name_field: str,
        type_field: str,
        type_skill: str
    ):
        self._candidate_id_field = candidate_id_field
        self._seniority_field = seniority_field
        self._years_experience_field = years_experience_field
        self._skill_name_field = skill_name_field
        self._type_field = type_field
        self._type_skill = type_skill
        self._seniority_order = {
            SeniorityLevel.INTERN: 0,
            SeniorityLevel.JUNIOR: 1,
            SeniorityLevel.MID: 2,
            SeniorityLevel.SENIOR: 3,
            SeniorityLevel.LEAD: 4,
            SeniorityLevel.PRINCIPAL: 5,
            SeniorityLevel.STAFF: 6
        }
    
    def build_candidate_filters(self, parsed_query: ParsedQuery) -> List[Dict[str, Any]]:
        filters = []
        
        if parsed_query.min_seniority_level:
            seniority_filters = self._build_seniority_filter(parsed_query.min_seniority_level)
            if seniority_filters:
                filters.extend(seniority_filters)
        
        if parsed_query.min_years_experience:
            years_filter = self._build_years_filter(parsed_query.min_years_experience)
            if years_filter:
                filters.append(years_filter)
        
        return filters
    
    def build_technology_filters(self, parsed_query: ParsedQuery) -> Optional[Dict[str, Any]]:
        if not parsed_query.required_technologies:
            return None
        
        return {
            "$and": [
                {self._type_field: self._type_skill},
                {self._skill_name_field: {"$in": parsed_query.required_technologies}}
            ]
        }
    
    def filter_aggregated_candidates(
        self,
        candidates: List,
        parsed_query: ParsedQuery
    ) -> List:
        filtered = []
        
        for candidate in candidates:
            if self._matches_filters(candidate, parsed_query):
                filtered.append(candidate)
        
        return filtered
    
    def _matches_filters(self, candidate, parsed_query: ParsedQuery) -> bool:
        if parsed_query.min_seniority_level:
            candidate_seniority_str = candidate.metadata.get(self._seniority_field)
            if not self._meets_seniority_requirement(
                candidate_seniority_str,
                parsed_query.min_seniority_level
            ):
                return False
        
        if parsed_query.min_years_experience:
            candidate_years = candidate.metadata.get(self._years_experience_field, 0)
            if not isinstance(candidate_years, (int, float)) or candidate_years < parsed_query.min_years_experience:
                return False
        
        return True
    
    def _meets_seniority_requirement(
        self,
        candidate_seniority_str: Optional[str],
        required_seniority: SeniorityLevel
    ) -> bool:
        if not candidate_seniority_str:
            return False
        
        candidate_seniority = self._parse_seniority(candidate_seniority_str)
        if not candidate_seniority:
            return False
        
        required_level = self._seniority_order.get(required_seniority, 0)
        candidate_level = self._seniority_order.get(candidate_seniority, 0)
        
        return candidate_level >= required_level
    
    def _parse_seniority(self, seniority_str: str) -> Optional[SeniorityLevel]:
        seniority_map = {
            "Intern": SeniorityLevel.INTERN,
            "Junior": SeniorityLevel.JUNIOR,
            "Mid": SeniorityLevel.MID,
            "Senior": SeniorityLevel.SENIOR,
            "Lead": SeniorityLevel.LEAD,
            "Principal": SeniorityLevel.PRINCIPAL,
            "Staff": SeniorityLevel.STAFF
        }
        return seniority_map.get(seniority_str)
    
    def _build_seniority_filter(self, min_seniority: SeniorityLevel) -> List[Dict[str, Any]]:
        min_level = self._seniority_order.get(min_seniority, 0)
        
        valid_seniorities = []
        for seniority, level in self._seniority_order.items():
            if level >= min_level:
                valid_seniorities.append(seniority.value)
        
        if not valid_seniorities:
            return []
        
        return [{self._seniority_field: {"$in": valid_seniorities}}]
    
    def _build_years_filter(self, min_years: int) -> Dict[str, Any]:
        return {self._years_experience_field: {"$gte": min_years}}
