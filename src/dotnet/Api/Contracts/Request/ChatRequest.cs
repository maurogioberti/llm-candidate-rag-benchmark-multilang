namespace Rag.Candidates.Api.Contracts.Request;

internal sealed record ChatRequest(string Question, ChatFilters? Filters);
internal sealed record ChatFilters(bool? Prepared, string? EnglishMin, string[]? CandidateIds);