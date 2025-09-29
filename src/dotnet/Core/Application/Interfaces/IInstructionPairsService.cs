namespace Rag.Candidates.Core.Application.Interfaces;

public interface IInstructionPairsService
{
    Task<(string Text, Dictionary<string, object> Metadata)[]> GetInstructionPairsAsync(string? path = null, CancellationToken ct = default);
}