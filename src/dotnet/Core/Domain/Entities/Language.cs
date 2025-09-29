using Rag.Candidates.Core.Domain.Enums;

namespace Rag.Candidates.Core.Domain.Entities;

public class Language
{
    public string? Name { get; set; }
    public LanguageProficiency? Proficiency { get; set; }
    public string? Evidence { get; set; }
}