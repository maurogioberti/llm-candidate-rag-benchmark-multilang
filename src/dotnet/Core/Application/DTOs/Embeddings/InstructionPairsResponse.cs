namespace Rag.Candidates.Core.Application.DTOs.Embeddings;

internal sealed record InstructionPairsResponse(Pair[] Pairs);
internal sealed record Pair(string Text, Dictionary<string, object> Metadata);