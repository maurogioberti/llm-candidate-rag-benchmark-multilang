namespace Rag.Candidates.Core.Application.DTOs;

public class ChatResult
{
    public required string Answer { get; set; }
    public required ChatSource[] Sources { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}