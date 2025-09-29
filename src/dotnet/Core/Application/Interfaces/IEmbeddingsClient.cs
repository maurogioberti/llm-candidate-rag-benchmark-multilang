namespace Rag.Candidates.Core.Application.Interfaces;

public interface IEmbeddingsClient
{
    Task<float[][]> EmbedAsync(IEnumerable<string> texts, CancellationToken ct = default);
    Task<(string text, Dictionary<string, object> metadata)[]> GetInstructionPairsAsync(string? path = null, CancellationToken ct = default);
}
