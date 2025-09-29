namespace Rag.Candidates.Core.Application.Interfaces;

public interface IResourceLoader
{
    Task<string> LoadPromptAsync(string name, CancellationToken ct = default);
    Task<string[]> LoadCandidateRecordsAsync(CancellationToken ct = default);
    Task<LlmInstructionRecord[]> LoadLlmInstructionRecordsAsync(CancellationToken ct = default);
}

public record LlmInstructionRecord(string Instruction, object Input, object Output, int RowId = 0);