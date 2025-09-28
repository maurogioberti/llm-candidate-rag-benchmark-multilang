using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class LlmProviderSettings
{
    public required string Provider { get; set; }
    public required string Model { get; set; }

    [YamlMember(Alias = "openai")]
    public required OpenAiSettings OpenAi { get; set; }

    [YamlMember(Alias = "ollama")]
    public required OllamaSettings Ollama { get; set; }
}
