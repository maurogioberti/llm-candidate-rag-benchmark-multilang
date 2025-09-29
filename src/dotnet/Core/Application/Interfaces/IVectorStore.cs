namespace Rag.Candidates.Core.Application.Interfaces;

public interface IVectorStore
{
    Task EnsureCollectionAsync(string name, CancellationToken ct = default);
    Task UpsertAsync(string name, IEnumerable<(string Id, float[] Vector, string Document, Dictionary<string, object> Metadata)> items, CancellationToken ct = default);
    Task<(string Document, Dictionary<string, object> Metadata, float Score)[]> SearchAsync(
        string collection,
        float[] queryVector,
        int limit = 10,
        Dictionary<string, object>? filter = null,
        CancellationToken ct = default);

    Task DeleteAsync(string collection, string id, CancellationToken ct = default);
    Task<int> CountAsync(string collection, CancellationToken ct = default);
}