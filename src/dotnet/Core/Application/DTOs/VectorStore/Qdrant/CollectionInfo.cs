using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class CollectionInfo
{
    [JsonPropertyName("points_count")] 
    public long PointsCount { get; set; }
}