using Rag.Candidates.Core.Domain.Configuration;
using Rag.Candidates.Core.Domain.Entities;
using Rag.Candidates.Core.Domain.Enums;
using Microsoft.SemanticKernel.Memory;

namespace Rag.Candidates.Core.Application.Services;

public sealed class SkillDocumentBuilder
{
    private readonly VectorMetadataConfig _config;

    public SkillDocumentBuilder(VectorMetadataConfig config)
    {
        _config = config;
    }

    public List<(string Content, Dictionary<string, object> Metadata)> BuildSkillDocuments(
        CandidateRecord candidate,
        string candidateId,
        string seniorityLevel,
        int yearsExperience)
    {
        var documents = new List<(string, Dictionary<string, object>)>();

        if (candidate.SkillMatrix == null)
            return documents;

        foreach (var skill in candidate.SkillMatrix)
        {
            if (string.IsNullOrWhiteSpace(skill.Name) || string.IsNullOrWhiteSpace(skill.Level))
                continue;

            if (!SkillLevelExtensions.IsStrong(skill.Level))
                continue;

            var metadata = BuildSkillMetadata(
                candidateId: candidateId,
                skillName: skill.Name,
                skillLevel: skill.Level,
                seniorityLevel: seniorityLevel,
                yearsExperience: yearsExperience
            );

            var content = BuildSkillContent(
                skillName: skill.Name,
                skillLevel: skill.Level,
                evidence: skill.Evidence
            );

            documents.Add((content, metadata));
        }

        return documents;
    }

    private Dictionary<string, object> BuildSkillMetadata(
        string candidateId,
        string skillName,
        string skillLevel,
        string seniorityLevel,
        int yearsExperience)
    {
        return new Dictionary<string, object>
        {
            [_config.FieldType] = _config.TypeSkill,
            [_config.FieldCandidateId] = candidateId,
            [_config.FieldSkillName] = skillName,
            [_config.FieldSkillLevel] = skillLevel,
            [_config.FieldSeniorityLevel] = seniorityLevel,
            [_config.FieldYearsExperience] = yearsExperience
        };
    }

    private static string BuildSkillContent(
        string skillName,
        string skillLevel,
        string? evidence = null)
    {
        var content = $"{skillName} ({skillLevel})";

        if (!string.IsNullOrWhiteSpace(evidence))
        {
            content += $": {evidence}";
        }

        return content;
    }
}
