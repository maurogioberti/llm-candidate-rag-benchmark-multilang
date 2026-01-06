using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Entities;

namespace Rag.Candidates.Core.Application.Services;

public sealed class VectorMetadataBuilder
{
    private readonly VectorMetadataConfig _config;
    private readonly PrimarySkillsExtractor _skillsExtractor;

    public VectorMetadataBuilder(VectorMetadataConfig config)
    {
        _config = config;
        _skillsExtractor = new PrimarySkillsExtractor(config);
    }

    public Dictionary<string, object> BuildCandidateMetadata(
        CandidateRecord candidate,
        string candidateId,
        string englishLevel,
        int englishLevelNum)
    {
        var metadata = new Dictionary<string, object>
        {
            [_config.FieldType] = _config.TypeCandidate,
            [_config.FieldCandidateId] = candidateId,
            [_config.FieldEnglishLevel] = englishLevel,
            [_config.FieldEnglishLevelNum] = englishLevelNum
        };

        // Add Phase 1 enrichments
        if (candidate.GeneralInfo != null)
        {
            if (candidate.GeneralInfo.SeniorityLevel != null)
                metadata[_config.FieldSeniorityLevel] = candidate.GeneralInfo.SeniorityLevel;

            if (candidate.GeneralInfo.YearsExperience.HasValue)
                metadata[_config.FieldYearsExperience] = candidate.GeneralInfo.YearsExperience.Value;

            if (candidate.GeneralInfo.RelevantYears.HasValue)
                metadata[_config.FieldRelevantYears] = candidate.GeneralInfo.RelevantYears.Value;

            if (candidate.GeneralInfo.MainIndustry != null)
                metadata[_config.FieldMainIndustry] = candidate.GeneralInfo.MainIndustry;
        }

        // Extract primary skills
        var primarySkills = _skillsExtractor.Extract(candidate);
        if (primarySkills.Length > 0)
            metadata[_config.FieldPrimarySkills] = primarySkills;

        return metadata;
    }
}
