from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Skill:
    SkillName: str
    SkillLevel: Optional[str] = None
    Years: Optional[float] = None
    Evidence: Optional[str] = None