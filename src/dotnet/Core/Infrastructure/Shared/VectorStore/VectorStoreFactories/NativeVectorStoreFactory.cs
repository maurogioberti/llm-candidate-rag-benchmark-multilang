using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.VectorStores.Native;

namespace Rag.Candidates.Core.Infrastructure.Shared.VectorStorage.VectorStoreFactories;

public class NativeVectorStoreFactory : VectorStoreFactoryBase
{
    public NativeVectorStoreFactory(VectorStorageSettings vectorSettings) : base(vectorSettings)
    {
    }

    public override IVectorStore CreateVectorStore(IServiceProvider serviceProvider)
    {
        var logger = serviceProvider.GetService<ILogger<InMemoryVectorStore>>();
        return new InMemoryVectorStore(logger);
    }
}