using System.Text.Json;
using Rag.Candidates.Core.Application.UseCases;
using Rag.Candidates.Core.Application.Services;
using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Infrastructure.Embeddings;
using Rag.Candidates.Core.Infrastructure.VectorStores.Native;
using Rag.Candidates.Core.Infrastructure.Llm.ChatClients;
using Rag.Candidates.Core.Infrastructure.Shared;

const string TEST_QUERY_JAVA = "who is the best candidate for java?";
const string EXPECTED_JAVA_CANDIDATE_FULLNAME = "Jan-Claudiu Crisan";
const string EXPECTED_CANDIDATE_ID_FRAGMENT = "JanClaudiuCrisan";

Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine(".NET INTEGRATION TEST: Java Candidate Returns Human Fullname");
Console.WriteLine("=".PadRight(80, '='));

var config = ConfigLoader.LoadConfig();
var embeddingsClient = new HttpEmbeddingsClient(config);
var vectorStore = new InMemoryVectorStore();
var llmClient = new OllamaLlmClient(config);
var candidateService = new CandidateService();

Console.WriteLine("\nBuilding index from data/input/...");
var buildIndexUseCase = new BuildIndexUseCase(embeddingsClient, vectorStore);
var dataDir = Path.Combine(Directory.GetCurrentDirectory(), "data", "input");
var candidates = candidateService.LoadCandidatesFromDirectory(dataDir);
var indexInfo = await buildIndexUseCase.ExecuteAsync(candidates);
Console.WriteLine($"Indexed {indexInfo.TotalChunks} chunks");

Console.WriteLine($"\nExecuting query: '{TEST_QUERY_JAVA}'");
var askQuestionUseCase = new AskQuestionUseCase(embeddingsClient, vectorStore, llmClient);
var request = new ChatRequestDto { Question = TEST_QUERY_JAVA };
var result = await askQuestionUseCase.ExecuteAsync(request);

Console.WriteLine("\n" + "-".PadRight(80, '-'));
Console.WriteLine("ASSERTIONS:");
Console.WriteLine("-".PadRight(80, '-'));

if (result.Metadata == null || result.Metadata.SelectedCandidate == null)
{
    Console.WriteLine("❌ FAIL: No selected candidate in metadata");
    Environment.Exit(1);
}

var selectedCandidate = result.Metadata.SelectedCandidate;
var fullname = selectedCandidate.Fullname;
var candidateId = selectedCandidate.CandidateId;

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
