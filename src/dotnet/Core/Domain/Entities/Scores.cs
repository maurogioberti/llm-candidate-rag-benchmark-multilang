using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Domain.Entities;

public class Scores
{
    public double? OverallScore { get; set; }
    public double? TechnicalScore { get; set; }
    public double? ExperienceScore { get; set; }
    public double? LanguageScore { get; set; }
    public double? CulturalFitScore { get; set; }
    public OverallFitLevel? OverallFitLevel { get; set; }
}