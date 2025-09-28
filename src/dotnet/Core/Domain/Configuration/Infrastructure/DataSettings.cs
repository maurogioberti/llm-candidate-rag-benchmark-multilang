using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class DataSettings
{
    public required string Root { get; set; }
    public required string Input { get; set; }
    public required string Prompts { get; set; }

    [YamlMember(Alias = "embeddings_instructions")]
    public required string EmbInstructions { get; set; }

    public required string Finetuning { get; set; }
    public required string Schema { get; set; }
}
