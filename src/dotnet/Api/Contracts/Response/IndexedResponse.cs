namespace Rag.Candidates.Api.Api.Contracts.Response;

internal sealed record IndexedResponse(IndexedData Indexed);
internal sealed record IndexedData(string Candidates, string Chunks);