"""
Validation script to test technology normalization rules.
Tests that dataset skills normalize correctly and identically in Python.
"""
import sys
sys.path.insert(0, 'src/python')

from core.application.services.skill_normalizer import SkillNormalizer

# Test cases from actual dataset
test_cases = [
    # Java variants
    ("Java 8", "Java"),
    ("Java (Spring/JSP)", "Java"),
    ("Data Structures & Algorithms (Java)", "Java"),
    
    # Spring variants
    ("Spring Boot", "Spring"),
    ("Spring MVC", "Spring"),
    ("Spring Data", "Spring"),
    ("Spring Security", "Spring"),
    
    # .NET variants
    (".NET (6–8) / C#", ".NET"),
    ("WPF / .NET Framework / WCF", ".NET"),
    ("ASP.NET Core", ".NET"),
    
    # C# variants
    ("C#", "C#"),
    
    # JavaScript variants
    ("JavaScript", "JavaScript"),
    ("JavaScript (ES6+)", "JavaScript"),
    
    # TypeScript
    ("TypeScript", "TypeScript"),
    
    # React
    ("React", "React"),
    ("Frontend Basics (React/HTML/CSS)", "React"),
    
    # Angular
    ("AngularJS (migration)", "Angular"),
    
    # Vue
    ("Vue.js", "Vue"),
    
    # Node
    ("Node.js", "Node.js"),
    
    # Python
    ("Python (for QA/Automation)", "Python"),
    
    # SQL variants
    ("SQL (Queries)", "SQL"),
    ("SQL (general)", "SQL"),
    ("SQL/MySQL/PostgreSQL", "SQL"),
    ("SQL Server", "SQL"),
    ("MySQL", "SQL"),
    ("PostgreSQL", "SQL"),
    
    # Docker
    ("Docker", "Docker"),
    
    # Git
    ("Git / Bitbucket", "Git"),
    ("Git/GitHub", "Git"),
    
    # Other
    ("PHP", "PHP"),
    ("C++", "C++"),
    ("Kotlin", "Kotlin"),
]

print("=" * 70)
print("PYTHON NORMALIZATION TEST")
print("=" * 70)

all_passed = True
for input_skill, expected in test_cases:
    result = SkillNormalizer.normalize(input_skill)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "PASS" if passed else "FAIL"
    print(f"{status} | '{input_skill}' -> '{result}' (expected: '{expected}')")

print("=" * 70)
if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
    sys.exit(1)

print("\n" + "=" * 70)
print("CANONICAL TECHNOLOGIES (based on dataset):")
print("=" * 70)
canonical = sorted(set(expected for _, expected in test_cases))
for tech in canonical:
    print(f"  - {tech}")
