using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Infrastructure.VectorStores.Qdrant;

namespace Rag.Candidates.Core.Infrastructure.Shared.VectorStorage.VectorStoreFactories;

public class QdrantVectorStoreFactory : IVectorStoreFactory
{
    public IVectorStore CreateVectorStore(IServiceProvider serviceProvider)
    {
        var httpClientFactory = serviceProvider.GetRequiredService<IHttpClientFactory>();
        var logger = serviceProvider.GetService<ILogger<QdrantVectorStore>>();

        return new QdrantVectorStore(httpClientFactory, logger);
    }
}