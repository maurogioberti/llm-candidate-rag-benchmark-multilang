from dataclasses import dataclass


@dataclass(frozen=True)
class RankingWeights:
    technical_match_weight: float
    seniority_match_weight: float
    leadership_signals_weight: float
    experience_match_weight: float
    leadership_keyword_threshold: int
    max_seniority_delta: int
    max_leadership_contribution: float
    
    @staticmethod
    def default() -> "RankingWeights":
        return RankingWeights(
            technical_match_weight=0.40,
            seniority_match_weight=0.25,
            leadership_signals_weight=0.20,
            experience_match_weight=0.15,
            leadership_keyword_threshold=2,
            max_seniority_delta=2,
            max_leadership_contribution=0.5
        )
