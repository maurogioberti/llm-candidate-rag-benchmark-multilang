using System.Text.Json;

namespace Rag.Candidates.Core.Domain.Entities;

public class Candidate
{
    public required CandidateRecord CandidateRecord { get; set; }
    public required string CandidateId { get; set; }
    public required Dictionary<string, object> Raw { get; set; }

    public static Candidate FromCandidateRecord(CandidateRecord candidateRecord, string candidateId, Dictionary<string, object>? rawData = null)
    {
        rawData ??= JsonSerializer.Deserialize<Dictionary<string, object>>(JsonSerializer.Serialize(candidateRecord)) ?? new();
        
        return new Candidate
        {
            CandidateRecord = candidateRecord,
            CandidateId = candidateId,
            Raw = rawData
        };
    }

    public string Summary => CandidateRecord.Summary;
    public GeneralInfo? GeneralInfo => CandidateRecord.GeneralInfo;
    public Skill[] SkillMatrix => CandidateRecord.SkillMatrix ?? Array.Empty<Skill>();
    public Scores? Scores => CandidateRecord.Scores;
    public Language[] Languages => CandidateRecord.Languages ?? Array.Empty<Language>();
    public string[] Strengths => CandidateRecord.Strengths ?? Array.Empty<string>();
    public string[] AreasToImprove => CandidateRecord.AreasToImprove ?? Array.Empty<string>();
    public string[] Tips => CandidateRecord.Tips ?? Array.Empty<string>();
    public string? CleanedResumeText => CandidateRecord.CleanedResumeText;

    public bool Prepared => Scores?.OverallScore >= 60;
}