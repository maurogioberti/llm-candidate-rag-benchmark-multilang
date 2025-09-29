using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Domain.Entities;

public class GeneralInfo
{
    public string? CandidateId { get; set; }
    public string? Fullname { get; set; }
    public string? TitleDetected { get; set; }
    public string? TitlePredicted { get; set; }
    public SeniorityLevel? SeniorityLevel { get; set; }
    public int? YearsExperience { get; set; }
    public int? RelevantYears { get; set; }
    public string? IndustryMatch { get; set; }
    public string? TrajectoryPattern { get; set; }
    public string? MainIndustry { get; set; }
    public string? EnglishLevel { get; set; }
    public string[]? OtherLanguages { get; set; }
    public string? Location { get; set; }
    public string? RemoteWork { get; set; }
    public string? Availability { get; set; }
    public string? SalaryExpectations { get; set; }
    public string? NoticePeriod { get; set; }
}