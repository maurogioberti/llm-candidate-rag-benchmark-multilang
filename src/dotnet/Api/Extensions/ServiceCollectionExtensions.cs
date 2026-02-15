using Microsoft.Extensions.AI;
using Microsoft.OpenApi.Models;
using Rag.Candidates.Core.Application.UseCases;
using Rag.Candidates.Core.Application.Configuration;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Application.Services;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Infrastructure.Embeddings;
using Rag.Candidates.Core.Infrastructure.Llm.Adapters;
using Rag.Candidates.Core.Infrastructure.Llm.Factories;
using Rag.Candidates.Core.Infrastructure.Llm.Providers;
using Rag.Candidates.Core.Infrastructure.Llm.Chats;
using Rag.Candidates.Core.Infrastructure.Shared;
using Rag.Candidates.Core.Infrastructure.Shared.VectorStorage;
using Rag.Candidates.Core.Infrastructure.VectorStores.Qdrant;

namespace Rag.Candidates.Api.Extensions;

public static class ServiceCollectionExtensions
{
    public const string SwaggerVersion = "v1";
    public const string SwaggerTitle = "Candidate RAG (Semantic Kernel)";
    public const string SwaggerApiVersion = "1.0.0";
    
    private const string HealthCheckName = "self";
    private const string HealthCheckDescription = "API is running";
    private const string HealthCheckReadyTag = "ready";
    
    private static readonly TimeSpan OllamaTimeout = TimeSpan.FromMinutes(5);

    public static IServiceCollection AddConfiguration(this IServiceCollection services, IConfiguration configuration)
    {
        var configService = new ConfigurationService();
        var settings = configService.LoadSettings();

        services.AddSingleton(settings);
        services.AddSingleton(settings.PythonApi);
        services.AddSingleton(settings.DotnetApi);
        services.AddSingleton(settings.EmbeddingsService);
        services.AddSingleton(settings.VectorStorage);
        services.AddSingleton(settings.LlmProvider);
        services.AddSingleton(settings.Qdrant);
        services.AddSingleton(settings.Data);

        return services;
    }

    public static IServiceCollection AddInfrastructure(this IServiceCollection services)
    {
        services.AddHttpClient(nameof(QdrantVectorStore), client =>
        {
            var settings = services.BuildServiceProvider().GetRequiredService<QdrantSettings>();
            client.BaseAddress = new Uri(settings.Url);
        });
        services.AddHttpClient(nameof(HttpEmbeddingsClient), client =>
        {
            var settings = services.BuildServiceProvider().GetRequiredService<EmbeddingsServiceSettings>();
            client.BaseAddress = new Uri(settings.Url);
        });
        services.AddHttpClient(nameof(OpenAILlmClient), client =>
        {
            var settings = services.BuildServiceProvider().GetRequiredService<LlmProviderSettings>();
            if (settings.OpenAi?.BaseUrl != null)
                client.BaseAddress = new Uri(settings.OpenAi.BaseUrl);
        });
        services.AddHttpClient(nameof(OllamaLlmClient), client =>
        {
            var settings = services.BuildServiceProvider().GetRequiredService<LlmProviderSettings>();
            if (settings.Ollama?.BaseUrl != null)
                client.BaseAddress = new Uri(settings.Ollama.BaseUrl);
            client.Timeout = OllamaTimeout;
        });
        services.AddHttpClient(nameof(OpenAIChatClient), client =>
        {
            var settings = services.BuildServiceProvider().GetRequiredService<LlmProviderSettings>();
            if (settings.OpenAi?.BaseUrl != null)
                client.BaseAddress = new Uri(settings.OpenAi.BaseUrl);
        });
        services.AddHttpClient(nameof(OllamaChatClient), client =>
        {
            var settings = services.BuildServiceProvider().GetRequiredService<LlmProviderSettings>();
            if (settings.Ollama?.BaseUrl != null)
                client.BaseAddress = new Uri(settings.Ollama.BaseUrl);
            client.Timeout = OllamaTimeout;
        });

        services.AddSingleton<IEmbeddingsClient, HttpEmbeddingsClient>();
        services.AddSingleton<IResourceLoader, ResourceLoader>();
        services.AddSingleton<ILlmFineTuningService, LlmFineTuningService>();
        services.AddSingleton<IInstructionPairsService, InstructionPairsService>();
        services.AddSingleton<ISchemaValidationService, SchemaValidationService>();
        services.AddSingleton<ICandidateFactory, CandidateFactory>();
        services.AddLlmProviders();
        services.AddVectorStorage();

        return services;
    }

    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddSingleton<BuildIndexUseCase>();
        services.AddSingleton<AskQuestionUseCase>();

        return services;
    }

    public static IServiceCollection AddPresentation(this IServiceCollection services)
    {
        services.AddEndpointsApiExplorer();
        services.AddSwaggerGen(o =>
        {
            o.SwaggerDoc(SwaggerVersion, new OpenApiInfo
            {
                Title = SwaggerTitle,
                Version = SwaggerApiVersion
            });
        });

        services.AddLogging(o => o.AddConsole());
        
        services.AddHealthChecks()
            .AddCheck(HealthCheckName, () => 
                Microsoft.Extensions.Diagnostics.HealthChecks.HealthCheckResult.Healthy(HealthCheckDescription), 
                tags: new[] { HealthCheckReadyTag });

        return services;
    }

    private static IServiceCollection AddVectorStorage(this IServiceCollection services)
    {
        services.AddSingleton<VectorStoreFactoryRegistry>();
        services.AddSingleton<VectorStoreProvider>();
        services.AddSingleton<IVectorStore>(provider =>
        {
            var vectorStoreProvider = provider.GetRequiredService<VectorStoreProvider>();
            return vectorStoreProvider.CreateVectorStore(provider);
        });

        return services;
    }

    private static IServiceCollection AddLlmProviders(this IServiceCollection services)
    {
        services.AddSingleton<IChatClient>(provider =>
        {
            var httpClientFactory = provider.GetRequiredService<IHttpClientFactory>();
            var settings = provider.GetRequiredService<LlmProviderSettings>();
            return ChatClientFactory.CreateChatClient(httpClientFactory, settings);
        });

        services.AddSingleton<ILlmClient>(provider =>
        {
            var chatClient = provider.GetRequiredService<IChatClient>();
            return new ChatClientAdapter(chatClient);
        });

        return services;
    }
}