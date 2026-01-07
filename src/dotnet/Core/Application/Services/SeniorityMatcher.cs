using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Application.Services;

public sealed class SeniorityMatcher
{
    private readonly QueryParsingConfig _config;
    private readonly Dictionary<string, SeniorityLevel> _tokenMap;

    public SeniorityMatcher(QueryParsingConfig config)
    {
        _config = config;
        _tokenMap = BuildTokenMap();
    }

    private Dictionary<string, SeniorityLevel> BuildTokenMap()
    {
        var mapping = new Dictionary<string, SeniorityLevel>();
        
        foreach (var (level, tokens) in _config.SeniorityTokens)
        {
            foreach (var token in tokens)
            {
                mapping[token.ToLowerInvariant()] = level;
            }
        }
        
        return mapping;
    }

    public SeniorityLevel? Match(string queryText)
    {
        var queryLower = queryText.ToLowerInvariant();
        
        foreach (var (token, level) in _tokenMap)
        {
            if (queryLower.Contains(token))
            {
                return level;
            }
        }
        
        return null;
    }
}
