using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.AspNetCore.Http.HttpResults;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using System.Text.Json;

namespace Rag.Candidates.Api.Endpoints;

public static class HealthEndpoints
{
    private const string HealthEndpoint = "/health";
    private const string ReadyEndpoint = "/health/ready";
    private const string LiveEndpoint = "/health/live";
    private const string StatusReady = "Ready";
    private const string StatusAlive = "Alive";
    private const string TargetFramework = "net10.0";
    private const string HealthCheckName = "HealthCheck";
    private const string ReadinessCheckName = "ReadinessCheck";
    private const string LivenessCheckName = "LivenessCheck";
    private const string ContentTypeJson = "application/json";

    public static void MapHealthEndpoints(this WebApplication app)
    {
        app.MapHealthChecks(HealthEndpoint, new HealthCheckOptions
        {
            ResponseWriter = async (context, report) =>
            {
                context.Response.ContentType = ContentTypeJson;

                var result = JsonSerializer.Serialize(new
                {
                    status = report.Status.ToString(),
                    timestamp = DateTime.UtcNow,
                    framework = $".NET {Environment.Version}",
                    targetFramework = TargetFramework,
                    checks = report.Entries.Select(e => new
                    {
                        name = e.Key,
                        status = e.Value.Status.ToString(),
                        description = e.Value.Description,
                        duration = e.Value.Duration.TotalMilliseconds,
                        exception = e.Value.Exception?.Message
                    })
                }, new JsonSerializerOptions { WriteIndented = true });

                await context.Response.WriteAsync(result);
            }
        })
        .WithName(HealthCheckName);

        app.MapGet(ReadyEndpoint, () => 
            Results.Ok(new 
            { 
                status = StatusReady, 
                timestamp = DateTime.UtcNow,
                framework = $".NET {Environment.Version}"
            }))
           .WithName(ReadinessCheckName);

        app.MapGet(LiveEndpoint, () => 
            Results.Ok(new 
            { 
                status = StatusAlive, 
                timestamp = DateTime.UtcNow,
                framework = $".NET {Environment.Version}"
            }))
           .WithName(LivenessCheckName);
    }
}
