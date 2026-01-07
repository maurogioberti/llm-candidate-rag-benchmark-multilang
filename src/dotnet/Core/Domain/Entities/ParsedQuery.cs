using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Domain.Entities;

public sealed class ParsedQuery
{
    public required string QueryText { get; init; }
    public required QueryIntent QueryIntent { get; init; }
    public required string[] RequiredTechnologies { get; init; }
    public SeniorityLevel? MinSeniorityLevel { get; init; }
    public int? MinYearsExperience { get; init; }
}
