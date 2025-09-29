using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class DeleteRequest
{
    [JsonPropertyName("points")] 
    public string[] Points { get; set; } = Array.Empty<string>();
}