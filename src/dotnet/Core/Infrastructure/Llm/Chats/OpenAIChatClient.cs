using System.Text.Json;
using Microsoft.Extensions.AI;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.Chats;

public sealed class OpenAIChatClient(IHttpClientFactory httpFactory, LlmProviderSettings settings)
    : BaseChatClient(httpFactory, nameof(OpenAIChatClient), settings, ProviderName, LlmProviderUriResolver.ResolveOpenAi(settings))
{
    private const string ChatCompletionsEndpoint = "/v1/chat/completions";
    private const string ProviderName = "OpenAI";

    protected override string GetEndpoint() => ChatCompletionsEndpoint;

    protected override string ParseResponse(string responseContent)
    {
        var result = JsonSerializer.Deserialize<OpenAIResponse>(responseContent);
        return result?.Choices?.FirstOrDefault()?.Message?.Content ?? string.Empty;
    }

    private record OpenAIResponse(Choice[]? Choices);
    private record Choice(Message? Message);
    private record Message(string? Content);
}