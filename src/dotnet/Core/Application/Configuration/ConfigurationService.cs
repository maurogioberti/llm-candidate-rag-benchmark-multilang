using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace Rag.Candidates.Core.Application.Configuration;

public class ConfigurationService
{
    private const string ConfigDirectory = "config";
    private const string CommonYamlFile = "common.yaml";
    private const string LocalYamlFile = "common.local.yaml";

    private readonly IDeserializer _deserializer;

    public ConfigurationService()
    {
        _deserializer = new DeserializerBuilder()
            .WithNamingConvention(UnderscoredNamingConvention.Instance)
            .Build();
    }

    public Domain.Configuration.Settings LoadSettings()
    {

        var baseDirectory = PathHelper.GetBaseDirectory();
        var commonYamlPath = Path.Combine(baseDirectory, ConfigDirectory, CommonYamlFile);
        var localYamlPath = Path.Combine(baseDirectory, ConfigDirectory, LocalYamlFile);

        var settings = LoadFromFile(commonYamlPath);
        return settings;
    }

    private Domain.Configuration.Settings LoadFromFile(string filePath)
    {
        var yamlContent = File.ReadAllText(filePath);
        return _deserializer.Deserialize<Domain.Configuration.Settings>(yamlContent);
    }
}
