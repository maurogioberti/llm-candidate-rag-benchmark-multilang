using Rag.Candidates.Core.Application.Services;

Console.WriteLine("=".PadRight(70, '='));
Console.WriteLine(".NET NORMALIZATION TEST");
Console.WriteLine("=".PadRight(70, '='));

var testCases = new (string Input, string Expected)[]
{
    // Java variants
    ("Java 8", "Java"),
    ("Java (Spring/JSP)", "Java"),
    ("Data Structures & Algorithms (Java)", "Java"),
    
    // Spring variants
    ("Spring Boot", "Spring"),
    ("Spring MVC", "Spring"),
    ("Spring Data", "Spring"),
    ("Spring Security", "Spring"),
    
    // .NET variants
    (".NET (6–8) / C#", ".NET"),
    ("WPF / .NET Framework / WCF", ".NET"),
    ("ASP.NET Core", ".NET"),
    
    // C# variants
    ("C#", "C#"),
    
    // JavaScript variants
    ("JavaScript", "JavaScript"),
    ("JavaScript (ES6+)", "JavaScript"),
    
    // TypeScript
    ("TypeScript", "TypeScript"),
    
    // React
    ("React", "React"),
    ("Frontend Basics (React/HTML/CSS)", "React"),
    
    // Angular
    ("AngularJS (migration)", "Angular"),
    
    // Vue
    ("Vue.js", "Vue"),
    
    // Node
    ("Node.js", "Node.js"),
    
    // Python
    ("Python (for QA/Automation)", "Python"),
    
    // SQL variants
    ("SQL (Queries)", "SQL"),
    ("SQL (general)", "SQL"),
    ("SQL/MySQL/PostgreSQL", "SQL"),
    ("SQL Server", "SQL"),
    ("MySQL", "SQL"),
    ("PostgreSQL", "SQL"),
    
    // Docker
    ("Docker", "Docker"),
    
    // Git
    ("Git / Bitbucket", "Git"),
    ("Git/GitHub", "Git"),
    
    // Other
    ("PHP", "PHP"),
    ("C++", "C++"),
    ("Kotlin", "Kotlin"),
};

var allPassed = true;
foreach (var (input, expected) in testCases)
{
    var result = SkillNormalizer.Normalize(input);
    var passed = result == expected;
    allPassed = allPassed && passed;
    
    var status = passed ? "PASS" : "FAIL";
    Console.WriteLine($"{status} | '{input}' -> '{result}' (expected: '{expected}')");
}

Console.WriteLine("=".PadRight(70, '='));
if (allPassed)
{
    Console.WriteLine("ALL TESTS PASSED");
}
else
{
    Console.WriteLine("SOME TESTS FAILED");
    return 1;
}

Console.WriteLine();
Console.WriteLine("=".PadRight(70, '='));
Console.WriteLine("CANONICAL TECHNOLOGIES (based on dataset):");
Console.WriteLine("=".PadRight(70, '='));

var canonical = testCases.Select(t => t.Expected).Distinct().OrderBy(x => x);
foreach (var tech in canonical)
{
    Console.WriteLine($"  - {tech}");
}

return 0;
