using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.Ollama;

public sealed class OllamaLlmClient(IHttpClientFactory httpFactory, LlmProviderSettings settings) : ILlmClient
{
    private readonly HttpClient _http = httpFactory.CreateClient(nameof(OllamaLlmClient));

    private const string ChatCompletionsEndpoint = "/api/chat";
    private const string RoleSystem = "system";
    private const string RoleUser = "user";
    private const float DefaultTemperature = 0f;

    public async Task<string> GenerateResponseAsync(IEnumerable<ChatMessage> messages, CancellationToken ct = default)
    {
        var request = new
        {
            model = settings.Model,
            messages = messages.Select(m => new { role = m.Role, content = m.Content }),
            temperature = DefaultTemperature,
            stream = false
        };

        using var response = await _http.PostAsJsonAsync(ChatCompletionsEndpoint, request, ct);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadFromJsonAsync<OllamaResponse>(cancellationToken: ct);
        return result?.Message?.Content ?? string.Empty;
    }

    public async Task<string> GenerateChatCompletionAsync(string systemPrompt, string userMessage, string? context = null, CancellationToken ct = default)
    {
        var messages = new List<ChatMessage>
        {
            new(RoleSystem, systemPrompt),
            new(RoleUser, userMessage)
        };

        if (!string.IsNullOrWhiteSpace(context))
        {
            messages.Insert(1, new(RoleUser, $"Context: {context}"));
        }

        return await GenerateResponseAsync(messages, ct);
    }

    private record OllamaResponse(Message? Message);
    private record Message(string? Content);
}