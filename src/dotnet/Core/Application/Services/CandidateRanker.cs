using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Entities;
using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Application.Services;

public sealed class CandidateRanker
{
    private static readonly Dictionary<SeniorityLevel, int> SeniorityOrdinals = new()
    {
        { SeniorityLevel.Intern, 0 },
        { SeniorityLevel.Junior, 1 },
        { SeniorityLevel.Mid, 2 },
        { SeniorityLevel.Senior, 3 },
        { SeniorityLevel.Lead, 4 },
        { SeniorityLevel.Principal, 5 },
        { SeniorityLevel.Staff, 6 }
    };
    
    private static readonly string[] LeadershipKeywords = 
        { "lead", "principal", "staff", "manager", "director", "head", "architect" };
    
    private static readonly HashSet<QueryIntent> LeadershipRelevantIntents = new()
    {
        QueryIntent.FindBest
    };
    
    private const double MaxNormalizedScore = 1.0;
    private const double MinNormalizedScore = 0.0;
    
    private readonly RankingWeights _weights;
    
    public CandidateRanker(RankingWeights weights)
    {
        _weights = weights;
    }
    
    public List<RankedCandidate> Rank(
        List<AggregatedCandidate> candidates, 
        ParsedQuery parsedQuery)
    {
        var ranked = new List<RankedCandidate>();
        
        foreach (var candidate in candidates)
        {
            var technicalScore = CalculateTechnicalScore(
                candidate, 
                parsedQuery.RequiredTechnologies.ToList()
            );
            var seniorityScore = CalculateSeniorityScore(
                candidate, 
                parsedQuery.MinSeniorityLevel
            );
            var leadershipScore = IsLeadershipRelevant(parsedQuery)
                ? CalculateLeadershipScore(candidate)
                : MinNormalizedScore;
            var experienceScore = CalculateExperienceScore(
                candidate, 
                parsedQuery.MinYearsExperience
            );
            
            var totalScore = 
                technicalScore * _weights.TechnicalMatchWeight +
                seniorityScore * _weights.SeniorityMatchWeight +
                leadershipScore * _weights.LeadershipSignalsWeight +
                experienceScore * _weights.ExperienceMatchWeight;
            
            ranked.Add(new RankedCandidate
            {
                CandidateId = candidate.CandidateId,
                Documents = candidate.Documents,
                Metadata = candidate.Metadata,
                MaxScore = candidate.MaxScore,
                AllScores = candidate.AllScores,
                TechnicalScore = technicalScore,
                SeniorityScore = seniorityScore,
                LeadershipScore = leadershipScore,
                ExperienceScore = experienceScore,
                TotalScore = totalScore
            });
        }
        
        return ranked.OrderByDescending(c => c.TotalScore).ToList();
    }
    
    private double CalculateTechnicalScore(
        AggregatedCandidate candidate, 
        List<string> requiredTechnologies)
    {
        if (requiredTechnologies.Count == 0)
        {
            return MaxNormalizedScore;
        }
        
        if (!candidate.Metadata.TryGetValue("primary_skills", out var primarySkillsObj) ||
            primarySkillsObj is not List<object> primarySkillsList)
        {
            return MinNormalizedScore;
        }
        
        var primarySkills = primarySkillsList
            .Select(s => s.ToString()?.ToLowerInvariant() ?? string.Empty)
            .ToList();
        
        if (primarySkills.Count == 0)
        {
            return MinNormalizedScore;
        }
        
        var matchedCount = requiredTechnologies
            .Count(tech => primarySkills.Any(skill => 
                skill.Contains(tech.ToLowerInvariant(), StringComparison.Ordinal)));
        
        return Math.Min((double)matchedCount / requiredTechnologies.Count, MaxNormalizedScore);
    }
    
    private double CalculateSeniorityScore(
        AggregatedCandidate candidate, 
        SeniorityLevel? minSeniority)
    {
        if (minSeniority is null)
        {
            return MaxNormalizedScore;
        }
        
        if (!candidate.Metadata.TryGetValue("seniority_level", out var seniorityObj) ||
            seniorityObj is not string seniorityStr)
        {
            return MinNormalizedScore;
        }
        
        if (!Enum.TryParse<SeniorityLevel>(seniorityStr, out var candidateSeniority))
        {
            return MinNormalizedScore;
        }
        
        var minOrdinal = SeniorityOrdinals.GetValueOrDefault(minSeniority.Value, 0);
        var candidateOrdinal = SeniorityOrdinals.GetValueOrDefault(candidateSeniority, 0);
        
        if (candidateOrdinal < minOrdinal)
        {
            return MinNormalizedScore;
        }
        
        var excessOrdinal = candidateOrdinal - minOrdinal;
        var cappedExcess = Math.Min(excessOrdinal, _weights.MaxSeniorityDelta);
        
        if (_weights.MaxSeniorityDelta == 0)
        {
            return excessOrdinal == 0 ? MaxNormalizedScore : MinNormalizedScore;
        }
        
        return (double)cappedExcess / _weights.MaxSeniorityDelta;
    }
    
    private double CalculateLeadershipScore(AggregatedCandidate candidate)
    {
        var combinedText = string.Join(" ", candidate.Documents).ToLowerInvariant();
        
        var matches = LeadershipKeywords.Count(keyword => 
            combinedText.Contains(keyword, StringComparison.Ordinal));
        
        if (matches == 0)
        {
            return MinNormalizedScore;
        }
        
        if (matches < _weights.LeadershipKeywordThreshold)
        {
            return MinNormalizedScore;
        }
        
        return Math.Min(_weights.MaxLeadershipContribution, MaxNormalizedScore);
    }
    
    private bool IsLeadershipRelevant(ParsedQuery parsedQuery)
    {
        if (LeadershipRelevantIntents.Contains(parsedQuery.QueryIntent))
        {
            return true;
        }
        
        var queryLower = parsedQuery.QueryText.ToLowerInvariant();
        return LeadershipKeywords.Any(keyword => queryLower.Contains(keyword, StringComparison.Ordinal));
    }
    
    private double CalculateExperienceScore(
        AggregatedCandidate candidate, 
        int? minYears)
    {
        if (minYears is null)
        {
            return MaxNormalizedScore;
        }
        
        if (!candidate.Metadata.TryGetValue("years_experience", out var yearsObj))
        {
            return MinNormalizedScore;
        }
        
        var candidateYears = yearsObj switch
        {
            int intValue => intValue,
            string strValue when int.TryParse(strValue, out var parsed) => parsed,
            _ => (int?)null
        };
        
        if (candidateYears is null)
        {
            return MinNormalizedScore;
        }
        
        if (candidateYears.Value < minYears.Value)
        {
            return MinNormalizedScore;
        }
        
        var excessYears = candidateYears.Value - minYears.Value;
        const int maxExcessYears = 10;
        
        return Math.Min((double)excessYears / maxExcessYears, MaxNormalizedScore);
    }
}
