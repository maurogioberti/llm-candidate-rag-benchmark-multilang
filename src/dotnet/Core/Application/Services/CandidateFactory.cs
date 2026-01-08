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
        var data = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonData, _jsonOptions) ?? new();
        
        if (validate)
        {
            var filteredData = FilterCommentFields(data);
            var filteredJson = JsonSerializer.Serialize(filteredData, _jsonOptions);
            
            var validationResult = _validationService.ValidateAsync(filteredJson);
            if (!validationResult.IsValid)
            {
                throw new ArgumentException($"JSON validation failed: {string.Join(", ", validationResult.Errors)}");
            }
        }

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

    private IReadOnlyList<Language>? ParseOtherLanguages(Dictionary<string, object> data)
    {
        if (!data.TryGetValue("OtherLanguages", out var value) || value is not JsonElement element)
            return null;

        if (element.ValueKind != JsonValueKind.Array)
            return null;

        var languages = new List<Language>();
        foreach (var langElement in element.EnumerateArray())
        {
            if (langElement.ValueKind == JsonValueKind.Object)
            {
                var language = new Language
                {
                    Name = GetStringValueFromElement(langElement, "Language"),
                    Proficiency = ParseLanguageProficiency(GetStringValueFromElement(langElement, "Proficiency")),
                    Evidence = GetStringValueFromElement(langElement, "Evidence")
                };
                languages.Add(language);
            }
        }
        return languages;
    }

    private static string? GetStringValueFromElement(JsonElement element, string propertyName)
    {
        return element.TryGetProperty(propertyName, out var prop) &&
               prop.ValueKind == JsonValueKind.String ? prop.GetString() : null;
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
            OtherLanguages = ParseOtherLanguages(data),
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

    private SeniorityLevel? ParseSeniorityLevel(string? value)
    {
        if (string.IsNullOrEmpty(value))
            return null;
        
        if (Enum.TryParse<SeniorityLevel>(value, true, out var result))
            return result;
        
        var normalized = NormalizeSeniorityLevel(value);
        if (normalized != null && Enum.TryParse<SeniorityLevel>(normalized, true, out result))
            return result;
        
        return null;
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
                        Name = GetStringValue(skillData, "SkillName"),
                        Category = GetStringValue(skillData, "SkillCategory"),
                        Level = GetStringValue(skillData, "SkillLevel"),
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

    private LanguageProficiency? ParseLanguageProficiency(string? value)
    {
        if (string.IsNullOrEmpty(value))
            return null;
        
        if (Enum.TryParse<LanguageProficiency>(value, true, out var result))
            return result;
        
        var normalized = NormalizeProficiency(value);
        if (normalized != null && Enum.TryParse<LanguageProficiency>(normalized, true, out result))
            return result;
        
        return null;
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

    private OverallFitLevel? ParseOverallFitLevel(string? value)
    {
        if (string.IsNullOrEmpty(value))
            return null;
        
        if (Enum.TryParse<OverallFitLevel>(value, true, out var result))
            return result;
        
        var enumValues = Enum.GetValues<OverallFitLevel>();
        foreach (var enumValue in enumValues)
        {
            if (string.Equals(value, enumValue.ToString(), StringComparison.OrdinalIgnoreCase))
                return enumValue;
        }
        
        return null;
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

    private Dictionary<string, object> FilterCommentFields(Dictionary<string, object> data)
    {
        var filteredData = new Dictionary<string, object>(data);
        
        if (filteredData.TryGetValue("Scores", out var scoresValue))
        {
            Dictionary<string, object>? scoresData = null;
            
            if (scoresValue is JsonElement scoresElement)
            {
                scoresData = JsonSerializer.Deserialize<Dictionary<string, object>>(scoresElement.GetRawText());
            }
            else if (scoresValue is Dictionary<string, object> scoresDict)
            {
                scoresData = new Dictionary<string, object>(scoresDict);
            }
            
            if (scoresData != null)
            {
                var commentFields = scoresData.Keys.Where(key => key.EndsWith("Comment")).ToList();
                foreach (var field in commentFields)
                {
                    scoresData.Remove(field);
                }
                filteredData["Scores"] = scoresData;
            }
        }
        
        if (filteredData.TryGetValue("Languages", out var languagesValue))
        {
            if (languagesValue is JsonElement languagesElement && languagesElement.ValueKind == JsonValueKind.Array)
            {
                var languagesList = new List<object>();
                foreach (var langElement in languagesElement.EnumerateArray())
                {
                    if (langElement.ValueKind == JsonValueKind.Object)
                    {
                        var langData = JsonSerializer.Deserialize<Dictionary<string, object>>(langElement.GetRawText());
                        if (langData != null)
                        {
                            NormalizeProficiencyInLanguage(langData);
                            languagesList.Add(langData);
                        }
                    }
                }
                filteredData["Languages"] = languagesList.ToArray();
            }
        }
        
        if (filteredData.TryGetValue("GeneralInfo", out var generalInfoValue))
        {
            Dictionary<string, object>? generalInfoData = null;
            
            if (generalInfoValue is JsonElement generalInfoElement)
            {
                generalInfoData = JsonSerializer.Deserialize<Dictionary<string, object>>(generalInfoElement.GetRawText());
            }
            else if (generalInfoValue is Dictionary<string, object> generalInfoDict)
            {
                generalInfoData = new Dictionary<string, object>(generalInfoDict);
            }
            
            if (generalInfoData != null)
            {
                if (generalInfoData.TryGetValue("SeniorityLevel", out var seniorityValue) && seniorityValue is string seniorityStr)
                {
                    var normalizedSeniority = NormalizeSeniorityLevel(seniorityStr);
                    if (normalizedSeniority != null)
                    {
                        generalInfoData["SeniorityLevel"] = normalizedSeniority;
                    }
                }
                
                if (generalInfoData.TryGetValue("OtherLanguages", out var otherLanguagesValue))
                {
                    if (otherLanguagesValue is JsonElement otherLanguagesElement && otherLanguagesElement.ValueKind == JsonValueKind.Array)
                    {
                        var otherLanguagesList = new List<object>();
                        foreach (var langElement in otherLanguagesElement.EnumerateArray())
                        {
                            if (langElement.ValueKind == JsonValueKind.Object)
                            {
                                var langData = JsonSerializer.Deserialize<Dictionary<string, object>>(langElement.GetRawText());
                                if (langData != null)
                                {
                                    NormalizeProficiencyInLanguage(langData);
                                    otherLanguagesList.Add(langData);
                                }
                            }
                        }
                        generalInfoData["OtherLanguages"] = otherLanguagesList.ToArray();
                    }
                }
                
                filteredData["GeneralInfo"] = generalInfoData;
            }
        }
        
        return filteredData;
    }
    
    private void NormalizeProficiencyInLanguage(Dictionary<string, object> langData)
    {
        if (langData.TryGetValue("Proficiency", out var proficiencyValue))
        {
            string? proficiencyStr = null;
            if (proficiencyValue is string str)
            {
                proficiencyStr = str;
            }
            else if (proficiencyValue is JsonElement element && element.ValueKind == JsonValueKind.String)
            {
                proficiencyStr = element.GetString();
            }
            
            if (proficiencyStr != null)
            {
                var normalized = NormalizeProficiency(proficiencyStr);
                if (normalized != null)
                {
                    langData["Proficiency"] = normalized;
                }
            }
        }
    }
    
    private string? NormalizeProficiency(string value)
    {
        if (string.IsNullOrEmpty(value))
            return null;
        
        value = value.Trim();
        
        foreach (var validValue in _proficiencyValues)
        {
            if (string.Equals(value, validValue, StringComparison.OrdinalIgnoreCase))
            {
                return validValue;
            }
        }
        
        var patterns = new[]
        {
            @"\(([A-Z]\d)\)",
            @"\b([A-Z]\d)\b",
            @"\b(Basic|Conversational|Fluent|Native|Advanced)\b"
        };
        
        foreach (var pattern in patterns)
        {
            var match = System.Text.RegularExpressions.Regex.Match(value, pattern, System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            if (match.Success && match.Groups.Count > 1)
            {
                var extracted = match.Groups[1].Value;
                foreach (var validValue in _proficiencyValues)
                {
                    if (string.Equals(extracted, validValue, StringComparison.OrdinalIgnoreCase))
                    {
                        return extracted;
                    }
                }
            }
        }
        
        return null;
    }
    
    private string? NormalizeSeniorityLevel(string value)
    {
        if (string.IsNullOrEmpty(value))
            return null;
        
        value = value.Trim();
        
        foreach (var validValue in _seniorityValues)
        {
            if (string.Equals(value, validValue, StringComparison.OrdinalIgnoreCase))
            {
                return validValue;
            }
        }
        
        var pattern = @"\b(Junior|Mid|Senior|Lead|Principal|Staff)\b";
        var match = System.Text.RegularExpressions.Regex.Match(value, pattern, System.Text.RegularExpressions.RegexOptions.IgnoreCase);
        if (match.Success && match.Groups.Count > 1)
        {
            var extracted = match.Groups[1].Value;
            foreach (var validValue in _seniorityValues)
            {
                if (string.Equals(extracted, validValue, StringComparison.OrdinalIgnoreCase))
                {
                    return validValue;
                }
            }
        }
        
        return null;
    }
}