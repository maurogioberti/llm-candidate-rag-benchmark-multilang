using Rag.Candidates.Core.Application.DTOs;

namespace Rag.Candidates.Api.Contracts.Response;

internal sealed record ChatResponse(string Answer, ChatSource[] Sources, object? Metadata = null);