using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Application.UseCases;

public sealed class AskQuestionUseCase
{
    private readonly IEmbeddingsClient _embeddingsClient;
    private readonly IVectorStore _vectorStore;
    private readonly ILlmClient _llmClient;
    private readonly IResourceLoader _resourceLoader;
    private readonly string _collection;

    private const int DefaultLimit = 6;
    private const string PreparedKey = "prepared";
    private const string EnglishLevelNumMinKey = "english_level_num_min";
    private const string CandidateIdKey = "candidate_id";
    private const string InOperator = "$in";
    private const string AndOperator = "$and";
    private const string GteOperator = "$gte";
    private const string ContextSeparator = "\n\n";
    private const string NewLine = "\n";
    private const string UnknownValue = "unknown";
    private const string TypeKey = "type";
    private const int DefaultContentLimit = 200;
    private const string ContentSuffix = "...";
    private const string ChatSystemFile = "chat_system.md";
    private const string ChatHumanFile = "chat_human.md";
    private const string NoCandidatesFoundMessage = "No candidates found matching the specified criteria.";

    public AskQuestionUseCase(
        IEmbeddingsClient embeddingsClient,
        IVectorStore vectorStore,
        ILlmClient llmClient,
        IResourceLoader resourceLoader,
        VectorStorageSettings vectorSettings)
    {
        _embeddingsClient = embeddingsClient;
        _vectorStore = vectorStore;
        _llmClient = llmClient;
        _resourceLoader = resourceLoader;
        _collection = vectorSettings.CollectionName;
    }

    public async Task<ChatResult> ExecuteAsync(ChatRequestDto request, CancellationToken ct = default)
    {
        var queryEmbedding = await _embeddingsClient.EmbedAsync([request.Question], ct);
        var metadataFilter = BuildMetadataFilter(request.Filters);

        var searchResults = await _vectorStore.SearchAsync(
            collection: _collection,
            queryVector: queryEmbedding[0],
            limit: DefaultLimit,
            filter: metadataFilter,
            ct: ct
        );

        if (searchResults.Length == 0)
        {
            return new ChatResult
            {
                Answer = NoCandidatesFoundMessage,
                Sources = Array.Empty<ChatSource>()
            };
        }

        var context = BuildContext(searchResults);
        var sources = ExtractSources(searchResults);

        var systemPrompt = await GetSystemPrompt(ct);
        var humanPrompt = await GetHumanPrompt(context, request.Question, ct);

        var answer = await _llmClient.GenerateChatCompletionAsync(systemPrompt, humanPrompt, context, ct);

        return new ChatResult
        {
            Answer = answer,
            Sources = sources
        };
    }

    private static Dictionary<string, object>? BuildMetadataFilter(ChatFilters? filters)
    {
        if (filters == null)
            return null;

        var conditions = new List<Dictionary<string, object>>();

        if (filters.Prepared.HasValue)
        {
            conditions.Add(new Dictionary<string, object> { [PreparedKey] = filters.Prepared.Value });
        }

        if (!string.IsNullOrEmpty(filters.EnglishMin))
        {
            var englishLevelNum = EnglishLevelToNum(filters.EnglishMin);
            conditions.Add(new Dictionary<string, object> { [EnglishLevelNumMinKey] = new Dictionary<string, object> { [GteOperator] = englishLevelNum } });
        }

        if (filters.CandidateIds?.Length > 0)
        {
            conditions.Add(new Dictionary<string, object> { [CandidateIdKey] = new Dictionary<string, object> { [InOperator] = filters.CandidateIds } });
        }

        if (conditions.Count == 0)
            return null;

        if (conditions.Count == 1)
            return conditions[0];

        return new Dictionary<string, object> { [AndOperator] = conditions };
    }

    private static string BuildContext((string Document, Dictionary<string, object> Metadata, float Score)[] searchResults)
    {
        var contextParts = searchResults.Select(result => result.Document);
        return string.Join(ContextSeparator, contextParts);
    }

    private static ChatSource[] ExtractSources((string Document, Dictionary<string, object> Metadata, float Score)[] searchResults)
    {
        return searchResults.Select(result =>
        {
            var candidateId = result.Metadata.TryGetValue(CandidateIdKey, out var id) ? id.ToString() ?? UnknownValue : UnknownValue;
            var section = result.Metadata.TryGetValue(TypeKey, out var type) ? type.ToString() ?? UnknownValue : UnknownValue;
            var content = result.Document.Length > DefaultContentLimit 
                ? result.Document[..DefaultContentLimit] + ContentSuffix 
                : result.Document;

            return new ChatSource
            {
                CandidateId = candidateId,
                Section = section,
                Content = content,
                Score = result.Score
            };
        }).ToArray();
    }

    private async Task<string> GetSystemPrompt(CancellationToken ct)
    {
        return await _resourceLoader.LoadPromptAsync(ChatSystemFile, ct);
    }

    private async Task<string> GetHumanPrompt(string context, string question, CancellationToken ct)
    {
        var humanTemplate = await _resourceLoader.LoadPromptAsync(ChatHumanFile, ct);
        return humanTemplate.Replace("{context}", context).Replace("{input}", question);
    }

    private static int EnglishLevelToNum(string level)
    {
        if (string.IsNullOrEmpty(level))
            return 0;

        return level.ToUpperInvariant() switch
        {
            "A1" => 1,
            "A2" => 2,
            "B1" => 3,
            "B2" => 4,
            "C1" => 5,
            "C2" => 6,
            "BASIC" => 2,
            "CONVERSATIONAL" => 3,
            "FLUENT" => 5,
            "NATIVE" => 6,
            "ADVANCED" => 5,
            _ => 0
        };
    }
}