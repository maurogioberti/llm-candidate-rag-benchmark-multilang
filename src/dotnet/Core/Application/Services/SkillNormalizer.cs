using System.Text.RegularExpressions;

namespace Rag.Candidates.Core.Application.Services;

public static class SkillNormalizer
{
    private static readonly Dictionary<string, string> NormalizationRules = new()
    {
        [@".*\bJava\b.*"] = "Java",
        [@".*\bSpring\b.*"] = "Spring",
        [@".*\bASP\.?\s*NET\b.*"] = ".NET",
        [@".*\b\.?\s*NET\b.*"] = ".NET",
        [@".*\bC#\b.*"] = "C#",
        [@".*\bCSharp\b.*"] = "C#",
        [@".*\bNode\.?js\b.*"] = "Node.js",
        [@".*\bNode\b.*"] = "Node.js",
        [@".*\bReact\b.*"] = "React",
        [@".*\bAngular.*"] = "Angular",
        [@".*\bVue\b.*"] = "Vue",
        [@".*\bJavaScript\b.*"] = "JavaScript",
        [@".*\bJS\b.*"] = "JavaScript",
        [@".*\bTypeScript\b.*"] = "TypeScript",
        [@".*\bTS\b.*"] = "TypeScript",
        [@".*\bPython\b.*"] = "Python",
        [@".*\bSQL\b.*"] = "SQL",
        [@".*MySQL.*"] = "SQL",
        [@".*PostgreSQL.*"] = "SQL",
        [@".*\bDocker\b.*"] = "Docker",
        [@".*\bKubernetes\b.*"] = "Kubernetes",
        [@".*\bK8s\b.*"] = "Kubernetes",
        [@".*\bGit\b.*"] = "Git",
        [@".*\bPHP\b.*"] = "PHP",
        [@".*\bC\+\+\b.*"] = "C++",
        [@".*\bKotlin\b.*"] = "Kotlin",
    };

    public static string Normalize(string skillName)
    {
        if (string.IsNullOrWhiteSpace(skillName))
            return skillName;

        var skillTrimmed = skillName.Trim();

        foreach (var (pattern, canonical) in NormalizationRules)
        {
            if (Regex.IsMatch(skillTrimmed, pattern, RegexOptions.IgnoreCase))
            {
                return canonical;
            }
        }

        return skillTrimmed;
    }
}
