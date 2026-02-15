using System.Text.Json;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.Providers;

public sealed class OpenAILlmClient : BaseLlmClient
{
    private const string ChatCompletionsEndpoint = "/v1/chat/completions";

    public OpenAILlmClient(IHttpClientFactory httpFactory, LlmProviderSettings settings)
        : base(httpFactory, nameof(OpenAILlmClient), settings)
    {
    }

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