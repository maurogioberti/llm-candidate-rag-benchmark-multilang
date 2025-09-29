using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;
using System.Text.Json;

namespace Rag.Candidates.Core.Application.UseCases;

public sealed class BuildIndexUseCase
{
    private readonly IEmbeddingsClient _embeddingsClient;
    private readonly IVectorStore _vectorStore;
    private readonly IResourceLoader _resourceLoader;
    private readonly ILlmFineTuningService _fineTuningService;
    private readonly ICandidateFactory _candidateFactory;
    private readonly IInstructionPairsService _instructionPairsService;
    private readonly string _collection;

    private const string TypeKey = "type";
    private const string TypeCandidate = "candidate";
    private const string TypeLlmInstruction = "llm_instruction";
    private const string CandidateIdKey = "candidate_id";
    private const string PreparedKey = "prepared";
    private const string EnglishLevelKey = "english_level";
    private const string EnglishLevelNumKey = "english_level_num";
    private const string RowIdKey = "_row_id";
    private const string LlmPrefix = "[LLMInstruction]";
    private const string ProviderSemanticKernel = "Semantic Kernel";

    public BuildIndexUseCase(
        IEmbeddingsClient embeddingsClient,
        IVectorStore vectorStore,
        IResourceLoader resourceLoader,
        ILlmFineTuningService fineTuningService,
        ICandidateFactory candidateFactory,
        IInstructionPairsService instructionPairsService,
        VectorStorageSettings vectorSettings)
    {
        _embeddingsClient = embeddingsClient;
        _vectorStore = vectorStore;
        _resourceLoader = resourceLoader;
        _fineTuningService = fineTuningService;
        _candidateFactory = candidateFactory;
        _instructionPairsService = instructionPairsService;
        _collection = vectorSettings.CollectionName;
    }

    public async Task<IndexInfo> ExecuteAsync(CancellationToken ct = default)
    {
        await _vectorStore.EnsureCollectionAsync(_collection, ct);

        var documents = new List<string>();
        var metadata = new List<Dictionary<string, object>>();

        // Load candidates
        var candidateRecords = await _resourceLoader.LoadCandidateRecordsAsync(ct);
        foreach (var candidateJson in candidateRecords)
        {
            try
            {
                var candidate = _candidateFactory.FromJsonToCandidate(candidateJson, Path.GetFileNameWithoutExtension("candidate"));
                var textBlocks = candidate.ToTextBlocks();

                foreach (var block in textBlocks)
                {
                    documents.Add(block);
                    metadata.Add(new Dictionary<string, object>
                    {
                        [TypeKey] = TypeCandidate,
                        [CandidateIdKey] = candidate.CandidateId,
                        [PreparedKey] = candidate.Prepared,
                        [EnglishLevelKey] = candidate.GeneralInfo?.EnglishLevel ?? "unknown",
                        [EnglishLevelNumKey] = EnglishLevelToNum(candidate.GeneralInfo?.EnglishLevel)
                    });
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Error processing candidate: {ex.Message}", ex);
            }
        }

        // Load LLM instructions
        var llmInstructions = await _resourceLoader.LoadLlmInstructionRecordsAsync(ct);
        foreach (var instruction in llmInstructions)
        {
            var content = $"{LlmPrefix} Instruction: {instruction.Instruction}\nInput:\n{JsonSerializer.Serialize(instruction.Input)}\nOutput:\n{JsonSerializer.Serialize(instruction.Output)}";
            documents.Add(content);
            metadata.Add(new Dictionary<string, object>
            {
                [TypeKey] = TypeLlmInstruction,
                [RowIdKey] = instruction.RowId
            });
        }

        // Load instruction pairs
        var instructionPairs = await _instructionPairsService.GetInstructionPairsAsync(ct: ct);
        foreach (var (text, meta) in instructionPairs)
        {
            documents.Add(text);
            var instructionMetadata = new Dictionary<string, object>(meta)
            {
                [TypeKey] = "instruction_pair"
            };
            metadata.Add(instructionMetadata);
        }

        if (documents.Count == 0)
        {
            return new IndexInfo(0, 0, 0, ProviderSemanticKernel);
        }

        // Generate embeddings
        var embeddings = await _embeddingsClient.EmbedAsync(documents, ct);

        // Upsert to vector store
        var items = documents.Select((doc, index) => (
            Id: index.ToString(),
            Vector: embeddings[index],
            Document: doc,
            Metadata: metadata[index]
        ));

        await _vectorStore.UpsertAsync(_collection, items, ct);

        // Get total count
        var totalPoints = await _vectorStore.CountAsync(_collection, ct);

        return new IndexInfo(
            Candidates: candidateRecords.Length,
            Chunks: documents.Count,
            Points: totalPoints,
            Provider: ProviderSemanticKernel
        );
    }

    private static int EnglishLevelToNum(string? level)
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