using Rag.Candidates.Core.Domain.Entities;

namespace Rag.Candidates.Core.Application.Interfaces;

public interface ICandidateFactory
{
    CandidateRecord FromJson(string jsonData, bool validate = true);
    CandidateRecord FromJsonFile(string filePath, bool validate = true);
    Candidate CreateCandidate(CandidateRecord candidateRecord, string candidateId, Dictionary<string, object>? rawData = null);
    Candidate FromJsonToCandidate(string jsonData, string candidateId);
    Candidate FromJsonFileToCandidate(string filePath, string candidateId);
    string ToJson(CandidateRecord candidateRecord);
    void ToJsonFile(CandidateRecord candidateRecord, string filePath);
}