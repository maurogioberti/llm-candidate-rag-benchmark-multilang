using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Shared.VectorStorage;

public class VectorStoreProvider
{
    private readonly VectorStorageSettings _vectorSettings;
    private readonly QdrantSettings _qdrantSettings;
    private readonly VectorStoreFactoryRegistry _registry;

    private const string SupportedProvidersSeparator = ", ";

    public VectorStoreProvider(VectorStorageSettings vectorSettings, QdrantSettings qdrantSettings, VectorStoreFactoryRegistry registry)
    {
        _vectorSettings = vectorSettings;
        _qdrantSettings = qdrantSettings;
        _registry = registry;
    }

    public IVectorStore CreateVectorStore(IServiceProvider serviceProvider)
    {
        var providerType = ParseProviderType(_vectorSettings.Type);
        var factory = _registry.GetFactory(providerType, _vectorSettings, _qdrantSettings);
        return factory.CreateVectorStore(serviceProvider);
    }

    private static VectorStoreProviderType ParseProviderType(string type)
    {
        if (Enum.TryParse<VectorStoreProviderType>(type, ignoreCase: true, out var result))
            return result;

        var supported = string.Join(SupportedProvidersSeparator, Array.ConvertAll(Enum.GetNames(typeof(VectorStoreProviderType)), n => n.ToLowerInvariant()));
        throw new NotSupportedException($"Vector store type '{type}' is not supported. Supported types: {supported}");
    }
}