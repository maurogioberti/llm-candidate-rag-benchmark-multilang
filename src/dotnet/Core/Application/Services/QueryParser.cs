using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Entities;
using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Application.Services;

public sealed class QueryParser
{
    private readonly QueryParsingConfig _config;
    private readonly SeniorityMatcher _seniorityMatcher;
    private readonly TechnologyMatcher _technologyMatcher;
    private readonly ExperienceParser _experienceParser;

    public QueryParser(QueryParsingConfig? config = null)
    {
        _config = config ?? QueryParsingConfig.Default;
        _seniorityMatcher = new SeniorityMatcher(_config);
        _technologyMatcher = new TechnologyMatcher(_config);
        _experienceParser = new ExperienceParser();
    }

    public ParsedQuery Parse(string queryText)
    {
        var queryIntent = ExtractIntent(queryText);
        var requiredTechnologies = _technologyMatcher.ExtractTechnologies(queryText);
        var minSeniorityLevel = _seniorityMatcher.Match(queryText);
        var minYearsExperience = _experienceParser.ExtractYears(queryText);

        return new ParsedQuery
        {
            QueryText = queryText,
            QueryIntent = queryIntent,
            RequiredTechnologies = requiredTechnologies,
            MinSeniorityLevel = minSeniorityLevel,
            MinYearsExperience = minYearsExperience
        };
    }

    private QueryIntent ExtractIntent(string queryText)
    {
        var queryLower = queryText.ToLowerInvariant();

        foreach (var (intentKey, keywords) in _config.IntentKeywords)
        {
            foreach (var keyword in keywords)
            {
                if (queryLower.Contains(keyword.ToLowerInvariant()))
                {
                    return MapIntentKey(intentKey);
                }
            }
        }

        return QueryIntent.General;
    }

    private static QueryIntent MapIntentKey(string intentKey)
    {
        return intentKey switch
        {
            "find_best" => QueryIntent.FindBest,
            "list_all" => QueryIntent.ListAll,
            "compare" => QueryIntent.Compare,
            "explain" => QueryIntent.Explain,
            _ => QueryIntent.General
        };
    }
}
