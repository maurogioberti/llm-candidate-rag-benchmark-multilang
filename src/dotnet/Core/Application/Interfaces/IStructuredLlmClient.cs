using Rag.Candidates.Core.Application.DTOs;

namespace Rag.Candidates.Core.Application.Interfaces;

public interface IStructuredLlmClient<T> where T : class
{
    Task<T> GenerateStructuredAsync(ChatContext context, CancellationToken ct = default);
}
