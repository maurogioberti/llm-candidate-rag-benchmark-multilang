using Rag.Candidates.Api.Endpoints;

namespace Rag.Candidates.Api.Extensions;

public static class WebApplicationExtensions
{
    public const string RouteTemplate = "openapi/{documentName}.json";
    public const string RoutePrefix = "docs";
    public const string SwaggerEndpoint = "/openapi/v1.json";
    public const string SwaggerTitle = "Candidate RAG (Semantic Kernel)";
    public const string SwaggerVersion = "1.0.0";

    public static WebApplication ConfigureSwagger(this WebApplication app)
    {
        app.UseSwagger(c => c.RouteTemplate = RouteTemplate);
        app.UseSwaggerUI(c =>
        {
            c.RoutePrefix = RoutePrefix;
            c.SwaggerEndpoint(SwaggerEndpoint, $"{SwaggerTitle} v{SwaggerVersion}");
        });
        return app;
    }

    public static WebApplication MapEndpoints(this WebApplication app)
    {
        app.MapChatEndpoints();
        return app;
    }
}