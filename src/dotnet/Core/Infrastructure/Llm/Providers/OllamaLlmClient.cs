using System.Text.Json;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.Providers;

public sealed class OllamaLlmClient : BaseLlmClient
{
    private const string ChatCompletionsEndpoint = "/api/chat";

    public OllamaLlmClient(IHttpClientFactory httpFactory, LlmProviderSettings settings) 
        : base(httpFactory, nameof(OllamaLlmClient), settings)
    {
    }

    protected override object BuildRequest(IEnumerable<ChatMessage> messages)
    {
        return new
        {
            model = Settings.Model,
            messages = messages.Select(m => new { role = m.Role, content = m.Content }),
            temperature = DefaultTemperature,
            stream = false
        };
    }

    protected override string GetEndpoint() => ChatCompletionsEndpoint;

    protected override string ParseResponse(string responseContent)
    {
        var result = JsonSerializer.Deserialize<OllamaResponse>(responseContent);
        return result?.Message?.Content ?? string.Empty;
    }

    private record OllamaResponse(Message? Message);
    private record Message(string? Content);
}