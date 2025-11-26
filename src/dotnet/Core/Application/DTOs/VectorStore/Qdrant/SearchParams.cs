using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class SearchParams
{
    [JsonPropertyName("hnsw_ef")]
    public int HnswEf { get; set; } = 128;
}
