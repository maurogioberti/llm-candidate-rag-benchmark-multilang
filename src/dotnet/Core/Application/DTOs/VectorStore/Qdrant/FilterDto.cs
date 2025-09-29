using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class FilterDto
{
    [JsonPropertyName("must")] 
    public List<ConditionDto> Must { get; set; } = new();
}