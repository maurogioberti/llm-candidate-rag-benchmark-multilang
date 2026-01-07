from typing import List, Optional
from ...domain.entities.ranked_candidate import RankedCandidate
from ...domain.entities.parsed_query import ParsedQuery
from ...domain.configuration.ranking_weights import RankingWeights
from ...domain.enums.seniority_level import SeniorityLevel
from ...domain.enums.query_intent import QueryIntent
from ..services.candidate_aggregator import AggregatedCandidate


class CandidateRanker:
    _SENIORITY_ORDINALS = {
        SeniorityLevel.INTERN: 0,
        SeniorityLevel.JUNIOR: 1,
        SeniorityLevel.MID: 2,
        SeniorityLevel.SENIOR: 3,
        SeniorityLevel.LEAD: 4,
        SeniorityLevel.PRINCIPAL: 5,
        SeniorityLevel.STAFF: 6
    }
    
    _LEADERSHIP_KEYWORDS = ["lead", "principal", "staff", "manager", "director", "head", "architect"]
    _LEADERSHIP_RELEVANT_INTENTS = {QueryIntent.FIND_BEST}
    _MAX_NORMALIZED_SCORE = 1.0
    _MIN_NORMALIZED_SCORE = 0.0
    
    def __init__(self, weights: RankingWeights):
        self._weights = weights
    
    def rank(
        self, 
        candidates: List[AggregatedCandidate], 
        parsed_query: ParsedQuery
    ) -> List[RankedCandidate]:
        ranked = []
        
        for candidate in candidates:
            technical_score = self._calculate_technical_score(
                candidate, 
                parsed_query.required_technologies
            )
            seniority_score = self._calculate_seniority_score(
                candidate, 
                parsed_query.min_seniority_level
            )
            leadership_score = (
                self._calculate_leadership_score(candidate) 
                if self._is_leadership_relevant(parsed_query) 
                else self._MIN_NORMALIZED_SCORE
            )
            experience_score = self._calculate_experience_score(
                candidate, 
                parsed_query.min_years_experience
            )
            
            total_score = (
                technical_score * self._weights.technical_match_weight +
                seniority_score * self._weights.seniority_match_weight +
                leadership_score * self._weights.leadership_signals_weight +
                experience_score * self._weights.experience_match_weight
            )
            
            ranked.append(RankedCandidate(
                candidate_id=candidate.candidate_id,
                documents=candidate.documents,
                metadata=candidate.metadata,
                max_score=candidate.max_score,
                all_scores=candidate.all_scores,
                technical_score=technical_score,
                seniority_score=seniority_score,
                leadership_score=leadership_score,
                experience_score=experience_score,
                total_score=total_score
            ))
        
        return sorted(ranked, key=lambda c: c.total_score, reverse=True)
    
    def _calculate_technical_score(
        self, 
        candidate: AggregatedCandidate, 
        required_technologies: List[str]
    ) -> float:
        if not required_technologies:
            return self._MAX_NORMALIZED_SCORE
        
        # Primary skills stored as comma-separated string for Chroma compatibility
        primary_skills_str = candidate.metadata.get("primary_skills", "")
        if not primary_skills_str:
            return self._MIN_NORMALIZED_SCORE
        
        primary_skills = [s.strip() for s in primary_skills_str.split(",") if s.strip()]
        primary_skills_lower = [skill.lower() for skill in primary_skills]
        matched_count = sum(
            1 for tech in required_technologies 
            if any(tech.lower() in skill for skill in primary_skills_lower)
        )
        
        return min(matched_count / len(required_technologies), self._MAX_NORMALIZED_SCORE)
    
    def _calculate_seniority_score(
        self, 
        candidate: AggregatedCandidate, 
        min_seniority: Optional[SeniorityLevel]
    ) -> float:
        if min_seniority is None:
            return self._MAX_NORMALIZED_SCORE
        
        candidate_seniority_str = candidate.metadata.get("seniority_level")
        if not candidate_seniority_str:
            return self._MIN_NORMALIZED_SCORE
        
        try:
            candidate_seniority = SeniorityLevel(candidate_seniority_str)
        except ValueError:
            return self._MIN_NORMALIZED_SCORE
        
        min_ordinal = self._SENIORITY_ORDINALS.get(min_seniority, 0)
        candidate_ordinal = self._SENIORITY_ORDINALS.get(candidate_seniority, 0)
        
        if candidate_ordinal < min_ordinal:
            return self._MIN_NORMALIZED_SCORE
        
        excess_ordinal = candidate_ordinal - min_ordinal
        capped_excess = min(excess_ordinal, self._weights.max_seniority_delta)
        
        if self._weights.max_seniority_delta == 0:
            return self._MAX_NORMALIZED_SCORE if excess_ordinal == 0 else self._MIN_NORMALIZED_SCORE
        
        return capped_excess / self._weights.max_seniority_delta
    
    def _calculate_leadership_score(self, candidate: AggregatedCandidate) -> float:
        combined_text = " ".join(candidate.documents).lower()
        
        matches = sum(1 for keyword in self._LEADERSHIP_KEYWORDS if keyword in combined_text)
        
        if matches == 0:
            return self._MIN_NORMALIZED_SCORE
        
        if matches < self._weights.leadership_keyword_threshold:
            return self._MIN_NORMALIZED_SCORE
        
        return min(self._weights.max_leadership_contribution, self._MAX_NORMALIZED_SCORE)
    
    def _is_leadership_relevant(self, parsed_query: ParsedQuery) -> bool:
        if parsed_query.query_intent in self._LEADERSHIP_RELEVANT_INTENTS:
            return True
        
        query_lower = parsed_query.query_text.lower()
        return any(keyword in query_lower for keyword in self._LEADERSHIP_KEYWORDS)
    
    def _calculate_experience_score(
        self, 
        candidate: AggregatedCandidate, 
        min_years: Optional[int]
    ) -> float:
        if min_years is None:
            return self._MAX_NORMALIZED_SCORE
        
        candidate_years = candidate.metadata.get("years_experience")
        if candidate_years is None:
            return self._MIN_NORMALIZED_SCORE
        
        try:
            candidate_years = int(candidate_years)
        except (ValueError, TypeError):
            return self._MIN_NORMALIZED_SCORE
        
        if candidate_years < min_years:
            return self._MIN_NORMALIZED_SCORE
        
        excess_years = candidate_years - min_years
        max_excess_years = 10
        
        return min(excess_years / max_excess_years, self._MAX_NORMALIZED_SCORE)
