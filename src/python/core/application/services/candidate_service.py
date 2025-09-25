from typing import List, Union
from pathlib import Path
from ...domain.entities.candidate import Candidate
from .candidate_factory import CandidateFactory


class CandidateService:
    
    def __init__(self):
        self.factory = CandidateFactory(validate_schema=True)
    
    def load_candidates_from_directory(self, input_dir: Union[str, Path]) -> List[Candidate]:
        print(f"[CANDIDATE_SERVICE] Loading candidates from: {input_dir}")
        candidates = []
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            print(f"[CANDIDATE_SERVICE] Directory does not exist: {input_dir}")
            return candidates
            
        json_files = list(input_dir.glob("*.json"))
        print(f"[CANDIDATE_SERVICE] Found {len(json_files)} JSON files")
        
        for json_file in json_files:
            try:
                print(f"[CANDIDATE_SERVICE] Loading file: {json_file.name}")
                candidate_id = json_file.stem  # Use filename without extension as candidate_id
                candidate = self.factory.from_json_file_to_candidate(json_file, candidate_id)
                candidates.append(candidate)
                print(f"[CANDIDATE_SERVICE] Loaded candidate: {candidate.candidate_id}")
                
            except Exception as e:
                print(f"[CANDIDATE_SERVICE] Error loading {json_file}: {e}")
                continue
                
        print(f"[CANDIDATE_SERVICE] Successfully loaded {len(candidates)} candidates")
        return candidates