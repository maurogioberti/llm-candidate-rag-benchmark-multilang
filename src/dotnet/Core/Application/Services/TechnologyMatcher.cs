using Rag.Candidates.Core.Domain.Configuration;
using System.Text.RegularExpressions;

namespace Rag.Candidates.Core.Application.Services;

public sealed class TechnologyMatcher
{
    private readonly QueryParsingConfig _config;

    public TechnologyMatcher(QueryParsingConfig config)
    {
        _config = config;
    }

    public string[] ExtractTechnologies(string queryText)
    {
        var technologies = new HashSet<string>();
        var queryLower = queryText.ToLowerInvariant();

        foreach (var (token, normalized) in _config.TechnologySynonyms)
        {
            var pattern = $@"\b{Regex.Escape(token.ToLowerInvariant())}\b";
            if (Regex.IsMatch(queryLower, pattern))
            {
                technologies.Add(normalized);
            }
        }

        return technologies.OrderBy(t => t).ToArray();
    }
}
