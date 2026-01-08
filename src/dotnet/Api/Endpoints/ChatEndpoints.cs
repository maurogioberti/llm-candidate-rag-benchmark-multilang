using Rag.Candidates.Api.Contracts.Request;
using Rag.Candidates.Api.Contracts.Response;
using Rag.Candidates.Core.Application.UseCases;

namespace Rag.Candidates.Api.Endpoints;

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
            var result = await buildIndex.ExecuteAsync();

            var response = new IndexedResponse(new IndexedData(
                Candidates: result.Candidates.ToString(), 
                Chunks: result.Chunks.ToString()
            ));

            return Results.Json(response);
        });

        app.MapPost(ChatEndpoint, async (ChatRequest req, AskQuestionUseCase askQuestion, ILoggerFactory lf) =>
        {
            var request = new Core.Application.DTOs.ChatRequestDto
            {
                Question = req.Question,
                Filters = req.Filters != null ? new Core.Application.DTOs.ChatFilters
                {
                    Prepared = req.Filters.Prepared,
                    EnglishMin = req.Filters.EnglishMin,
                    CandidateIds = req.Filters.CandidateIds
                } : null
            };

            var result = await askQuestion.ExecuteAsync(request);

            var response = new ChatResponse(
                Answer: result.Answer,
                Sources: result.Sources,
                Metadata: result.Metadata
            );

            return Results.Json(response);
        });
    }
}