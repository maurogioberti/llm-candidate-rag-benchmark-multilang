from typing import List, Union
from pathlib import Path
from ...domain.entities.candidate_record import CandidateRecord
from .candidate_factory import CandidateFactory


class CandidateService:
    
    def __init__(self):
        self.factory = CandidateFactory(validate_schema=True)
    
    def load_candidates_from_directory(self, input_dir: Union[str, Path]) -> List[CandidateRecord]:
        candidates = []
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            return candidates
            
        for json_file in input_dir.glob("*.json"):
            try:
                candidate = self.factory.from_json_file(json_file)
                candidates.append(candidate)
                
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
                
        return candidates