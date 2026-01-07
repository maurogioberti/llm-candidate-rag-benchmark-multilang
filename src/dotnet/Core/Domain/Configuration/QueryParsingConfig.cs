using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Domain.Configuration;

public sealed class QueryParsingConfig
{
    public Dictionary<SeniorityLevel, string[]> SeniorityTokens { get; init; } = new()
    {
        [SeniorityLevel.Intern] = new[] { "intern", "internship", "trainee" },
        [SeniorityLevel.Junior] = new[] { "junior", "jr", "entry level", "entry-level" },
        [SeniorityLevel.Mid] = new[] { "mid", "mid-level", "intermediate" },
        [SeniorityLevel.Senior] = new[] { "senior", "sr", "advanced" },
        [SeniorityLevel.Lead] = new[] { "lead", "tech lead", "team lead", "technical lead" },
        [SeniorityLevel.Principal] = new[] { "principal", "staff engineer" },
        [SeniorityLevel.Staff] = new[] { "staff", "architect" }
    };

    public Dictionary<string, string> TechnologySynonyms { get; init; } = new()
    {
        ["js"] = "JavaScript",
        ["javascript"] = "JavaScript",
        ["ts"] = "TypeScript",
        ["typescript"] = "TypeScript",
        ["py"] = "Python",
        ["python"] = "Python",
        ["k8s"] = "Kubernetes",
        ["react"] = "React",
        ["reactjs"] = "React",
        ["vue"] = "Vue",
        ["vuejs"] = "Vue",
        ["angular"] = "Angular",
        ["angularjs"] = "Angular",
        ["node"] = "Node.js",
        ["nodejs"] = "Node.js",
        ["node.js"] = "Node.js",
        ["dotnet"] = ".NET",
        ["csharp"] = "C#",
        ["c#"] = "C#",
        ["java"] = "Java",
        ["golang"] = "Go",
        ["postgres"] = "PostgreSQL",
        ["postgresql"] = "PostgreSQL",
        ["mongo"] = "MongoDB",
        ["mongodb"] = "MongoDB",
        ["docker"] = "Docker",
        ["kubernetes"] = "Kubernetes",
        ["aws"] = "AWS",
        ["azure"] = "Azure",
        ["gcp"] = "Google Cloud"
    };

    public Dictionary<string, string[]> IntentKeywords { get; init; } = new()
    {
        ["find_best"] = new[] { "best", "top", "most qualified", "ideal", "perfect", "strongest" },
        ["list_all"] = new[] { "list", "all", "show me", "find all", "get all" },
        ["compare"] = new[] { "compare", "comparison", "versus", "vs", "difference between" },
        ["explain"] = new[] { "explain", "why", "how", "what makes", "reasoning" }
    };

    public static QueryParsingConfig Default { get; } = new();
}
