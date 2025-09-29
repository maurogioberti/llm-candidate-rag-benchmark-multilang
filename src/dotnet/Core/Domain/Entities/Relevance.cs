namespace Rag.Candidates.Core.Domain.Entities;

public class Relevance
{
    public string? JobTitleMatch { get; set; }
    public string? IndustryMatch { get; set; }
    public string? TechnologyMatch { get; set; }
    public string? ExperienceMatch { get; set; }
    public string? LocationMatch { get; set; }
    public string? RemoteWorkMatch { get; set; }
    public double? OverallRelevanceScore { get; set; }
}