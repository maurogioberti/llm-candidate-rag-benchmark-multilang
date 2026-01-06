using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Entities;

namespace Rag.Candidates.Core.Application.Services;

public sealed class PrimarySkillsExtractor
{
    private readonly VectorMetadataConfig _config;

    public PrimarySkillsExtractor(VectorMetadataConfig config)
    {
        _config = config;
    }

    public string[] Extract(CandidateRecord candidate)
    {
        if (candidate.SkillMatrix == null || candidate.SkillMatrix.Length == 0)
            return Array.Empty<string>();

        var primarySkills = new List<string>();

        foreach (var skill in candidate.SkillMatrix)
        {
            if (string.IsNullOrWhiteSpace(skill.SkillName))
                continue;

            // Check if skill level is in the strong category
            if (skill.SkillLevel != null && _config.StrongSkillLevels.Contains(skill.SkillLevel))
            {
                primarySkills.Add(skill.SkillName);
            }
        }

        // Limit to max count and return
        return primarySkills.Take(_config.PrimarySkillsMaxCount).ToArray();
    }
}
