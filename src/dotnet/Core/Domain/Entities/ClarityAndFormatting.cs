namespace Rag.Candidates.Core.Domain.Entities;

public class ClarityAndFormatting
{
    public string? FormattingQuality { get; set; }
    public string? ClarityScore { get; set; }
    public string[]? FormattingIssues { get; set; }
    public string[]? ClarityIssues { get; set; }
    public string[]? Suggestions { get; set; }
}