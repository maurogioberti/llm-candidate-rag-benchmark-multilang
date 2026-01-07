namespace Semantic.Kernel.Api.Core.Domain.Entities;

public sealed record RankedCandidate
{
    public required string CandidateId { get; init; }
    public required List<string> Documents { get; init; }
    public required Dictionary<string, object> Metadata { get; init; }
    public required double MaxScore { get; init; }
    public required List<double> AllScores { get; init; }
    public required double TechnicalScore { get; init; }
    public required double SeniorityScore { get; init; }
    public required double LeadershipScore { get; init; }
    public required double ExperienceScore { get; init; }
    public required double TotalScore { get; init; }
}
