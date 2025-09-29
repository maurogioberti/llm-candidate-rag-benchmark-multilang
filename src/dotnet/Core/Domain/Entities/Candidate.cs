using System.Text.Json;

namespace Rag.Candidates.Core.Domain.Entities;

public class Candidate
{
    private const string Separator = ", ";
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

    public string[] ToTextBlocks()
    {
        var blocks = new List<string>();
        
        var titleHint = GetTitleHint();
        var candidateSummary = $"[Candidate] {CandidateId} {titleHint}\nSummary:\n{CandidateRecord.Summary}";
        blocks.Add(candidateSummary);
        
        if (CandidateRecord.SkillMatrix?.Length > 0)
        {
            var skillsSummary = string.Join(", ", CandidateRecord.SkillMatrix
                .Where(s => !string.IsNullOrEmpty(s.Name))
                .Select(s => s.Name!));
            blocks.Add($"Skills: {skillsSummary}");
        }
        
        var derivedKeywords = GetDerivedKeywords();
        if (derivedKeywords.Length > 0)
        {
            blocks.Add($"DerivedKeywords: {string.Join(", ", derivedKeywords.OrderBy(k => k))}");
        }
        
        blocks.Add(System.Text.Json.JsonSerializer.Serialize(Raw, new System.Text.Json.JsonSerializerOptions { WriteIndented = false }));
        
        return blocks.ToArray();
    }

    private string GetTitleHint()
    {
        if (GeneralInfo?.TitleDetected != null)
            return GeneralInfo.TitleDetected;
        if (GeneralInfo?.TitlePredicted != null)
            return GeneralInfo.TitlePredicted;
        return string.Empty;
    }

    private string[] GetDerivedKeywords()
    {
        var keywords = new HashSet<string>();
        
        if (GeneralInfo?.TitleDetected != null)
            keywords.Add(GeneralInfo.TitleDetected);
        if (GeneralInfo?.TitlePredicted != null)
            keywords.Add(GeneralInfo.TitlePredicted);
        if (GeneralInfo?.MainIndustry != null)
            keywords.Add(GeneralInfo.MainIndustry);
        
        if (SkillMatrix.Length > 0)
        {
            foreach (var skill in SkillMatrix)
            {
                if (!string.IsNullOrEmpty(skill.Name))
                    keywords.Add(skill.Name);
                if (!string.IsNullOrEmpty(skill.Category))
                    keywords.Add(skill.Category);
            }
        }
        
        return keywords.ToArray();
    }
}