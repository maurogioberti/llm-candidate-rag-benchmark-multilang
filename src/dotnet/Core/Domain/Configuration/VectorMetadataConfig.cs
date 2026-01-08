namespace Rag.Candidates.Core.Domain.Configuration;

public sealed record VectorMetadataConfig
{
    public string FieldType { get; init; } = "type";
    public string FieldCandidateId { get; init; } = "candidate_id";
    public string FieldFullname { get; init; } = "fullname";
    public string FieldEnglishLevel { get; init; } = "english_level";
    public string FieldEnglishLevelNum { get; init; } = "english_level_num";
    public string FieldSeniorityLevel { get; init; } = "seniority_level";
    public string FieldYearsExperience { get; init; } = "years_experience";
    public string FieldRelevantYears { get; init; } = "relevant_years";
    public string FieldMainIndustry { get; init; } = "main_industry";
    public string FieldPrimarySkills { get; init; } = "primary_skills";
    public string FieldSkillName { get; init; } = "skill_name";
    public string FieldSkillLevel { get; init; } = "skill_level";

    public string TypeCandidate { get; init; } = "candidate";
    public string TypeSkill { get; init; } = "skill";
    public string TypeLlmInstruction { get; init; } = "llm_instruction";

    public int PrimarySkillsMaxCount { get; init; } = 5;
    public string[] StrongSkillLevels { get; init; } = new[] { "High", "Very High" };

    public static VectorMetadataConfig Default { get; } = new();
}
