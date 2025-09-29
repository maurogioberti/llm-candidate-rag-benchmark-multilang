using YamlDotNet.Serialization;

namespace Rag.Candidates.Core.Domain.Configuration;

public class EmbeddingsServiceSettings
{
    public required string Host { get; set; }
    public int Port { get; set; }
    public required string Url { get; set; }

    [YamlMember(Alias = "instruction_file")]
    public required string InstructionFile { get; set; }
}
