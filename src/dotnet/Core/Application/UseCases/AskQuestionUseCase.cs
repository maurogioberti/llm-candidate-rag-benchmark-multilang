using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Application.Services;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Entities;
using System.Text.Json;

namespace Rag.Candidates.Core.Application.UseCases;

public sealed class AskQuestionUseCase
{
    private readonly IEmbeddingsClient _embeddingsClient;
    private readonly IVectorStore _vectorStore;
    private readonly ILlmClient _llmClient;
    private readonly IResourceLoader _resourceLoader;
    private readonly string _collection;
    private readonly VectorMetadataConfig _metadataConfig;
    private readonly QueryParser _queryParser;
    private readonly CandidateAggregator _candidateAggregator;
    private readonly CandidateRanker _candidateRanker;
    private readonly MetadataFilterBuilder _filterBuilder;

    private const int DefaultLimit = 6;
    private const string InOperator = "$in";
    private const string AndOperator = "$and";
    private const string GteOperator = "$gte";
    private const string ContextSeparator = "\n\n";
    private const string NewLine = "\n";
    private const string UnknownValue = "unknown";
    private const int DefaultContentLimit = 200;
    private const string ContentSuffix = "...";
    private const string ChatSystemFile = "chat_system.md";
    private const string ChatHumanFile = "chat_human.md";
    private const string NoCandidatesFoundMessage = "No candidates found matching the specified criteria.";
    private const string PreparedKey = "prepared";
    private const string EnglishLevelNumMinKey = "english_level_num_min";

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
        
