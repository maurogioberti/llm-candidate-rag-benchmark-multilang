using System.Text.RegularExpressions;

namespace Rag.Candidates.Core.Application.Services;

public sealed class ExperienceParser
{
    private readonly List<Regex> _patterns;

    public ExperienceParser()
    {
        _patterns = new List<Regex>
        {
            new Regex(@"(\d+)\+?\s*(?:years?|yrs?)", RegexOptions.IgnoreCase | RegexOptions.Compiled),
            new Regex(@"at least (\d+)\s*(?:years?|yrs?)", RegexOptions.IgnoreCase | RegexOptions.Compiled),
            new Regex(@"minimum (\d+)\s*(?:years?|yrs?)", RegexOptions.IgnoreCase | RegexOptions.Compiled),
            new Regex(@"min (\d+)\s*(?:years?|yrs?)", RegexOptions.IgnoreCase | RegexOptions.Compiled),
            new Regex(@"(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)", RegexOptions.IgnoreCase | RegexOptions.Compiled)
        };
    }

    public int? ExtractYears(string queryText)
    {
        foreach (var pattern in _patterns)
        {
            var match = pattern.Match(queryText);
            if (match.Success && match.Groups.Count > 1)
            {
                if (int.TryParse(match.Groups[1].Value, out var years))
                {
                    return years;
                }
            }
        }

        return null;
    }
}
