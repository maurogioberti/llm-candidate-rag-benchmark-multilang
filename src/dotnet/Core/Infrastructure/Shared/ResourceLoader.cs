using System.Text.Json;
using Rag.Candidates.Core.Application.Configuration;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Shared;

public sealed class ResourceLoader : IResourceLoader
{
    private readonly DataSettings _dataSettings;

    private const string LlmInstructionFile = "llm.jsonl";
    private const string InstructionField = "instruction";
    private const string InputField = "input";
    private const string OutputField = "output";

    private const string JsonFileSearchPattern = "*.json";
    private const char NewLineChar = '\n';
    private const string PromptFileNotFoundMessage = "Prompt file not found: {0}";

    public ResourceLoader(DataSettings dataSettings)
    {
        _dataSettings = dataSettings;
    }

    public async Task<string> LoadPromptAsync(string name, CancellationToken ct = default)
    {
        var baseDirectory = PathHelper.GetBaseDirectory();
        var promptsPath = Path.Combine(baseDirectory, _dataSettings.Root, _dataSettings.Prompts, name);
        
        if (!File.Exists(promptsPath))
        {
            throw new FileNotFoundException(string.Format(PromptFileNotFoundMessage, promptsPath));
        }

        return await File.ReadAllTextAsync(promptsPath, ct);
    }

    public async Task<string[]> LoadCandidateRecordsAsync(CancellationToken ct = default)
    {
        var baseDirectory = PathHelper.GetBaseDirectory();
        var inputPath = Path.Combine(baseDirectory, _dataSettings.Root, _dataSettings.Input);
        
        if (!Directory.Exists(inputPath))
        {
            return Array.Empty<string>();
        }

        var jsonFiles = Directory.GetFiles(inputPath, JsonFileSearchPattern);
        var records = new List<string>();

        foreach (var file in jsonFiles)
        {
            var content = await File.ReadAllTextAsync(file, ct);
            records.Add(content);
        }

        return records.ToArray();
    }

    public async Task<LlmInstructionRecord[]> LoadLlmInstructionRecordsAsync(CancellationToken ct = default)
    {
        var baseDirectory = PathHelper.GetBaseDirectory();
        var instructionsPath = Path.Combine(baseDirectory, _dataSettings.Root, _dataSettings.EmbInstructions, LlmInstructionFile);
        
        if (!File.Exists(instructionsPath))
        {
            return Array.Empty<LlmInstructionRecord>();
        }

        var content = await File.ReadAllTextAsync(instructionsPath, ct);
        var lines = content.Split(NewLineChar, StringSplitOptions.RemoveEmptyEntries);
        var records = new List<LlmInstructionRecord>();

        for (int i = 0; i < lines.Length; i++)
        {
            var line = lines[i].Trim();
            if (string.IsNullOrWhiteSpace(line))
                continue;

            try
            {
                var record = JsonSerializer.Deserialize<Dictionary<string, object>>(line);
                if (record != null && 
                    record.ContainsKey(InstructionField) && 
                    record.ContainsKey(InputField) && 
                    record.ContainsKey(OutputField))
                {
                    records.Add(new LlmInstructionRecord(
                        record[InstructionField].ToString() ?? string.Empty,
                        record[InputField],
                        record[OutputField],
                        i + 1
                    ));
                }
            }
            catch (JsonException)
            {
                continue;
            }
        }

        return records.ToArray();
    }
}