using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.Shared.VectorStorage.VectorStoreFactories;

namespace Rag.Candidates.Core.Infrastructure.Shared.VectorStorage;

public class VectorStoreFactoryRegistry
{
    private readonly Dictionary<VectorStoreProviderType, Func<VectorStorageSettings, QdrantSettings, IVectorStoreFactory>> _factories;

    public VectorStoreFactoryRegistry()
    {
        _factories = new Dictionary<VectorStoreProviderType, Func<VectorStorageSettings, QdrantSettings, IVectorStoreFactory>>
        {
            [VectorStoreProviderType.Native] = (vector, qdrant) => new NativeVectorStoreFactory(vector),
            [VectorStoreProviderType.Qdrant] = (vector, qdrant) => new QdrantVectorStoreFactory(vector, qdrant)
        };
    }

    public IVectorStoreFactory GetFactory(VectorStoreProviderType provider, VectorStorageSettings vectorSettings, QdrantSettings qdrantSettings)
    {
        if (!_factories.TryGetValue(provider, out var factoryFunc))
        {
            throw new NotSupportedException($"Vector store provider '{provider}' is not supported. Available providers: {string.Join(", ", _factories.Keys)}");
        }

        return factoryFunc(vectorSettings, qdrantSettings);
    }

    public void RegisterFactory(VectorStoreProviderType provider, Func<VectorStorageSettings, QdrantSettings, IVectorStoreFactory> factoryFunc)
    {
        _factories[provider] = factoryFunc;
    }

    public IEnumerable<VectorStoreProviderType> GetAvailableProviders() => _factories.Keys;
}