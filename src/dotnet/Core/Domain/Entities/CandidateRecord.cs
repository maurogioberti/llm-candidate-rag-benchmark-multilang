using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Domain.Entities;

public class CandidateRecord
{
    public required string Summary { get; set; }
    public string SchemaVersion { get; set; } = "1.0";
    public DateTime? GeneratedAt { get; set; }
    public string? Source { get; set; }
    public GeneralInfo? GeneralInfo { get; set; }
    public Skill[]? SkillMatrix { get; set; }
    public KeywordCoverage? KeywordCoverage { get; set; }
    public Language[]? Languages { get; set; }
    public Scores? Scores { get; set; }
    public Relevance? Relevance { get; set; }
    public ClarityAndFormatting? ClarityAndFormatting { get; set; }
    public string[]? Strengths { get; set; }
    public string[]? AreasToImprove { get; set; }
    public string[]? Tips { get; set; }
    public string? CleanedResumeText { get; set; }
}