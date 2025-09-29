using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class SearchResult
{
    [JsonPropertyName("id")] 
    public object? Id { get; set; }
    
    [JsonPropertyName("score")] 
    public float Score { get; set; }
    
    [JsonPropertyName("payload")] 
    public Dictionary<string, object?> Payload { get; set; } = new();
}