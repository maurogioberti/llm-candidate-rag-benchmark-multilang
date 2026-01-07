from dataclasses import dataclass, field
from typing import Dict, List
from ..enums.seniority_level import SeniorityLevel


@dataclass(frozen=True)
class QueryParsingConfig:
    seniority_tokens: Dict[SeniorityLevel, List[str]] = field(default_factory=lambda: {
        SeniorityLevel.INTERN: ["intern", "internship", "trainee"],
        SeniorityLevel.JUNIOR: ["junior", "jr", "entry level", "entry-level"],
        SeniorityLevel.MID: ["mid", "mid-level", "intermediate"],
        SeniorityLevel.SENIOR: ["senior", "sr", "advanced"],
        SeniorityLevel.LEAD: ["lead", "tech lead", "team lead", "technical lead"],
        SeniorityLevel.PRINCIPAL: ["principal", "staff engineer"],
        SeniorityLevel.STAFF: ["staff", "architect"],
    })
    
    technology_synonyms: Dict[str, str] = field(default_factory=lambda: {
        "js": "JavaScript",
        "javascript": "JavaScript",
        "ts": "TypeScript",
        "typescript": "TypeScript",
        "py": "Python",
        "python": "Python",
        "k8s": "Kubernetes",
        "react": "React",
        "reactjs": "React",
        "vue": "Vue",
        "vuejs": "Vue",
        "angular": "Angular",
        "angularjs": "Angular",
        "node": "Node.js",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "dotnet": ".NET",
        "csharp": "C#",
        "c#": "C#",
        "java": "Java",
        "golang": "Go",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "mongo": "MongoDB",
        "mongodb": "MongoDB",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "Google Cloud",
    })
    
    intent_keywords: Dict[str, List[str]] = field(default_factory=lambda: {
        "find_best": ["best", "top", "most qualified", "ideal", "perfect", "strongest"],
        "list_all": ["list", "all", "show me", "find all", "get all"],
        "compare": ["compare", "comparison", "versus", "vs", "difference between"],
        "explain": ["explain", "why", "how", "what makes", "reasoning"],
    })


DEFAULT_QUERY_PARSING_CONFIG = QueryParsingConfig()
