namespace Semantic.Kernel.Api.Core.Domain.Configuration;

public sealed record RankingWeights
{
    public required double TechnicalMatchWeight { get; init; }
    public required double SeniorityMatchWeight { get; init; }
    public required double LeadershipSignalsWeight { get; init; }
    public required double ExperienceMatchWeight { get; init; }
    public required int LeadershipKeywordThreshold { get; init; }
    public required int MaxSeniorityDelta { get; init; }
    public required double MaxLeadershipContribution { get; init; }
    
    public static RankingWeights Default() => new()
    {
        TechnicalMatchWeight = 0.40,
        SeniorityMatchWeight = 0.25,
        LeadershipSignalsWeight = 0.20,
        ExperienceMatchWeight = 0.15,
        LeadershipKeywordThreshold = 2,
        MaxSeniorityDelta = 2,
        MaxLeadershipContribution = 0.5
    };
}
