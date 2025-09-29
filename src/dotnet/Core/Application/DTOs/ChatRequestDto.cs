namespace Rag.Candidates.Core.Application.DTOs;

public class ChatRequestDto
{
    public required string Question { get; set; }
    public ChatFilters? Filters { get; set; }
}