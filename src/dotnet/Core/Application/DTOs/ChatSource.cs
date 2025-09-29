namespace Rag.Candidates.Core.Application.DTOs;

public class ChatSource
{
    public required string CandidateId { get; set; }
    public required string Section { get; set; }
    public required string Content { get; set; }
    public required float Score { get; set; }
}