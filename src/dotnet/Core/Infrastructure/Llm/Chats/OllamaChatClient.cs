using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.AI;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.Llm.Providers;

namespace Rag.Candidates.Core.Infrastructure.Llm.Chats;

public sealed class OllamaChatClient(IHttpClientFactory httpFactory, LlmProviderSettings settings)
    : BaseChatClient(httpFactory, nameof(OllamaChatClient), settings, ProviderName, LlmProviderUriResolver.ResolveOllama(settings))
{
    private const string ChatCompletionsEndpoint = "/api/chat";
    private const string ProviderName = "Ollama";
    private const string SettingsRequiredMessage = "Ollama settings are required";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    protected override object BuildRequest(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options)
    {
        return new
        {
            model = options?.ModelId ?? ModelId,
            messages = chatMessages.Select(m => new
            {
                role = m.Role.Value,
                content = m.Text
            }),
            temperature = options?.Temperature ?? DefaultTemperature,
            stream = false
        };
    }

    protected override string GetEndpoint() => ChatCompletionsEndpoint;

    protected override string ParseResponse(string responseContent)
    {
        var result = JsonSerializer.Deserialize<OllamaResponse>(responseContent, JsonOptions);
        return result?.Message?.Content ?? string.Empty;
    }

    private sealed record OllamaResponse
    {
        [JsonPropertyName("message")]
        public OllamaMessage? Message { get; init; }
    }

    private sealed record OllamaMessage
    {
        [JsonPropertyName("role")]
        public string? Role { get; init; }

        [JsonPropertyName("content")]
        public string? Content { get; init; }
    }
}