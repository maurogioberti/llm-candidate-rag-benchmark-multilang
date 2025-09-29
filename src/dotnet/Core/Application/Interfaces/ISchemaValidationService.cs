using NJsonSchema;
using Rag.Candidates.Core.Application.DTOs;

namespace Rag.Candidates.Core.Application.Interfaces;

public interface ISchemaValidationService
{
    ValidationResult ValidateAsync(string jsonData);
    JsonSchema GetSchema();
}