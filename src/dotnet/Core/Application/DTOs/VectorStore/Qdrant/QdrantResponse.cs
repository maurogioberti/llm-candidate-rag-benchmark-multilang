using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class QdrantResponse<T>
{
    [JsonPropertyName("result")] 
    public T Result { get; set; } = default!;
    
    [JsonPropertyName("status")] 
    public string Status { get; set; } = "";
    
    [JsonPropertyName("time")] 
    public double Time { get; set; }
}