using System.Text.RegularExpressions;

namespace Rag.Candidates.Core.Application.Services;

/// <summary>
/// Normalizes skill names to canonical technology names for deterministic filtering.
/// </summary>
public static class SkillNormalizer
{
    private static readonly Dictionary<string, string> NormalizationRules = new()
    {
        // Java variants
        [@"^Java\s*\d*\.?\d*$"] = "Java",
        [@"^Java\s*\([^)]+\)$"] = "Java",
        [@".*\bJava\b.*"] = "Java",
        
        // JavaScript variants
        [@"^JavaScript.*"] = "JavaScript",
        [@"^JS\s*\(.*\)$"] = "JavaScript",
        
        // Python variants
        [@"^Python\s*\d*\.?\d*$"] = "Python",
        
        // C# variants
        [@"^C#.*"] = "C#",
        [@"^CSharp.*"] = "C#",
        
        // TypeScript variants
        [@"^TypeScript.*"] = "TypeScript",
        [@"^TS\s*\(.*\)$"] = "TypeScript",
        
        // React variants
        [@"^React.*"] = "React",
        
        // Angular variants
        [@"^Angular.*"] = "Angular",
        
        // Spring variants
        [@"^Spring\s*\([^)]+\)$"] = "Spring",
        [@"^Spring\s+\w+$"] = "Spring",
        
        // .NET variants
        [@"^\.NET.*"] = ".NET",
        [@"^ASP\.NET.*"] = "ASP.NET",
        
        // Node variants
        [@"^Node\.?js.*"] = "Node.js",
        
        // SQL variants
        [@"^SQL\s*\([^)]+\)$"] = "SQL",
        [@".*SQL$"] = "SQL",
        
        // Docker
        [@"^Docker.*"] = "Docker",
        
        // Kubernetes
        [@"^Kubernetes.*"] = "Kubernetes",
        [@"^K8s$"] = "Kubernetes",
        
        // Git
        [@"^Git.*"] = "Git",
    };

    /// <summary>
    /// Normalize a skill name to its canonical form.
    /// </summary>
    /// <param name="skillName">Raw skill name from candidate data</param>
    /// <returns>Canonical skill name for filtering, or original if no rule matches</returns>
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
