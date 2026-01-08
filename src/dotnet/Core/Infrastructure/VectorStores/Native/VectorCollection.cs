using System.Collections.Concurrent;

namespace Rag.Candidates.Core.Infrastructure.VectorStores.Native;

public sealed class VectorCollection
{
    private readonly ConcurrentDictionary<string, VectorItem> _items = new();

    private const string OperatorGte = "$gte";
    private const string OperatorIn = "$in";
    private const string OperatorAnd = "$and";

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
        var candidates = _items.Values.AsEnumerable();
        
        if (filter != null)
        {
            candidates = candidates.Where(item => MatchesFilter(item.Metadata, filter));
        }

        var results = new List<(string Document, Dictionary<string, object> Metadata, float Score)>(limit);
        var scoredItems = candidates
            .AsParallel()
            .Select(item => new
            {
                item.Document,
                item.Metadata,
                Score = CosineSimilarity(queryVector, item.Vector)
            })
            .OrderByDescending(x => x.Score)
            .Take(limit)
            .ToArray();

        return scoredItems.Select(x => (x.Document, x.Metadata, x.Score)).ToArray();
    }

    private static bool MatchesFilter(Dictionary<string, object> metadata, Dictionary<string, object> filter)
    {
        foreach (var (key, value) in filter)
        {
            if (key == OperatorAnd)
            {
                if (value is not object[] andConditions)
                    return false;

                foreach (var condition in andConditions)
                {
                    if (condition is not Dictionary<string, object> conditionDict)
                        return false;

                    if (!MatchesFilter(metadata, conditionDict))
                        return false;
                }
                continue;
            }

            if (!metadata.TryGetValue(key, out var metaValue))
                return false;

            if (value is Dictionary<string, object> operatorDict)
            {
                foreach (var (op, opValue) in operatorDict)
                {
                    if (op == OperatorGte)
                    {
                        if (int.TryParse(metaValue?.ToString(), out var metaInt) &&
                            int.TryParse(opValue?.ToString(), out var filterInt))
                        {
                            if (metaInt < filterInt)
                                return false;
                        }
                    }
                    else if (op == OperatorIn)
                    {
                        if (opValue is not object[] inValues)
                            return false;

                        var metaStr = metaValue?.ToString();
                        var found = false;

                        foreach (var inVal in inValues)
                        {
                            if (Equals(metaStr, inVal?.ToString()))
                            {
                                found = true;
                                break;
                            }
                        }

                        if (!found)
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

    private static readonly float ZeroSimilarity = 0f;
    
    private static float CosineSimilarity(float[] a, float[] b)
    {
        if (a.Length != b.Length) return ZeroSimilarity;

        float dotProduct = ZeroSimilarity;
        float normA = ZeroSimilarity;
        float normB = ZeroSimilarity;

        for (var i = 0; i < a.Length; i++)
        {
            dotProduct += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }

        if (normA == ZeroSimilarity || normB == ZeroSimilarity) return ZeroSimilarity;

        return dotProduct / (float)(Math.Sqrt(normA) * Math.Sqrt(normB));
    }

    private record VectorItem(string Id, float[] Vector, string Document, Dictionary<string, object> Metadata);
}