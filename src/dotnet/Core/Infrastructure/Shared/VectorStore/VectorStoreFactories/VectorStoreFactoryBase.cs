using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Shared.VectorStorage.VectorStoreFactories;

public abstract class VectorStoreFactoryBase : IVectorStoreFactory
{
    protected readonly VectorStorageSettings _vectorSettings;

    protected VectorStoreFactoryBase(VectorStorageSettings vectorSettings)
    {
        _vectorSettings = vectorSettings;
    }

    public abstract IVectorStore CreateVectorStore(IServiceProvider serviceProvider);
}