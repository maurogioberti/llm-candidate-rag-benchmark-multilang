using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Application.Configuration;

public class ConfigurationService
{
    private readonly IDeserializer _deserializer;

    public ConfigurationService()
    {
        _deserializer = new DeserializerBuilder()
            .WithNamingConvention(UnderscoredNamingConvention.Instance)
            .Build();
    }

    public Settings LoadSettings()
    {
        const string ConfigDirectory = "config";
        const string CommonYamlFile = "common.yaml";
        const string LocalYamlFile = "common.local.yaml";

        var baseDirectory = PathHelper.GetBaseDirectory();
        var commonYamlPath = Path.Combine(baseDirectory, ConfigDirectory, CommonYamlFile);
        var localYamlPath = Path.Combine(baseDirectory, ConfigDirectory, LocalYamlFile);

        var settings = LoadFromFile(commonYamlPath);
        return settings;
    }

    private Settings LoadFromFile(string filePath)
    {
        var yamlContent = File.ReadAllText(filePath);
        return _deserializer.Deserialize<Settings>(yamlContent);
    }
}
