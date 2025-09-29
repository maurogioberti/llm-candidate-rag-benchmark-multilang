namespace Rag.Candidates.Core.Domain.Entities;

public class Skill
{
    public string? Name { get; set; }
    public string? Category { get; set; }
    public string? Level { get; set; }
    public int? YearsExperience { get; set; }
    public string? Evidence { get; set; }
    public bool? IsRelevant { get; set; }
}