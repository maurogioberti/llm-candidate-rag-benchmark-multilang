using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class UpsertRequest
{
    [JsonPropertyName("points")] 
    public PointWrite[] Points { get; set; } = Array.Empty<PointWrite>();
}