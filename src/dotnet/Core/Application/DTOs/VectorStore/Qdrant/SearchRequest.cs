using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class SearchRequest
{
    [JsonPropertyName("vector")] 
    public float[] Vector { get; set; } = Array.Empty<float>();
    
    [JsonPropertyName("limit")] 
    public int Limit { get; set; } = 10;
    
    [JsonPropertyName("with_payload")] 
    public bool WithPayload { get; set; } = true;
    
    [JsonPropertyName("with_vector")] 
    public bool WithVector { get; set; } = false;
    
    [JsonPropertyName("filter")] 
    public object? Filter { get; set; }
}