using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class MatchDto
{
    [JsonPropertyName("value")] 
    public object? Value { get; set; }
}