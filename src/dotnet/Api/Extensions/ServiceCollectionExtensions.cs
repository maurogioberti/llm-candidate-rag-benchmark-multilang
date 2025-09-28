using Microsoft.OpenApi.Models;
using Rag.Candidates.Api.Core.Application.UseCases;

namespace Rag.Candidates.Api.Api.Extensions;

public static class ServiceCollectionExtensions
{
    public const string SwaggerVersion = "v1";
    public const string SwaggerTitle = "Candidate RAG (Semantic Kernel)";
    public const string SwaggerApiVersion = "1.0.0";

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
}