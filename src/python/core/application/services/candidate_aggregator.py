from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class AggregatedCandidate:
    candidate_id: str
    documents: List[str]
    metadata: Dict[str, Any]
    max_score: float
    all_scores: List[float]


class CandidateAggregator:
    def __init__(self, candidate_id_field: str):
        self._candidate_id_field = candidate_id_field
    
    def aggregate(self, search_results: List[tuple]) -> List[AggregatedCandidate]:
        candidate_map = {}
        
        for document, metadata, score in search_results:
            candidate_id = metadata.get(self._candidate_id_field, "unknown")
            
            if candidate_id not in candidate_map:
                candidate_map[candidate_id] = {
                    "candidate_id": candidate_id,
                    "documents": [],
                    "metadata": metadata.copy(),
                    "scores": []
                }
            
            candidate_map[candidate_id]["documents"].append(document)
            candidate_map[candidate_id]["scores"].append(score)
        
        aggregated = []
        for candidate_data in candidate_map.values():
            aggregated.append(AggregatedCandidate(
                candidate_id=candidate_data["candidate_id"],
                documents=candidate_data["documents"],
                metadata=candidate_data["metadata"],
                max_score=max(candidate_data["scores"]) if candidate_data["scores"] else 0.0,
                all_scores=candidate_data["scores"]
            ))
        
        return aggregated
