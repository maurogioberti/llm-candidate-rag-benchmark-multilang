using System.Text.Json.Serialization;

namespace Rag.Candidates.Core.Domain.Entities;

public class Skill
{
    [JsonPropertyName("SkillName")]
    public string? Name { get; set; }
    
    [JsonPropertyName("SkillCategory")]
    public string? Category { get; set; }
    
    [JsonPropertyName("SkillLevel")]
    public string? Level { get; set; }
    
    [JsonPropertyName("YearsExperience")]
    public int? YearsExperience { get; set; }
    
    [JsonPropertyName("Evidence")]
    public string? Evidence { get; set; }
    
    [JsonPropertyName("IsRelevant")]
    public bool? IsRelevant { get; set; }
}