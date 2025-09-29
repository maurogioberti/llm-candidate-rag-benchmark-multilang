using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class ConditionDto
{
    [JsonPropertyName("field")] 
    public FieldConditionDto? Field { get; set; }
}