using Rag.Candidates.Core.Application.Interfaces;
using System.Collections.Concurrent;

namespace Rag.Candidates.Core.Infrastructure.VectorStores.Native;

public sealed class InMemoryVectorStore : IVectorStore
{
    private readonly ConcurrentDictionary<string, VectorCollection> _collections = new();
    private readonly ILogger<InMemoryVectorStore>? _logger;

    private const string CollectionNotFoundMsg = "Collection '{0}' not found";
    private const string SearchLogTemplate = "Searching in collection {Collection} with {ItemCount} items, limit={Limit}, filter={Filter}";
    private const string SearchResultLogTemplate = "Search returned {ResultCount} results. Top scores: {TopScores}";
    private const string FilterNone = "none";
    private const string FilterSeparator = ", ";
    private const string TopScoreFormat = "F4";
    private const int TopScoresToShow = 3;

    public InMemoryVectorStore(ILogger<InMemoryVectorStore>? logger = null) => _logger = logger;

    public Task EnsureCollectionAsync(string name, CancellationToken ct = default)
    {
        _collections.TryAdd(name, new VectorCollection(name));
        return Task.CompletedTask;
    }

    public Task UpsertAsync(string collection, IEnumerable<(string Id, float[] Vector, string Document, Dictionary<string, object> Metadata)> items, CancellationToken ct = default)
    {
        if (!_collections.TryGetValue(collection, out var coll))
            throw new InvalidOperationException(string.Format(CollectionNotFoundMsg, collection));

        foreach (var (id, vector, document, metadata) in items)
        {
            coll.Upsert(id, vector, document, metadata);
        }

        return Task.CompletedTask;
    }

    public Task<(string Document, Dictionary<string, object> Metadata, float Score)[]> SearchAsync(
        string collection,
        float[] queryVector,
        int limit = 10,
        Dictionary<string, object>? filter = null,
        CancellationToken ct = default)
    {
        if (!_collections.TryGetValue(collection, out var coll))
            return Task.FromResult(Array.Empty<(string, Dictionary<string, object>, float)>());

        _logger?.LogInformation(SearchLogTemplate,
            collection, coll.Count, limit, filter != null ? string.Join(FilterSeparator, filter.Select(kv => $"{kv.Key}={kv.Value}")) : FilterNone);

        var results = coll.Search(queryVector, limit, filter);

        _logger?.LogInformation(SearchResultLogTemplate,
            results.Length,
            string.Join(FilterSeparator, results.Take(TopScoresToShow).Select(r => r.Score.ToString(TopScoreFormat))));

        return Task.FromResult(results);
    }

    public Task DeleteAsync(string collection, string id, CancellationToken ct = default)
    {
        if (_collections.TryGetValue(collection, out var coll))
        {
            coll.Delete(id);
        }
        return Task.CompletedTask;
    }

    public Task<int> CountAsync(string collection, CancellationToken ct = default)
    {
        if (!_collections.TryGetValue(collection, out var coll))
            return Task.FromResult(0);

        return Task.FromResult(coll.Count);
    }
}