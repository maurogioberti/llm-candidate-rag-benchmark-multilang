using Rag.Candidates.Core.Application.Interfaces;

namespace Rag.Candidates.Core.Infrastructure.Shared;

public sealed class InstructionPairsService : IInstructionPairsService
{
    private readonly IEmbeddingsClient _embeddingsClient;

    public InstructionPairsService(IEmbeddingsClient embeddingsClient)
    {
        _embeddingsClient = embeddingsClient;
    }

    public async Task<(string Text, Dictionary<string, object> Metadata)[]> GetInstructionPairsAsync(string? path = null, CancellationToken ct = default)
    {
        return await _embeddingsClient.GetInstructionPairsAsync(path, ct);
    }
}