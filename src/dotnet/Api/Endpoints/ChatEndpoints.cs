using Rag.Candidates.Api.Api.Contracts.Request;
using Rag.Candidates.Api.Api.Contracts.Response;
using Rag.Candidates.Api.Core.Application.UseCases;

namespace Rag.Candidates.Api.Api.Endpoints;

public static class ChatEndpoints
{
    private const string HealthEndpoint = "/health";
    private const string IndexEndpoint = "/index";
    private const string ChatEndpoint = "/chat";

    private const string StatusOk = "ok";

    public static void MapChatEndpoints(this WebApplication app)
    {
        app.MapGet(HealthEndpoint, () => Results.Json(new { status = StatusOk }));

        app.MapPost(IndexEndpoint, async (BuildIndexUseCase buildIndex, ILoggerFactory lf) =>
        {
            await Task.CompletedTask;

            var response = new IndexedResponse(new IndexedData(Candidates: "", Chunks: ""));

            return Results.Json(response);
        });

        app.MapPost(ChatEndpoint, async (ChatRequest req, AskQuestionUseCase askQuestion, ILoggerFactory lf) =>
        {
            await Task.CompletedTask;

            var response = new ChatResponse(
                Answer: "",
                Sources: ""
            );

            return Results.Json(response);
        });
    }
}