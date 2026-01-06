from enum import Enum


class SkillLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    VERY_HIGH = "Very High"
    
    @classmethod
    def from_string(cls, value: str) -> 'SkillLevel':
        if not value:
            return None
        
        normalized = value.strip()
        
        mappings = {
            "Low": cls.LOW,
            "Medium": cls.MEDIUM,
            "High": cls.HIGH,
            "Very High": cls.VERY_HIGH,
            "VeryHigh": cls.VERY_HIGH,
        }
        
        return mappings.get(normalized, None)
    
    @classmethod
    def is_strong(cls, level: 'SkillLevel') -> bool:
        return level in [cls.HIGH, cls.VERY_HIGH]
