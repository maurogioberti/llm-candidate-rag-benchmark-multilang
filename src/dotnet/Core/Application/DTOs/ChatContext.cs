namespace Rag.Candidates.Core.Application.DTOs;

public sealed record ChatContext(string SystemPrompt, string UserMessage, string? Context = null);
