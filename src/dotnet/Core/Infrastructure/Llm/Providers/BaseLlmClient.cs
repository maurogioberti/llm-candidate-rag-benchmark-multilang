using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.Providers;

public abstract class BaseLlmClient : ILlmClient
{
    protected readonly HttpClient HttpClient;
    protected readonly LlmProviderSettings Settings;

    protected const string RoleSystem = "system";
    protected const string RoleUser = "user";
    protected const float DefaultTemperature = 0f;

    protected BaseLlmClient(IHttpClientFactory httpFactory, string clientName, LlmProviderSettings settings)
    {
        HttpClient = httpFactory.CreateClient(clientName);
        Settings = settings;
    }

    public async Task<string> GenerateResponseAsync(IEnumerable<ChatMessage> messages, CancellationToken ct = default)
    {
        var request = BuildRequest(messages);
        var endpoint = GetEndpoint();

        using var response = await HttpClient.PostAsJsonAsync(endpoint, request, ct);
        response.EnsureSuccessStatusCode();

        var content = await response.Content.ReadAsStringAsync(ct);
        return ParseResponse(content);
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

    protected virtual object BuildRequest(IEnumerable<ChatMessage> messages)
    {
        return new
        {
            model = Settings.Model,
            messages = messages.Select(m => new { role = m.Role, content = m.Content }),
            temperature = DefaultTemperature
        };
    }

    protected abstract string GetEndpoint();
    protected abstract string ParseResponse(string responseContent);
}
