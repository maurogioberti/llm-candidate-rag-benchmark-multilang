namespace Rag.Candidates.Core.Application.DTOs;

public record ValidationResult
{
    public bool IsValid { get; init; }
    public IReadOnlyList<string> Errors { get; init; } = [];
}