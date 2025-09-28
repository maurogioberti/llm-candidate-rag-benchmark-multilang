using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class OllamaSettings
{
    [YamlMember(Alias = "base_url")]
    public required string BaseUrl { get; set; }
}
