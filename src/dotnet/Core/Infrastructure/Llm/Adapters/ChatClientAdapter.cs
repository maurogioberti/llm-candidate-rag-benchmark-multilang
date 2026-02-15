using Microsoft.Extensions.AI;
using Rag.Candidates.Core.Application.Interfaces;
using AppChatMessage = Rag.Candidates.Core.Application.Interfaces.ChatMessage;
using AIChatMessage = Microsoft.Extensions.AI.ChatMessage;

namespace Rag.Candidates.Core.Infrastructure.Llm.Adapters;

public sealed class ChatClientAdapter(IChatClient chatClient) : ILlmClient
{
    private const string SystemRole = "system";
    private const string UserRole = "user";

    public async Task<string> GenerateResponseAsync(IEnumerable<AppChatMessage> messages, CancellationToken cancellationToken = default)
    {
        var aiMessages = messages.Select(m => new AIChatMessage(
            new ChatRole(m.Role.ToLowerInvariant()),
            m.Content
        ));

        var response = await chatClient.GetResponseAsync(aiMessages, cancellationToken: cancellationToken);
        return response.Messages.LastOrDefault()?.Text ?? string.Empty;
    }

    public async Task<string> GenerateChatCompletionAsync(
        string systemPrompt,
        string userMessage,
        string? context = null,
        CancellationToken cancellationToken = default)
    {
        var messages = new List<AppChatMessage>
        {
            new(SystemRole, systemPrompt)
        };

        if (!string.IsNullOrEmpty(context))
        {
            messages.Add(new(SystemRole, context));
        }

        messages.Add(new(UserRole, userMessage));

        return await GenerateResponseAsync(messages, cancellationToken);
    }
}
