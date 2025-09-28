using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class Settings
{
    [YamlMember(Alias = "python_api")]
    public required PythonApiSettings PythonApi { get; set; }

    [YamlMember(Alias = "dotnet_api")]
    public required DotNetApiSettings DotnetApi { get; set; }

    [YamlMember(Alias = "embeddings_service")]
    public required EmbeddingsServiceSettings EmbeddingsService { get; set; }

    [YamlMember(Alias = "vector_storage")]
    public required VectorStorageSettings VectorStorage { get; set; }

    [YamlMember(Alias = "llm_provider")]
    public required LlmProviderSettings LlmProvider { get; set; }

    public required QdrantSettings Qdrant { get; set; }
    public required DataSettings Data { get; set; }
}
