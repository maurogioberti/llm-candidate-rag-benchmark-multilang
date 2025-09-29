namespace Rag.Candidates.Core.Domain.Entities;

public class KeywordCoverage
{
    public string[]? RequiredKeywords { get; set; }
    public string[]? FoundKeywords { get; set; }
    public string[]? MissingKeywords { get; set; }
    public double? CoveragePercentage { get; set; }
    public string[]? AlternativeKeywords { get; set; }
}