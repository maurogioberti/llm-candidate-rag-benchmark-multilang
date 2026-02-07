using Microsoft.Extensions.AI;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Llm.Chats;

public abstract class BaseChatClient : IChatClient
{
    protected readonly HttpClient HttpClient;
    protected readonly string ModelId;

    protected const float DefaultTemperature = 0f;
    protected const string StreamingNotImplementedMessage = "Streaming is not implemented for this chat client";

    public ChatClientMetadata Metadata { get; }

    protected BaseChatClient(
        IHttpClientFactory httpFactory,
        string clientName,
        LlmProviderSettings settings,
        string providerName,
        Uri providerUri)
    {
        HttpClient = httpFactory.CreateClient(clientName);
        ModelId = settings.Model;
        Metadata = new ChatClientMetadata(
            providerName: providerName,
            providerUri: providerUri,
            defaultModelId: ModelId
        );
    }

    public async Task<ChatResponse> GetResponseAsync(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options = null,
        CancellationToken cancellationToken = default)
    {
        var request = BuildRequest(chatMessages, options);
        var endpoint = GetEndpoint();

        using var response = await HttpClient.PostAsJsonAsync(endpoint, request, cancellationToken);
        response.EnsureSuccessStatusCode();

        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        var messageContent = ParseResponse(content);

        return new ChatResponse([new ChatMessage(ChatRole.Assistant, messageContent)])
        {
            ModelId = ModelId
        };
    }

    public IAsyncEnumerable<ChatResponseUpdate> GetStreamingResponseAsync(
        IEnumerable<ChatMessage> chatMessages,
        ChatOptions? options = null,
        CancellationToken cancellationToken = default)
    {
        throw new NotImplementedException(StreamingNotImplementedMessage);
    }

    public object? GetService(Type serviceType, object? serviceKey = null)
    {
        return serviceType.IsInstanceOfType(this) ? this : null;
    }

    public void Dispose()
    {
    }

    protected virtual object BuildRequest(IEnumerable<ChatMessage> chatMessages, ChatOptions? options)
    {
        return new
        {
            model = options?.ModelId ?? ModelId,
            messages = chatMessages.Select(m => new { role = m.Role.Value, content = m.Text }),
            temperature = options?.Temperature ?? DefaultTemperature
        };
    }

    protected abstract string GetEndpoint();
    protected abstract string ParseResponse(string responseContent);
}
