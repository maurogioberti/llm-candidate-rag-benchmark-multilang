using Microsoft.Extensions.AI;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.Llm.Factories;

namespace Rag.Candidates.Api.Extensions;

public static class ChatClientExtensions
{
    public static IServiceCollection AddChatClient(this IServiceCollection services, LlmProviderSettings settings)
    {
        services.AddSingleton<IChatClient>(sp =>
        {
            var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
            return ChatClientFactory.CreateChatClient(httpClientFactory, settings);
        });

        return services;
    }
}
