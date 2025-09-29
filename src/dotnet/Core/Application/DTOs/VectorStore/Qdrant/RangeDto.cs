using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class RangeDto
{
    [JsonPropertyName("gte")] 
    public double? Gte { get; set; }
    
    [JsonPropertyName("lte")] 
    public double? Lte { get; set; }
}