namespace Rag.Candidates.Core.Application.Interfaces;

public interface ILlmClient
{
    Task<string> GenerateResponseAsync(IEnumerable<ChatMessage> messages, CancellationToken ct = default);
    Task<string> GenerateChatCompletionAsync(string systemPrompt, string userMessage, string? context = null, CancellationToken ct = default);
}

public record ChatMessage(string Role, string Content);