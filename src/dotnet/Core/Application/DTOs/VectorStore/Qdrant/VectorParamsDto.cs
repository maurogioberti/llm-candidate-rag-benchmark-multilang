using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Application.DTOs.VectorStore.Qdrant;

internal sealed class VectorParamsDto
{
    [JsonPropertyName("size")] 
    public int Size { get; set; }
    
    [JsonPropertyName("distance")] 
    public string Distance { get; set; } = "Cosine";
    
    [JsonPropertyName("hnsw_config")]
    public HnswConfigDto? HnswConfig { get; set; }
}