        _metadataConfig = VectorMetadataConfig.Default;
        _queryParser = new QueryParser();
        _candidateAggregator = new CandidateAggregator(_metadataConfig.FieldCandidateId);
        _candidateRanker = new CandidateRanker(RankingWeights.Default());
        _filterBuilder = new MetadataFilterBuilder(
            candidateIdField: _metadataConfig.FieldCandidateId,
            seniorityField: _metadataConfig.FieldSeniorityLevel,
            yearsExperienceField: _metadataConfig.FieldYearsExperience,
            skillNameField: _metadataConfig.FieldSkillName,
            typeField: _metadataConfig.FieldType,
            typeSkill: _metadataConfig.TypeSkill
        );
    }

    public async Task<ChatResult> ExecuteAsync(ChatRequestDto request, CancellationToken ct = default)
    {
        var parsedQuery = _queryParser.Parse(request.Question);
        
        var queryEmbedding = await _embeddingsClient.EmbedAsync([request.Question], ct);
        var metadataFilter = BuildMetadataFilter(request.Filters, parsedQuery);

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

        var searchResultsList = searchResults.Select(r => (r.Document, r.Metadata, (double)r.Score)).ToList();
        var aggregatedCandidates = _candidateAggregator.Aggregate(searchResultsList);
        var filteredCandidates = _filterBuilder.FilterAggregatedCandidates(aggregatedCandidates, parsedQuery);

        if (filteredCandidates.Count == 0)
        {
            return new ChatResult
            {
                Answer = NoCandidatesFoundMessage,
                Sources = Array.Empty<ChatSource>()
            };
        }

        var rankedCandidates = _candidateRanker.Rank(filteredCandidates, parsedQuery);

        var context = BuildContextFromCandidates(rankedCandidates);
        var sources = ExtractSourcesFromCandidates(rankedCandidates);

        var systemPrompt = await GetSystemPrompt(ct);
        var humanPrompt = await GetHumanPrompt(context, request.Question, ct);

        var llmOutput = await _llmClient.GenerateChatCompletionAsync(systemPrompt, humanPrompt, context, ct);
        
        var parsedResponse = ParseAndValidateLlmOutput(llmOutput);
        
        var answer = FormatFinalAnswer(parsedResponse);
        
        var metadata = BuildResponseMetadata(parsedResponse);

        return new ChatResult
        {
            Answer = answer,
            Sources = sources,
            Metadata = metadata
        };
    }

    private Dictionary<string, object>? BuildMetadataFilter(ChatFilters? filters, Domain.Entities.ParsedQuery parsedQuery)
    {
        var conditions = new List<Dictionary<string, object>>();

        if (filters != null)
        {
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
                conditions.Add(new Dictionary<string, object> { [_metadataConfig.FieldCandidateId] = new Dictionary<string, object> { [InOperator] = filters.CandidateIds } });
            }
        }

        var queryFilters = _filterBuilder.BuildCandidateFilters(parsedQuery);
        conditions.AddRange(queryFilters);

        var techFilter = _filterBuilder.BuildTechnologyFilters(parsedQuery);
        if (techFilter != null)
        {
            conditions.Add(techFilter);
        }

        if (conditions.Count == 0)
            return null;

        if (conditions.Count == 1)
            return conditions[0];

        return new Dictionary<string, object> { [AndOperator] = conditions };
    }

    private static string BuildContextFromCandidates(List<RankedCandidate> candidates)
    {
        var contextParts = new List<string>();
        foreach (var candidate in candidates)
        {
            contextParts.AddRange(candidate.Documents);
        }
        return string.Join(ContextSeparator, contextParts);
    }

    private ChatSource[] ExtractSourcesFromCandidates(List<RankedCandidate> candidates)
    {
        var sources = new List<ChatSource>();
        foreach (var candidate in candidates)
        {
            for (int i = 0; i < candidate.Documents.Count; i++)
            {
                var document = candidate.Documents[i];
                var score = i < candidate.AllScores.Count ? candidate.AllScores[i] : 0.0;
                var section = candidate.Metadata.TryGetValue(_metadataConfig.FieldType, out var type) 
                    ? type.ToString() ?? UnknownValue 
                    : UnknownValue;
                var content = document.Length > DefaultContentLimit 
                    ? document[..DefaultContentLimit] + ContentSuffix 
                    : document;

                sources.Add(new ChatSource
                {
                    CandidateId = candidate.CandidateId,
                    Section = section,
                    Content = content,
                    Score = (float)score
                });
            }
        }
        return sources.ToArray();
    }

    private static string BuildContext((string Document, Dictionary<string, object> Metadata, float Score)[] searchResults)
    {
        var contextParts = searchResults.Select(result => result.Document);
        return string.Join(ContextSeparator, contextParts);
    }

    private ChatSource[] ExtractSources((string Document, Dictionary<string, object> Metadata, float Score)[] searchResults)
    {
        return searchResults.Select(result =>
        {
            var candidateId = result.Metadata.TryGetValue(_metadataConfig.FieldCandidateId, out var id) ? id.ToString() ?? UnknownValue : UnknownValue;
            var section = result.Metadata.TryGetValue(_metadataConfig.FieldType, out var type) ? type.ToString() ?? UnknownValue : UnknownValue;
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
    
    private LlmResponseSchema ParseAndValidateLlmOutput(string llmOutput)
    {
        try
        {
            var jsonStart = llmOutput.IndexOf('{');
            var jsonEnd = llmOutput.LastIndexOf('}');
            
            if (jsonStart == -1 || jsonEnd == -1 || jsonEnd <= jsonStart)
            {
                throw new InvalidOperationException("No JSON object found in LLM output");
            }
            
            var jsonStr = llmOutput.Substring(jsonStart, jsonEnd - jsonStart + 1);
            var jsonDoc = JsonDocument.Parse(jsonStr);
            var root = jsonDoc.RootElement;
            
            if (!root.TryGetProperty("justification", out _))
            {
                throw new InvalidOperationException("Missing required field: justification");
            }
            
            var justification = root.GetProperty("justification").GetString() ?? string.Empty;
            
            SelectedCandidate? selectedCandidate = null;
            
            if (root.TryGetProperty("selected_candidate", out var candidateElement) && 
                candidateElement.ValueKind != JsonValueKind.Null)
            {
                if (!candidateElement.TryGetProperty("fullname", out _) ||
                    !candidateElement.TryGetProperty("candidate_id", out _) ||
                    !candidateElement.TryGetProperty("rank", out _))
                {
                    throw new InvalidOperationException("selected_candidate must contain fullname, candidate_id, and rank");
                }
                
                selectedCandidate = new SelectedCandidate
                {
                    Fullname = candidateElement.GetProperty("fullname").GetString() ?? string.Empty,
                    CandidateId = candidateElement.GetProperty("candidate_id").GetString() ?? string.Empty,
                    Rank = candidateElement.GetProperty("rank").GetInt32()
                };
            }
            
            return new LlmResponseSchema
            {
                SelectedCandidate = selectedCandidate,
                Justification = justification
            };
        }
        catch (Exception ex) when (ex is JsonException or InvalidOperationException)
        {
            throw new InvalidOperationException($"Failed to parse LLM output as valid JSON schema: {ex.Message}", ex);
        }
    }
    
    private string FormatFinalAnswer(LlmResponseSchema parsedResponse)
    {
        if (parsedResponse.SelectedCandidate is null)
        {
            return $"No candidate selected.\n\n{parsedResponse.Justification}";
        }
        
        return $"Selected Candidate: {parsedResponse.SelectedCandidate.Fullname} " +
               $"(ID: {parsedResponse.SelectedCandidate.CandidateId}, Rank: {parsedResponse.SelectedCandidate.Rank})\n\n" +
               $"Justification: {parsedResponse.Justification}";
    }
    
    private Dictionary<string, object> BuildResponseMetadata(LlmResponseSchema parsedResponse)
    {
        var metadata = new Dictionary<string, object>
        {
            ["justification"] = parsedResponse.Justification
        };
        
        if (parsedResponse.SelectedCandidate is not null)
        {
            metadata["selected_candidate"] = new Dictionary<string, object>
            {
                ["fullname"] = parsedResponse.SelectedCandidate.Fullname,
                ["candidate_id"] = parsedResponse.SelectedCandidate.CandidateId,
                ["rank"] = parsedResponse.SelectedCandidate.Rank
            };
        }
        else
        {
            metadata["selected_candidate"] = null!;
        }
        
        return metadata;
    }
}