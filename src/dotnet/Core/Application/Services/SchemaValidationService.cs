using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NJsonSchema;
using Rag.Candidates.Core.Application.Configuration;
using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Application.Services;

public class SchemaValidationService : ISchemaValidationService
{
    private readonly JsonSchema _schema;

    public SchemaValidationService(DataSettings dataSettings)
    {
        var schemaPath = PathHelper.GetSchemaPath(dataSettings);

        if (!File.Exists(schemaPath))
            throw new FileNotFoundException($"Schema file not found at: {schemaPath}");

        var schemaJson = File.ReadAllText(schemaPath);
        _schema = JsonSchema.FromJsonAsync(schemaJson).GetAwaiter().GetResult();
    }

    public ValidationResult ValidateAsync(string jsonData)
    {
        try
        {
            var jsonObject = JObject.Parse(jsonData);
            var errors = _schema.Validate(jsonObject);

            return new ValidationResult
            {
                IsValid = !errors.Any(),
                Errors = errors.Select(e => e.ToString()).ToList()
            };
        }
        catch (JsonException ex)
        {
            return new ValidationResult
            {
                IsValid = false,
                Errors = [$"Invalid JSON format: {ex.Message}"]
            };
        }
    }

    public JsonSchema GetSchema() => _schema;
}