using Rag.Candidates.Core.Domain.Entities;

namespace Rag.Candidates.Core.Application.DTOs;

public sealed class AggregatedCandidate
{
    public required string CandidateId { get; init; }
    public required List<string> Documents { get; init; }
    public required Dictionary<string, object> Metadata { get; init; }
    public required double MaxScore { get; init; }
    public required List<double> AllScores { get; init; }
}
