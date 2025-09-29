namespace Rag.Candidates.Core.Application.DTOs;

public class ChatFilters
{
    public bool? Prepared { get; set; }
    public string? EnglishMin { get; set; }
    public string[]? CandidateIds { get; set; }
}