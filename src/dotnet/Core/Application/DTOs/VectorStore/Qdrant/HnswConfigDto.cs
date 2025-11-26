using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class HnswConfigDto
{
    [JsonPropertyName("m")]
    public int M { get; set; } = 16;
    
    [JsonPropertyName("ef_construct")]
    public int EfConstruct { get; set; } = 128;
}
