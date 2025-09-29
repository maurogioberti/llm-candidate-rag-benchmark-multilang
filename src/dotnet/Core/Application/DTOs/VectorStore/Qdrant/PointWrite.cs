using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class PointWrite
{
    [JsonPropertyName("id")] 
    public object? Id { get; set; }
    
    [JsonPropertyName("vector")] 
    public float[] Vector { get; set; } = Array.Empty<float>();
    
    [JsonPropertyName("payload")] 
    public Dictionary<string, object?> Payload { get; set; } = new();
}