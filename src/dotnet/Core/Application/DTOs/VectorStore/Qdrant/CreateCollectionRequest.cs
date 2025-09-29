using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class CreateCollectionRequest
{
    [JsonPropertyName("vectors")] 
    public VectorParamsDto Vectors { get; set; } = default!;
}