using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Entities;
using Rag.Candidates.Core.Domain.Enums;
using System.Text.Json;

namespace Rag.Candidates.Core.Application.Services;

public sealed class CandidateFactory : ICandidateFactory
{
    private readonly ISchemaValidationService _validationService;
    private readonly JsonSerializerOptions _jsonOptions;

    private const string DefaultSchemaVersion = "1.0";
    private const string DefaultSummary = "";
    private const string JsonDataDoesNotMatchSchema = "JSON data doesn't match schema: {0}";
    private const string JsonFileNotFound = "JSON file not found: {0}";
    private const string CandidateRecordDoesNotMatchSchema = "CandidateRecord instance doesn't match schema";

    private readonly string[] _proficiencyValues = ["A1", "A2", "B1", "B2", "C1", "C2", "Basic", "Conversational", "Fluent", "Native", "Advanced"];
    private readonly string[] _seniorityValues = ["Junior", "Mid", "Senior", "Lead", "Principal", "Staff"];

    public CandidateFactory(ISchemaValidationService validationService)
    {
        _validationService = validationService;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            WriteIndented = true
        };
    }

    public CandidateRecord FromJson(string jsonData, bool validate = true)
    {
        if (validate)
        {
            var validationResult = _validationService.ValidateAsync(jsonData);
            if (!validationResult.IsValid)
            {
                throw new ArgumentException($"JSON validation failed: {string.Join(", ", validationResult.Errors)}");
            }
        }

        var data = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonData, _jsonOptions) ?? new();
        return CreateCandidateRecord(data);
    }

    public CandidateRecord FromJsonFile(string filePath, bool validate = true)
    {
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException(string.Format(JsonFileNotFound, filePath));
        }

        var jsonData = File.ReadAllText(filePath);
        return FromJson(jsonData, validate);
    }

    public Candidate CreateCandidate(CandidateRecord candidateRecord, string candidateId, Dictionary<string, object>? rawData = null)
    {
        return Candidate.FromCandidateRecord(candidateRecord, candidateId, rawData);
    }

    public Candidate FromJsonToCandidate(string jsonData, string candidateId)
    {
        var candidateRecord = FromJson(jsonData);
        var rawData = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonData);
        return CreateCandidate(candidateRecord, candidateId, rawData);
    }

    public Candidate FromJsonFileToCandidate(string filePath, string candidateId)
    {
        var candidateRecord = FromJsonFile(filePath);
        var rawData = JsonSerializer.Deserialize<Dictionary<string, object>>(File.ReadAllText(filePath));
        return CreateCandidate(candidateRecord, candidateId, rawData);
    }

    public string ToJson(CandidateRecord candidateRecord)
    {
        return JsonSerializer.Serialize(candidateRecord, new JsonSerializerOptions { WriteIndented = true });
    }

    public void ToJsonFile(CandidateRecord candidateRecord, string filePath)
    {
        var data = ToJson(candidateRecord);
        var directory = Path.GetDirectoryName(filePath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }
        File.WriteAllText(filePath, data);
    }

    private CandidateRecord CreateCandidateRecord(Dictionary<string, object> data)
    {
        return new CandidateRecord
        {
            Summary = GetStringValue(data, "Summary") ?? DefaultSummary,
            SchemaVersion = GetStringValue(data, "schemaVersion") ?? DefaultSchemaVersion,
            GeneratedAt = ParseDateTime(GetStringValue(data, "generatedAt")),
            Source = GetStringValue(data, "source"),
            GeneralInfo = ParseGeneralInfo(GetObjectValue(data, "GeneralInfo")),
            SkillMatrix = ParseSkillMatrix(GetArrayValue(data, "SkillMatrix")),
            KeywordCoverage = ParseKeywordCoverage(GetObjectValue(data, "KeywordCoverage")),
            Languages = ParseLanguages(GetArrayValue(data, "Languages")),
            Scores = ParseScores(GetObjectValue(data, "Scores")),
            Relevance = ParseRelevance(GetObjectValue(data, "Relevance")),
            ClarityAndFormatting = ParseClarityAndFormatting(GetObjectValue(data, "ClarityAndFormatting")),
            Strengths = GetStringArrayValue(data, "Strengths"),
            AreasToImprove = GetStringArrayValue(data, "AreasToImprove"),
            Tips = GetStringArrayValue(data, "Tips"),
            CleanedResumeText = GetStringValue(data, "CleanedResumeText")
        };
    }

    private static string? GetStringValue(Dictionary<string, object> data, string key)
    {
        return data.TryGetValue(key, out var value) ? value?.ToString() : null;
    }

    private static Dictionary<string, object>? GetObjectValue(Dictionary<string, object> data, string key)
    {
        return data.TryGetValue(key, out var value) && value is JsonElement element
            ? JsonSerializer.Deserialize<Dictionary<string, object>>(element.GetRawText())
            : null;
    }

    private static object[]? GetArrayValue(Dictionary<string, object> data, string key)
    {
        return data.TryGetValue(key, out var value) && value is JsonElement element
            ? JsonSerializer.Deserialize<object[]>(element.GetRawText())
            : null;
    }

    private static string[]? GetStringArrayValue(Dictionary<string, object> data, string key)
    {
        return data.TryGetValue(key, out var value) && value is JsonElement element
            ? JsonSerializer.Deserialize<string[]>(element.GetRawText())
            : null;
    }

    private static DateTime? ParseDateTime(string? value)
    {
        if (string.IsNullOrEmpty(value))
            return null;

        try
        {
            if (value.EndsWith('Z'))
                value = value[..^1] + "+00:00";
            return DateTime.Parse(value);
        }
        catch
        {
            return null;
        }
    }

    private GeneralInfo? ParseGeneralInfo(Dictionary<string, object>? data)
    {
        if (data == null) return null;

        return new GeneralInfo
        {
            CandidateId = GetStringValue(data, "CandidateId"),
            Fullname = GetStringValue(data, "Fullname"),
            TitleDetected = GetStringValue(data, "TitleDetected"),
            TitlePredicted = GetStringValue(data, "TitlePredicted"),
            SeniorityLevel = ParseSeniorityLevel(GetStringValue(data, "SeniorityLevel")),
            YearsExperience = GetIntValue(data, "YearsExperience"),
            RelevantYears = GetIntValue(data, "RelevantYears"),
            IndustryMatch = GetStringValue(data, "IndustryMatch"),
            TrajectoryPattern = GetStringValue(data, "TrajectoryPattern"),
            MainIndustry = GetStringValue(data, "MainIndustry"),
            EnglishLevel = GetStringValue(data, "EnglishLevel"),
            OtherLanguages = GetStringArrayValue(data, "OtherLanguages"),
            Location = GetStringValue(data, "Location"),
            RemoteWork = GetStringValue(data, "RemoteWork"),
            Availability = GetStringValue(data, "Availability"),
            SalaryExpectations = GetStringValue(data, "SalaryExpectations"),
            NoticePeriod = GetStringValue(data, "NoticePeriod")
        };
    }

    private static int? GetIntValue(Dictionary<string, object> data, string key)
    {
        if (!data.TryGetValue(key, out var value)) return null;
        return value switch
        {
            int i => i,
            JsonElement element when element.ValueKind == JsonValueKind.Number => element.GetInt32(),
            string str when int.TryParse(str, out var parsed) => parsed,
            _ => null
        };
    }

    private static SeniorityLevel? ParseSeniorityLevel(string? value)
    {
        if (string.IsNullOrEmpty(value)) return null;
        return Enum.TryParse<SeniorityLevel>(value, true, out var result) ? result : null;
    }

    private Skill[]? ParseSkillMatrix(object[]? data)
    {
        if (data == null) return null;

        var skills = new List<Skill>();
        foreach (var item in data)
        {
            if (item is JsonElement element)
            {
                var skillData = JsonSerializer.Deserialize<Dictionary<string, object>>(element.GetRawText());
                if (skillData != null)
                {
                    skills.Add(new Skill
                    {
                        Name = GetStringValue(skillData, "Name"),
                        Category = GetStringValue(skillData, "Category"),
                        Level = GetStringValue(skillData, "Level"),
                        YearsExperience = GetIntValue(skillData, "YearsExperience"),
                        Evidence = GetStringValue(skillData, "Evidence"),
                        IsRelevant = GetBoolValue(skillData, "IsRelevant")
                    });
                }
            }
        }
        return skills.ToArray();
    }

    private static bool? GetBoolValue(Dictionary<string, object> data, string key)
    {
        if (!data.TryGetValue(key, out var value)) return null;
        return value switch
        {
            bool b => b,
            JsonElement element when element.ValueKind == JsonValueKind.True => true,
            JsonElement element when element.ValueKind == JsonValueKind.False => false,
            string str when bool.TryParse(str, out var parsed) => parsed,
            _ => null
        };
    }

    private KeywordCoverage? ParseKeywordCoverage(Dictionary<string, object>? data)
    {
        if (data == null) return null;

        return new KeywordCoverage
        {
            RequiredKeywords = GetStringArrayValue(data, "RequiredKeywords"),
            FoundKeywords = GetStringArrayValue(data, "FoundKeywords"),
            MissingKeywords = GetStringArrayValue(data, "MissingKeywords"),
            CoveragePercentage = GetDoubleValue(data, "CoveragePercentage"),
            AlternativeKeywords = GetStringArrayValue(data, "AlternativeKeywords")
        };
    }

    private static double? GetDoubleValue(Dictionary<string, object> data, string key)
    {
        if (!data.TryGetValue(key, out var value)) return null;
        return value switch
        {
            double d => d,
            JsonElement element when element.ValueKind == JsonValueKind.Number => element.GetDouble(),
            string str when double.TryParse(str, out var parsed) => parsed,
            _ => null
        };
    }

    private Language[]? ParseLanguages(object[]? data)
    {
        if (data == null) return null;

        var languages = new List<Language>();
        foreach (var item in data)
        {
            if (item is JsonElement element)
            {
                var langData = JsonSerializer.Deserialize<Dictionary<string, object>>(element.GetRawText());
                if (langData != null)
                {
                    languages.Add(new Language
                    {
                        Name = GetStringValue(langData, "Name"),
                        Proficiency = ParseLanguageProficiency(GetStringValue(langData, "Proficiency")),
                        Evidence = GetStringValue(langData, "Evidence")
                    });
                }
            }
        }
        return languages.ToArray();
    }

    private static LanguageProficiency? ParseLanguageProficiency(string? value)
    {
        if (string.IsNullOrEmpty(value)) return null;
        return Enum.TryParse<LanguageProficiency>(value, true, out var result) ? result : null;
    }

    private Scores? ParseScores(Dictionary<string, object>? data)
    {
        if (data == null) return null;

        return new Scores
        {
            OverallScore = GetDoubleValue(data, "OverallScore"),
            TechnicalScore = GetDoubleValue(data, "TechnicalScore"),
            ExperienceScore = GetDoubleValue(data, "ExperienceScore"),
            LanguageScore = GetDoubleValue(data, "LanguageScore"),
            CulturalFitScore = GetDoubleValue(data, "CulturalFitScore"),
            OverallFitLevel = ParseOverallFitLevel(GetStringValue(data, "OverallFitLevel"))
        };
    }

    private static OverallFitLevel? ParseOverallFitLevel(string? value)
    {
        if (string.IsNullOrEmpty(value)) return null;
        return Enum.TryParse<OverallFitLevel>(value, true, out var result) ? result : null;
    }

    private Relevance? ParseRelevance(Dictionary<string, object>? data)
    {
        if (data == null) return null;

        return new Relevance
        {
            JobTitleMatch = GetStringValue(data, "JobTitleMatch"),
            IndustryMatch = GetStringValue(data, "IndustryMatch"),
            TechnologyMatch = GetStringValue(data, "TechnologyMatch"),
            ExperienceMatch = GetStringValue(data, "ExperienceMatch"),
            LocationMatch = GetStringValue(data, "LocationMatch"),
            RemoteWorkMatch = GetStringValue(data, "RemoteWorkMatch"),
            OverallRelevanceScore = GetDoubleValue(data, "OverallRelevanceScore")
        };
    }

    private ClarityAndFormatting? ParseClarityAndFormatting(Dictionary<string, object>? data)
    {
        if (data == null)
            return null;

        return new ClarityAndFormatting
        {
            FormattingQuality = GetStringValue(data, "FormattingQuality"),
            ClarityScore = GetStringValue(data, "ClarityScore"),
            FormattingIssues = GetStringArrayValue(data, "FormattingIssues"),
            ClarityIssues = GetStringArrayValue(data, "ClarityIssues"),
            Suggestions = GetStringArrayValue(data, "Suggestions")
        };
    }
}