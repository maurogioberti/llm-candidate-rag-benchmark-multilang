using Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;
using Rag.Candidates.Core.Application.Interfaces;
using System.Net;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Infrastructure.VectorStores.Qdrant;

public sealed class QdrantVectorStore : IVectorStore
{
    private readonly HttpClient _http;
    private readonly ILogger<QdrantVectorStore>? _logger;
    private static readonly JsonSerializerOptions JsonOpts = new(JsonSerializerDefaults.Web)
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
    };

    private const int VectorSize = 1536;
    private const string DistanceMetric = "Cosine";
    private const string EmptyResponseMessage = "Empty response from Qdrant";

    private const string CollectionsPathTemplate = "/collections/{0}";
    private const string PointsPathTemplate = "/collections/{0}/points";
    private const string PointsSearchPathTemplate = "/collections/{0}/points/search";
    private const string DeletePointsPathTemplate = "/collections/{0}/points/delete";

    private const string CollectionExistsLog = "Collection {Name} already exists";
    private const string CreatedCollectionLog = "Created collection {Name} (size={Size}, distance={Distance})";
    private const string UpsertErrorLog = "Qdrant upsert response: {Status} {Content}";
    private const string UpsertedLog = "Upserted {Count} points into {Collection}";
    private const string SearchReturnedLog = "Search returned {Count} results. Top score={Top:F4}";
    private const string DeletedLog = "Deleted point {Id} from {Collection}";

    private const string OperatorGte = "$gte";
    private const string OperatorIn = "$in";
    private const string AndOperator = "$and";
    private const string DocumentKey = "document";

    public QdrantVectorStore(IHttpClientFactory httpFactory, ILogger<QdrantVectorStore>? logger = null)
    {
        _http = httpFactory.CreateClient(nameof(QdrantVectorStore));
        _logger = logger;
    }

    public async Task EnsureCollectionAsync(string name, CancellationToken ct = default)
    {
        var get = await _http.GetAsync(string.Format(CollectionsPathTemplate, Uri.EscapeDataString(name)), ct);
        if (get.StatusCode == HttpStatusCode.OK)
        {
            _logger?.LogInformation(CollectionExistsLog, name);
            return;
        }
        if (get.StatusCode != HttpStatusCode.NotFound)
        {
            get.EnsureSuccessStatusCode();
        }

        var req = new CreateCollectionRequest
        {
            Vectors = new VectorParamsDto { Size = VectorSize, Distance = DistanceMetric }
        };

        var put = await _http.PutAsJsonAsync(string.Format(CollectionsPathTemplate, Uri.EscapeDataString(name)), req, JsonOpts, ct);
        put.EnsureSuccessStatusCode();
        _logger?.LogInformation(CreatedCollectionLog, name, VectorSize, DistanceMetric);
    }

    public async Task UpsertAsync(
        string collection,
        IEnumerable<(string Id, float[] Vector, string Document, Dictionary<string, object> Metadata)> items,
        CancellationToken ct = default)
    {
        var points = items.Select(x => new PointWrite
        {
            Id = Guid.TryParse(x.Id, out var g) ? g.ToString() : ToDeterministicUuid(x.Id),
            Vector = x.Vector,
            Payload = BuildPayload(x.Document, x.Metadata)
        }).ToArray();

        var body = new UpsertRequest { Points = points };

        var resp = await _http.PutAsJsonAsync(
            string.Format(PointsPathTemplate, Uri.EscapeDataString(collection)),
            body, JsonOpts, ct);

        var content = await resp.Content.ReadAsStringAsync(ct);
        if (!resp.IsSuccessStatusCode)
        {
            _logger?.LogError(UpsertErrorLog,
                resp.StatusCode, content);
            resp.EnsureSuccessStatusCode();
        }

        _logger?.LogInformation(UpsertedLog,
            points.Length, collection);
    }

    public async Task<(string Document, Dictionary<string, object> Metadata, float Score)[]> SearchAsync(
        string collection,
        float[] queryVector,
        int limit = 10,
        Dictionary<string, object>? filter = null,
        CancellationToken ct = default)
    {
        var body = new SearchRequest
        {
            Vector = queryVector,
            Limit = limit,
            WithPayload = true,
            WithVector = false,
            Filter = filter != null ? BuildFilter(filter) : null
        };

        var jsonBody = JsonSerializer.Serialize(body, JsonOpts);
        _logger?.LogInformation("Qdrant Search Request: {JsonBody}", jsonBody);

        var resp = await _http.PostAsJsonAsync(
            string.Format(PointsSearchPathTemplate, Uri.EscapeDataString(collection)),
            body, JsonOpts, ct);

        if (!resp.IsSuccessStatusCode)
        {
            var errorContent = await resp.Content.ReadAsStringAsync(ct);
            _logger?.LogError("Qdrant Search Error: {StatusCode} - {ErrorContent}", resp.StatusCode, errorContent);
        }

        resp.EnsureSuccessStatusCode();

        var data = await resp.Content.ReadFromJsonAsync<QdrantResponse<List<SearchResult>>>(JsonOpts, ct)
                   ?? throw new InvalidOperationException(EmptyResponseMessage);

        var results = data.Result.Select(r =>
        {
            var doc = r.Payload.TryGetValue(DocumentKey, out var dv) ? dv?.ToString() ?? "" : "";
            var meta = r.Payload
                .Where(kv => kv.Key != DocumentKey)
                .ToDictionary(kv => kv.Key, kv => kv.Value!);

            return (doc, meta, r.Score);
        }).ToArray();

        _logger?.LogInformation(SearchReturnedLog,
            results.Length, results.Length > 0 ? results[0].Score : 0f);

        return results;
    }

    public async Task DeleteAsync(string collection, string id, CancellationToken ct = default)
    {
        var body = new DeleteRequest { Points = new[] { id } };

        var resp = await _http.PostAsJsonAsync(
            string.Format(DeletePointsPathTemplate, Uri.EscapeDataString(collection)),
            body, JsonOpts, ct);

        resp.EnsureSuccessStatusCode();
        _logger?.LogInformation(DeletedLog, id, collection);
    }

    public async Task<int> CountAsync(string collection, CancellationToken ct = default)
    {
        var resp = await _http.GetAsync(string.Format(CollectionsPathTemplate, Uri.EscapeDataString(collection)), ct);
        resp.EnsureSuccessStatusCode();

        var info = await resp.Content.ReadFromJsonAsync<QdrantResponse<CollectionInfo>>(JsonOpts, ct)
                   ?? throw new InvalidOperationException(EmptyResponseMessage);

        var count = (int)Math.Min(info.Result.PointsCount, int.MaxValue);
        return count;
    }

    private static string ToDeterministicUuid(string input)
    {
        using var md5 = System.Security.Cryptography.MD5.Create();
        var hash = md5.ComputeHash(System.Text.Encoding.UTF8.GetBytes(input));
        var g = new Guid(hash);
        return g.ToString();
    }

    private static Dictionary<string, object?> BuildPayload(string document, Dictionary<string, object> metadata)
    {
        var dict = new Dictionary<string, object?>(StringComparer.OrdinalIgnoreCase)
        {
            [DocumentKey] = document
        };
        foreach (var kv in metadata)
            dict[kv.Key] = kv.Value;
        return dict;
    }

    private static object BuildFilter(Dictionary<string, object> filter)
    {
        if (filter.Count == 1 && filter.TryGetValue(AndOperator, out var andValue) && andValue is List<object> andList)
        {
            var must = new List<object>();
            foreach (var condition in andList)
            {
                if (condition is Dictionary<string, object> conditionDict)
                {
                    must.Add(ConvertConditionToQdrant(conditionDict));
                }
            }
            return new { must };
        }
        
        if (filter.Count > 1)
        {
            var must = new List<object>();
            foreach (var kvp in filter)
            {
                must.Add(ConvertConditionToQdrant(new Dictionary<string, object> { { kvp.Key, kvp.Value } }));
            }
            return new { must };
        }
        
        return ConvertConditionToQdrant(filter);
    }

    private static object ConvertConditionToQdrant(Dictionary<string, object> condition)
    {
        if (condition.Count == 1)
        {
            var kvp = condition.First();
            var key = kvp.Key;
            var value = kvp.Value;

            if (value is Dictionary<string, object> ops)
            {
                if (ops.TryGetValue(OperatorGte, out var gte))
                {
                    return new
                    {
                        key = key,
                        range = new { gte = gte }
                    };
                }
                if (ops.TryGetValue(OperatorIn, out var inValues))
                {
                    return new
                    {
                        key = key,
                        match = new { any = inValues }
                    };
                }
            }
            else
            {
                return new
                {
                    key = key,
                    match = new { value = value }
                };
            }
        }

        return condition;
    }
}