using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class OpenAiSettings
{
    [YamlMember(Alias = "api_key")]
    public required string ApiKey { get; set; }

    [YamlMember(Alias = "base_url")]
    public required string BaseUrl { get; set; }
}
