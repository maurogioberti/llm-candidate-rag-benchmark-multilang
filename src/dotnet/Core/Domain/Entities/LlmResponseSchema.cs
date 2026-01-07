namespace Semantic.Kernel.Api.Core.Domain.Entities;

public sealed record SelectedCandidate
{
    public required string Fullname { get; init; }
    public required string CandidateId { get; init; }
    public required int Rank { get; init; }
}

public sealed record LlmResponseSchema
{
    public SelectedCandidate? SelectedCandidate { get; init; }
    public required string Justification { get; init; }
}
