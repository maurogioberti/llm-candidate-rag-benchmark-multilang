namespace Rag.Candidates.Core.Domain.Configuration;

public static class LlmProviderUriResolver
{
    private static readonly string OpenAiSettingsRequiredMessage = "OpenAI settings are required";
    private static readonly string OllamaSettingsRequiredMessage = "Ollama settings are required";

    public static Uri ResolveOpenAi(LlmProviderSettings settings)
    {
        if (settings.OpenAi is null)
        {
            throw new InvalidOperationException(OpenAiSettingsRequiredMessage);
        }

        return new Uri(settings.OpenAi.BaseUrl);
    }

    public static Uri ResolveOllama(LlmProviderSettings settings)
    {
        if (settings.Ollama is null)
        {
            throw new InvalidOperationException(OllamaSettingsRequiredMessage);
        }

        return new Uri(settings.Ollama.BaseUrl);
    }
}