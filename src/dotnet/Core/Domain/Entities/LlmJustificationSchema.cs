namespace Rag.Candidates.Core.Domain.Entities;

public sealed record LlmJustificationSchema
{
    public required string Justification { get; init; }
}