using Rag.Candidates.Core.Application.DTOs;

namespace Rag.Candidates.Core.Application.Services;

public sealed class CandidateAggregator
{
    private readonly string _candidateIdField;

    public CandidateAggregator(string candidateIdField)
    {
        _candidateIdField = candidateIdField;
    }

    public List<AggregatedCandidate> Aggregate(List<(string Document, Dictionary<string, object> Metadata, double Score)> searchResults)
    {
        var candidateMap = new Dictionary<string, CandidateData>();

        foreach (var (document, metadata, score) in searchResults)
        {
            var candidateId = metadata.TryGetValue(_candidateIdField, out var id) 
                ? id.ToString() ?? "unknown" 
                : "unknown";

            if (!candidateMap.ContainsKey(candidateId))
            {
                candidateMap[candidateId] = new CandidateData
                {
                    CandidateId = candidateId,
                    Documents = new List<string>(),
                    Metadata = new Dictionary<string, object>(metadata),
                    Scores = new List<double>()
                };
            }

            candidateMap[candidateId].Documents.Add(document);
            candidateMap[candidateId].Scores.Add(score);
        }

        var aggregated = new List<AggregatedCandidate>();
        foreach (var candidateData in candidateMap.Values)
        {
            aggregated.Add(new AggregatedCandidate
            {
                CandidateId = candidateData.CandidateId,
                Documents = candidateData.Documents,
                Metadata = candidateData.Metadata,
                MaxScore = candidateData.Scores.Count > 0 ? candidateData.Scores.Max() : 0.0,
                AllScores = candidateData.Scores
            });
        }

        return aggregated;
    }

    private class CandidateData
    {
        public required string CandidateId { get; init; }
        public required List<string> Documents { get; init; }
        public required Dictionary<string, object> Metadata { get; init; }
        public required List<double> Scores { get; init; }
    }
}
