using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.Llm.Providers;

namespace Rag.Candidates.Core.Infrastructure.Shared;

public sealed class LlmProviderFactory(LlmProviderSettings settings)
{
    private const string SupportedProvidersSeparator = ", ";

    public ILlmClient CreateLlmClient(IServiceProvider serviceProvider)
    {
        var providerType = ParseProviderType(settings.Provider);
        var httpFactory = serviceProvider.GetRequiredService<IHttpClientFactory>();

        return providerType switch
        {
            LlmProviderType.OpenAI => new OpenAILlmClient(httpFactory, settings),
            LlmProviderType.Ollama => new OllamaLlmClient(httpFactory, settings),
            _ => throw new NotSupportedException($"LLM provider '{settings.Provider}' is not supported")
        };
    }

    private static LlmProviderType ParseProviderType(string provider)
    {
        if (Enum.TryParse<LlmProviderType>(provider, ignoreCase: true, out var result))
            return result;

        var supported = string.Join(SupportedProvidersSeparator, Array.ConvertAll(Enum.GetNames(typeof(LlmProviderType)), n => n.ToLowerInvariant()));
        throw new NotSupportedException($"LLM provider '{provider}' is not supported. Supported providers: {supported}");
    }
}