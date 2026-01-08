"""Normalize skill names to canonical technology names for deterministic filtering."""
import re
from typing import Dict


class SkillNormalizer:
    """Normalizes skill names to canonical technology identifiers."""
    
    _NORMALIZATION_RULES: Dict[str, str] = {
        # Java variants
        r'^Java\s*\d*\.?\d*$': 'Java',
        r'^Java\s*\([^)]+\)$': 'Java',
        r'.*\bJava\b.*': 'Java',
        
        # JavaScript variants
        r'^JavaScript.*': 'JavaScript',
        r'^JS\s*\(.*\)$': 'JavaScript',
        
        # Python variants
        r'^Python\s*\d*\.?\d*$': 'Python',
        
        # C# variants
        r'^C#.*': 'C#',
        r'^CSharp.*': 'C#',
        
        # TypeScript variants
        r'^TypeScript.*': 'TypeScript',
        r'^TS\s*\(.*\)$': 'TypeScript',
        
        # React variants
        r'^React.*': 'React',
        
        # Angular variants
        r'^Angular.*': 'Angular',
        
        # Spring variants
        r'^Spring\s*\([^)]+\)$': 'Spring',
        r'^Spring\s+\w+$': 'Spring',
        
        # .NET variants
        r'^\.NET.*': '.NET',
        r'^ASP\.NET.*': 'ASP.NET',
        
        # Node variants
        r'^Node\.?js.*': 'Node.js',
        
        # SQL variants
        r'^SQL\s*\([^)]+\)$': 'SQL',
        r'.*SQL$': 'SQL',
        
        # Docker
        r'^Docker.*': 'Docker',
        
        # Kubernetes
        r'^Kubernetes.*': 'Kubernetes',
        r'^K8s$': 'Kubernetes',
        
        # Git
        r'^Git.*': 'Git',
    }
    
    @staticmethod
    def normalize(skill_name: str) -> str:
        """
        Normalize a skill name to its canonical form.
        
        Args:
            skill_name: Raw skill name from candidate data
            
        Returns:
            Canonical skill name for filtering, or original if no rule matches
        """
        if not skill_name:
            return skill_name
        
        skill_trimmed = skill_name.strip()
        
        for pattern, canonical in SkillNormalizer._NORMALIZATION_RULES.items():
            if re.match(pattern, skill_trimmed, re.IGNORECASE):
                return canonical
        
        return skill_trimmed
