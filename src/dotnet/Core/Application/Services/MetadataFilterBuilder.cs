using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Domain.Entities;
using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Application.Services;

public sealed class MetadataFilterBuilder
{
    private readonly string _candidateIdField;
    private readonly string _seniorityField;
    private readonly string _yearsExperienceField;
    private readonly string _skillNameField;
    private readonly string _typeField;
    private readonly string _typeSkill;
    private readonly Dictionary<SeniorityLevel, int> _seniorityOrder;

    public MetadataFilterBuilder(
        string candidateIdField,
        string seniorityField,
        string yearsExperienceField,
        string skillNameField,
        string typeField,
        string typeSkill)
    {
        _candidateIdField = candidateIdField;
        _seniorityField = seniorityField;
        _yearsExperienceField = yearsExperienceField;
        _skillNameField = skillNameField;
        _typeField = typeField;
        _typeSkill = typeSkill;
        _seniorityOrder = new Dictionary<SeniorityLevel, int>
        {
            [SeniorityLevel.Intern] = 0,
            [SeniorityLevel.Junior] = 1,
            [SeniorityLevel.Mid] = 2,
            [SeniorityLevel.Senior] = 3,
            [SeniorityLevel.Lead] = 4,
            [SeniorityLevel.Principal] = 5,
            [SeniorityLevel.Staff] = 6
        };
    }

    public List<Dictionary<string, object>> BuildCandidateFilters(ParsedQuery parsedQuery)
    {
        var filters = new List<Dictionary<string, object>>();

        if (parsedQuery.MinSeniorityLevel.HasValue)
        {
            var seniorityFilters = BuildSeniorityFilter(parsedQuery.MinSeniorityLevel.Value);
            filters.AddRange(seniorityFilters);
        }

        if (parsedQuery.MinYearsExperience.HasValue)
        {
            var yearsFilter = BuildYearsFilter(parsedQuery.MinYearsExperience.Value);
            filters.Add(yearsFilter);
        }

        return filters;
    }

    public Dictionary<string, object>? BuildTechnologyFilters(ParsedQuery parsedQuery)
    {
        if (parsedQuery.RequiredTechnologies.Length == 0)
            return null;

        return new Dictionary<string, object>
        {
            ["$and"] = new object[]
            {
                new Dictionary<string, object> { [_typeField] = _typeSkill },
                new Dictionary<string, object> 
                { 
                    [_skillNameField] = new Dictionary<string, object> 
                    { 
                        ["$in"] = parsedQuery.RequiredTechnologies 
                    } 
                }
            }
        };
    }

    public List<AggregatedCandidate> FilterAggregatedCandidates(
        List<AggregatedCandidate> candidates,
        ParsedQuery parsedQuery)
    {
        var filtered = new List<AggregatedCandidate>();

        foreach (var candidate in candidates)
        {
            if (MatchesFilters(candidate, parsedQuery))
            {
                filtered.Add(candidate);
            }
        }

        return filtered;
    }

    private bool MatchesFilters(AggregatedCandidate candidate, ParsedQuery parsedQuery)
    {
        if (parsedQuery.MinSeniorityLevel.HasValue)
        {
            var candidateSeniorityStr = candidate.Metadata.TryGetValue(_seniorityField, out var seniorityObj)
                ? seniorityObj?.ToString()
                : null;

            if (!MeetsSeniorityRequirement(candidateSeniorityStr, parsedQuery.MinSeniorityLevel.Value))
            {
                return false;
            }
        }

        if (parsedQuery.MinYearsExperience.HasValue)
        {
            var candidateYears = candidate.Metadata.TryGetValue(_yearsExperienceField, out var yearsObj)
                ? Convert.ToInt32(yearsObj)
                : 0;

            if (candidateYears < parsedQuery.MinYearsExperience.Value)
            {
                return false;
            }
        }

        return true;
    }

    private bool MeetsSeniorityRequirement(string? candidateSeniorityStr, SeniorityLevel requiredSeniority)
    {
        if (string.IsNullOrWhiteSpace(candidateSeniorityStr))
            return false;

        var candidateSeniority = ParseSeniority(candidateSeniorityStr);
        if (!candidateSeniority.HasValue)
            return false;

        var requiredLevel = _seniorityOrder.TryGetValue(requiredSeniority, out var reqLevel) ? reqLevel : 0;
        var candidateLevel = _seniorityOrder.TryGetValue(candidateSeniority.Value, out var candLevel) ? candLevel : 0;

        return candidateLevel >= requiredLevel;
    }

    private SeniorityLevel? ParseSeniority(string seniorityStr)
    {
        var seniorityMap = new Dictionary<string, SeniorityLevel>
        {
            ["Intern"] = SeniorityLevel.Intern,
            ["Junior"] = SeniorityLevel.Junior,
            ["Mid"] = SeniorityLevel.Mid,
            ["Senior"] = SeniorityLevel.Senior,
            ["Lead"] = SeniorityLevel.Lead,
            ["Principal"] = SeniorityLevel.Principal,
            ["Staff"] = SeniorityLevel.Staff
        };

        return seniorityMap.TryGetValue(seniorityStr, out var level) ? level : null;
    }

    private List<Dictionary<string, object>> BuildSeniorityFilter(SeniorityLevel minSeniority)
    {
        var minLevel = _seniorityOrder.TryGetValue(minSeniority, out var level) ? level : 0;

        var validSeniorities = new List<string>();
        foreach (var (seniority, seniorityLevel) in _seniorityOrder)
        {
            if (seniorityLevel >= minLevel)
            {
                validSeniorities.Add(SeniorityLevelToString(seniority));
            }
        }

        if (validSeniorities.Count == 0)
            return new List<Dictionary<string, object>>();

        return new List<Dictionary<string, object>>
        {
            new Dictionary<string, object>
            {
                [_seniorityField] = new Dictionary<string, object>
                {
                    ["$in"] = validSeniorities
                }
            }
        };
    }

    private Dictionary<string, object> BuildYearsFilter(int minYears)
    {
        return new Dictionary<string, object>
        {
            [_yearsExperienceField] = new Dictionary<string, object>
            {
                ["$gte"] = minYears
            }
        };
    }

    private static string SeniorityLevelToString(SeniorityLevel level)
    {
        return level switch
        {
            SeniorityLevel.Intern => "Intern",
            SeniorityLevel.Junior => "Junior",
            SeniorityLevel.Mid => "Mid",
            SeniorityLevel.Senior => "Senior",
            SeniorityLevel.Lead => "Lead",
            SeniorityLevel.Principal => "Principal",
            SeniorityLevel.Staff => "Staff",
            _ => "Unknown"
        };
    }
}
