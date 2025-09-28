using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class VectorStorageSettings
{
    public required string Type { get; set; }

    [YamlMember(Alias = "collection_name")]
    public required string CollectionName { get; set; }
}
