import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...domain.entities.candidate_record import CandidateRecord
from ...infrastructure.shared.config_loader import get_config

SCHEMA_FILE = "candidate_record.schema.json"


class SchemaValidationService:
    def __init__(self, schema_path: Optional[str] = None):
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            cfg = get_config()
            schema_dir = cfg.raw["data"]["schema"]
            self.schema_path = cfg.get_data_root() / schema_dir / SCHEMA_FILE
        
        self._schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
        
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_json(self, data: Dict[str, Any]) -> bool:
        try:
            jsonschema.validate(data, self._schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"Schema validation error: {e}")
            return False
        except jsonschema.exceptions.SchemaError as e:
            print(f"Schema definition error: {e}")
            return False

    def validate_candidate_record(self, candidate_record: CandidateRecord) -> bool:
        try:
            data = self._to_dict(candidate_record)
            return self.validate_json(data)
        except Exception as e:
            print(f"Error converting CandidateRecord to dict: {e}")
            return False

    def _to_dict(self, obj: Any) -> Any:
        if obj is None:
            return None
        
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field_name, field_def in obj.__dataclass_fields__.items():
                value = getattr(obj, field_name)
                if value is not None:
                    result[field_name] = self._to_dict(value)
            return result
        
        elif isinstance(obj, list):
            return [self._to_dict(item) for item in obj]
        
        elif hasattr(obj, 'value'):
            return obj.value
        
        elif isinstance(obj, datetime):
            return obj.isoformat()
        
        else:
            return obj

    def get_validation_errors(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        try:
            jsonschema.validate(data, self._schema)
        except jsonschema.exceptions.ValidationError as e:
            errors.append(str(e))
            if e.absolute_path:
                path = " -> ".join(str(p) for p in e.absolute_path)
                errors.append(f"Error location: {path}")
        except jsonschema.exceptions.SchemaError as e:
            errors.append(f"Schema definition error: {e}")
        
        return errors