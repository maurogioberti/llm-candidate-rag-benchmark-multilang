using Microsoft.Extensions.AI;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.Llm.Chats;

namespace Rag.Candidates.Core.Infrastructure.Llm.Factories;

public static class ChatClientFactory
{
    private const string OllamaProvider = "ollama";
    private const string OpenAIProvider = "openai";

    public static IChatClient CreateChatClient(
        IHttpClientFactory httpClientFactory,
        LlmProviderSettings settings)
    {
        return settings.Provider.ToLowerInvariant() switch
        {
            OllamaProvider => new OllamaChatClient(httpClientFactory, settings),
            OpenAIProvider => new OpenAIChatClient(httpClientFactory, settings),
            _ => throw new NotSupportedException($"Provider type '{settings.Provider}' is not supported")
        };
    }
}
