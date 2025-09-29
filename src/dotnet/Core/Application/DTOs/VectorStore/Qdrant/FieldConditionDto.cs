using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class FieldConditionDto
{
    [JsonPropertyName("key")] 
    public string Key { get; set; } = default!;
    
    [JsonPropertyName("match")] 
    public MatchDto? Match { get; set; }
    
    [JsonPropertyName("range")] 
    public RangeDto? Range { get; set; }
}