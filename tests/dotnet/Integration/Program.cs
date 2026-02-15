using Microsoft.Extensions.DependencyInjection;
using System.Text.Json;
using Rag.Candidates.Core.Application.UseCases;
using Rag.Candidates.Core.Application.Services;
using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Application.Configuration;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Infrastructure.Embeddings;
using Rag.Candidates.Core.Infrastructure.VectorStores.Native;
using Rag.Candidates.Core.Infrastructure.Shared;
using Rag.Candidates.Core.Domain.Configuration;

// Test Constants
const string TEST_QUERY_JAVA = "who is the best candidate for java?";
const string EXPECTED_JAVA_CANDIDATE_FULLNAME = "Jan-Claudiu Crisan";
const string EXPECTED_CANDIDATE_ID_FRAGMENT = "JanClaudiuCrisan";

Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine(".NET INTEGRATION TEST: Java Candidate Returns Human Fullname");
Console.WriteLine("=".PadRight(80, '='));

// Setup DI
var services = new ServiceCollection();
var configService = new ConfigurationService();
var settings = configService.LoadSettings();

services.AddSingleton(settings);
services.AddSingleton(settings.EmbeddingsService);
services.AddSingleton(settings.VectorStorage);
services.AddSingleton(settings.LlmProvider);
services.AddSingleton(settings.Data);

services.AddHttpClient(nameof(HttpEmbeddingsClient), client =>
{
    client.BaseAddress = new Uri(settings.EmbeddingsService.Url);
});

services.AddSingleton<IEmbeddingsClient, HttpEmbeddingsClient>();
services.AddSingleton<IVectorStore, InMemoryVectorStore>();
services.AddSingleton<IResourceLoader, ResourceLoader>();
services.AddSingleton<ILlmFineTuningService, LlmFineTuningService>();
services.AddSingleton<IInstructionPairsService, InstructionPairsService>();
services.AddSingleton<ICandidateFactory, CandidateFactory>();
services.AddSingleton<ISchemaValidationService, SchemaValidationService>();

services.AddSingleton<ILlmClient>(sp =>
{
    var llmSettings = sp.GetRequiredService<LlmProviderSettings>();
    var factory = sp.GetRequiredService<IHttpClientFactory>();
    return new Rag.Candidates.Core.Infrastructure.Llm.Providers.OllamaLlmClient(factory, llmSettings);
});

services.AddSingleton<BuildIndexUseCase>();
services.AddSingleton<AskQuestionUseCase>();

var provider = services.BuildServiceProvider();

Console.WriteLine("\nBuilding index from data/input/...");
var buildIndexUseCase = provider.GetRequiredService<BuildIndexUseCase>();
await buildIndexUseCase.ExecuteAsync();
Console.WriteLine("Index built successfully");

Console.WriteLine($"\nExecuting query: '{TEST_QUERY_JAVA}'");
var askQuestionUseCase = provider.GetRequiredService<AskQuestionUseCase>();
var request = new ChatRequestDto { Question = TEST_QUERY_JAVA };
var result = await askQuestionUseCase.ExecuteAsync(request);

Console.WriteLine("\n" + "-".PadRight(80, '-'));
Console.WriteLine("ASSERTIONS:");
Console.WriteLine("-".PadRight(80, '-'));

if (result.Metadata == null || !result.Metadata.ContainsKey("selected_candidate"))
{
    Console.WriteLine("❌ FAIL: No selected candidate in metadata");
    Environment.Exit(1);
}

var selectedCandidateObj = result.Metadata["selected_candidate"];
if (selectedCandidateObj is null or not Dictionary<string, object>)
{
    Console.WriteLine("❌ FAIL: Invalid selected candidate format in metadata");
    Environment.Exit(1);
}

var selectedCandidate = (Dictionary<string, object>)selectedCandidateObj;
var fullname = selectedCandidate["fullname"]?.ToString() ?? string.Empty;
var candidateId = selectedCandidate["candidate_id"]?.ToString() ?? string.Empty;

Console.WriteLine($"[OK] Selected candidate fullname: {fullname}");
Console.WriteLine($"[OK] Selected candidate ID: {candidateId}");

if (fullname != EXPECTED_JAVA_CANDIDATE_FULLNAME)
{
    Console.WriteLine($"❌ FAIL: Expected fullname '{EXPECTED_JAVA_CANDIDATE_FULLNAME}', got '{fullname}'");
    Environment.Exit(1);
}

if (!candidateId.Contains(EXPECTED_CANDIDATE_ID_FRAGMENT))
{
    Console.WriteLine($"❌ FAIL: Expected candidate_id to contain '{EXPECTED_CANDIDATE_ID_FRAGMENT}', got '{candidateId}'");
    Environment.Exit(1);
}

if (fullname == candidateId)
{
    Console.WriteLine($"❌ FAIL: fullname should NOT equal candidate_id! Both are '{fullname}'");
    Environment.Exit(1);
}

Console.WriteLine("\n" + "=".PadRight(80, '='));
Console.WriteLine("[PASS] TEST PASSED");
Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine($"Selected Candidate: {fullname} (ID: {candidateId}, Rank: 1)");
Console.WriteLine($"fullname != candidate_id: {fullname} != {candidateId}");
Console.WriteLine("=".PadRight(80, '='));
