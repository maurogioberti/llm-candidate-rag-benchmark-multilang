import re
from typing import Dict


class SkillNormalizer:
    _NORMALIZATION_RULES: Dict[str, str] = {
        r'.*\bJava\b.*': 'Java',
        r'.*\bSpring\b.*': 'Spring',
        r'.*\bASP\.?\s*NET\b.*': '.NET',
        r'.*\b\.?\s*NET\b.*': '.NET',
        r'.*\bC#\b.*': 'C#',
        r'.*\bCSharp\b.*': 'C#',
        r'.*\bNode\.?js\b.*': 'Node.js',
        r'.*\bNode\b.*': 'Node.js',
        r'.*\bReact\b.*': 'React',
        r'.*\bAngular.*': 'Angular',
        r'.*\bVue\b.*': 'Vue',
        r'.*\bJavaScript\b.*': 'JavaScript',
        r'.*\bJS\b.*': 'JavaScript',
        r'.*\bTypeScript\b.*': 'TypeScript',
        r'.*\bTS\b.*': 'TypeScript',
        r'.*\bPython\b.*': 'Python',
        r'.*\bSQL\b.*': 'SQL',
        r'.*MySQL.*': 'SQL',
        r'.*PostgreSQL.*': 'SQL',
        r'.*\bDocker\b.*': 'Docker',
        r'.*\bKubernetes\b.*': 'Kubernetes',
        r'.*\bK8s\b.*': 'Kubernetes',
        r'.*\bGit\b.*': 'Git',
        r'.*\bPHP\b.*': 'PHP',
        r'.*\bC\+\+\b.*': 'C++',
        r'.*\bKotlin\b.*': 'Kotlin',
    }
    
    @staticmethod
    def normalize(skill_name: str) -> str:
        if not skill_name:
            return skill_name
        
        skill_trimmed = skill_name.strip()
        
        for pattern, canonical in SkillNormalizer._NORMALIZATION_RULES.items():
            if re.match(pattern, skill_trimmed, re.IGNORECASE):
                return canonical
        
        return skill_trimmed
