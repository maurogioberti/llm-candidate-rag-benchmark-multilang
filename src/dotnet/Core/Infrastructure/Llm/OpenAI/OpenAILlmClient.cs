using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.OpenAI;

public sealed class OpenAILlmClient : ILlmClient
{
    private readonly HttpClient _http;
    private readonly LlmProviderSettings _settings;

    private const string ChatCompletionsEndpoint = "/v1/chat/completions";
    private const string RoleSystem = "system";
    private const string RoleUser = "user";
    private const float DefaultTemperature = 0f;

    public OpenAILlmClient(IHttpClientFactory httpFactory, LlmProviderSettings settings)
    {
        _http = httpFactory.CreateClient(nameof(OpenAILlmClient));
        _settings = settings;
    }

    public async Task<string> GenerateResponseAsync(IEnumerable<ChatMessage> messages, CancellationToken ct = default)
    {
        var request = new
        {
            model = _settings.Model,
            messages = messages.Select(m => new { role = m.Role, content = m.Content }),
            temperature = DefaultTemperature
        };

        using var response = await _http.PostAsJsonAsync(ChatCompletionsEndpoint, request, ct);
        response.EnsureSuccessStatusCode();

        var result = await response.Content.ReadFromJsonAsync<OpenAIResponse>(cancellationToken: ct);
        return result?.Choices?.FirstOrDefault()?.Message?.Content ?? string.Empty;
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

    private record OpenAIResponse(Choice[]? Choices);
    private record Choice(Message? Message);
    private record Message(string? Content);
}