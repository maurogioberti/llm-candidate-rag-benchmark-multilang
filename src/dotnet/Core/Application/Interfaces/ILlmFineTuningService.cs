namespace Rag.Candidates.Core.Application.Interfaces;

public interface ILlmFineTuningService
{
    Task ExportForOpenAIAsync(CancellationToken ct = default);
    Task ExportForInstructAsync(CancellationToken ct = default);
}