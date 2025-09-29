using Microsoft.OpenApi.Models;
using Rag.Candidates.Api.Core.Application.UseCases;
using Rag.Candidates.Core.Application.Configuration;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Infrastructure.Embeddings;
using Rag.Candidates.Core.Infrastructure.Shared;
using Rag.Candidates.Core.Infrastructure.Shared.VectorStorage;

namespace Rag.Candidates.Api.Extensions;

public static class ServiceCollectionExtensions
{
    public const string SwaggerVersion = "v1";
    public const string SwaggerTitle = "Candidate RAG (Semantic Kernel)";
    public const string SwaggerApiVersion = "1.0.0";

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
        services.AddHttpClient();
        services.AddSingleton<IEmbeddingsClient, HttpEmbeddingsClient>();
        services.AddSingleton<IResourceLoader, ResourceLoader>();
        services.AddSingleton<ILlmFineTuningService, LlmFineTuningService>();
        services.AddSingleton<IInstructionPairsService, InstructionPairsService>();
        services.AddSingleton<LlmProviderFactory>();
        services.AddSingleton<ILlmClient>(provider =>
        {
            var factory = provider.GetRequiredService<LlmProviderFactory>();
            return factory.CreateLlmClient(provider);
        });

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
}