using System.Collections.Concurrent;

namespace Rag.Candidates.Core.Infrastructure.VectorStores.Native;

public sealed class VectorCollection
{
    private readonly ConcurrentDictionary<string, VectorItem> _items = new();

    private const string OperatorGte = "$gte";

    public string Name { get; }
    public int Count => _items.Count;

    public VectorCollection(string name)
    {
        Name = name;
    }

    public void Upsert(string id, float[] vector, string document, Dictionary<string, object> metadata)
    {
        _items[id] = new VectorItem(id, vector, document, metadata);
    }

    public void Delete(string id)
    {
        _items.TryRemove(id, out _);
    }

    public (string Document, Dictionary<string, object> Metadata, float Score)[] Search(
        float[] queryVector,
        int limit,
        Dictionary<string, object>? filter = null)
    {
        var candidates = _items.Values.AsParallel();
        var totalCandidates = candidates.Count();

        if (filter != null)
        {
            candidates = candidates.Where(item => MatchesFilter(item.Metadata, filter));
        }

        var results = candidates
            .Select(item => new
            {
                item.Document,
                item.Metadata,
                Score = L2Distance(queryVector, item.Vector)
            })
            .OrderBy(x => x.Score)
            .Take(limit)
            .Select(x => (x.Document, x.Metadata, x.Score))
            .ToArray();

        return results;
    }

    private static bool MatchesFilter(Dictionary<string, object> metadata, Dictionary<string, object> filter)
    {
        foreach (var (key, value) in filter)
        {
            if (!metadata.TryGetValue(key, out var metaValue))
                return false;

            if (value is Dictionary<string, object> operatorDict)
            {
                foreach (var (op, opValue) in operatorDict)
                {
                    if (op == OperatorGte &&
                        int.TryParse(metaValue?.ToString(), out var metaInt) &&
                        int.TryParse(opValue?.ToString(), out var filterInt))
                    {
                        if (metaInt < filterInt)
                            return false;
                    }
                }
            }
            else
            {
                if (!Equals(metaValue?.ToString(), value?.ToString()))
                    return false;
            }
        }
        return true;
    }

    private static float L2Distance(float[] a, float[] b)
    {
        if (a.Length != b.Length) return float.MaxValue;

        float sum = 0f;
        for (int i = 0; i < a.Length; i++)
        {
            var diff = a[i] - b[i];
            sum += diff * diff;
        }

        return (float)Math.Sqrt(sum);
    }

    private record VectorItem(string Id, float[] Vector, string Document, Dictionary<string, object> Metadata);
}