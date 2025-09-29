namespace Rag.Candidates.Core.Application.Interfaces;

public interface IVectorStoreFactory
{
    IVectorStore CreateVectorStore(IServiceProvider serviceProvider);
}