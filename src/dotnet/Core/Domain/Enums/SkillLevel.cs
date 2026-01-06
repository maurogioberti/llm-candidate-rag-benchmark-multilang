namespace Rag.Candidates.Core.Domain.Enums;

public enum SkillLevel
{
    Low = 0,
    Medium = 1,
    High = 2,
    VeryHigh = 3
}

public static class SkillLevelExtensions
{
    public static SkillLevel? FromString(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            return null;

        var normalized = value.Trim();

        return normalized switch
        {
            "Low" => SkillLevel.Low,
            "Medium" => SkillLevel.Medium,
            "High" => SkillLevel.High,
            "Very High" => SkillLevel.VeryHigh,
            "VeryHigh" => SkillLevel.VeryHigh,
            _ => null
        };
    }

    public static bool IsStrong(SkillLevel level)
    {
        return level == SkillLevel.High || level == SkillLevel.VeryHigh;
    }

    public static bool IsStrong(string levelString)
    {
        var level = FromString(levelString);
        return level.HasValue && IsStrong(level.Value);
    }
}
