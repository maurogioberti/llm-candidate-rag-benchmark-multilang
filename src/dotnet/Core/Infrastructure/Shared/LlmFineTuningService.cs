using System.Text.Json;
using Rag.Candidates.Core.Application.Configuration;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Shared;

public sealed class LlmFineTuningService : ILlmFineTuningService
{
    private readonly IResourceLoader _resourceLoader;
    private readonly DataSettings _dataSettings;

    private const string OpenAiExportFilename = "openai_chat.jsonl";
    private const string InstructExportFilename = "instruct_generic.jsonl";
    private const string FinetuneExportsDir = "finetune_exports";
    private const string FileEncoding = "utf-8";
    private const string RoleSystem = "system";
    private const string RoleUser = "user";
    private const string RoleAssistant = "assistant";

    public LlmFineTuningService(IResourceLoader resourceLoader, DataSettings dataSettings)
    {
        _resourceLoader = resourceLoader;
        _dataSettings = dataSettings;
    }

    public async Task ExportForOpenAIAsync(CancellationToken ct = default)
    {
        var records = await _resourceLoader.LoadLlmInstructionRecordsAsync(ct);
        if (records.Length == 0)
        {
            return;
        }

        var baseDirectory = PathHelper.GetBaseDirectory();
        var exportDir = Path.Combine(baseDirectory, _dataSettings.Root, _dataSettings.Finetuning, FinetuneExportsDir);
        Directory.CreateDirectory(exportDir);

        var openAiPath = Path.Combine(exportDir, OpenAiExportFilename);
        using var writer = new StreamWriter(openAiPath, false, System.Text.Encoding.GetEncoding(FileEncoding));

        foreach (var record in records)
        {
            var openAiRecord = new
            {
                messages = new[]
                {
                    new { role = RoleSystem, content = record.Instruction },
                    new { role = RoleUser, content = JsonSerializer.Serialize(record.Input) },
                    new { role = RoleAssistant, content = JsonSerializer.Serialize(record.Output) }
                }
            };

            var jsonLine = JsonSerializer.Serialize(openAiRecord);
            await writer.WriteLineAsync(jsonLine);
        }
    }

    public async Task ExportForInstructAsync(CancellationToken ct = default)
    {
        var records = await _resourceLoader.LoadLlmInstructionRecordsAsync(ct);
        if (records.Length == 0)
        {
            return;
        }

        var baseDirectory = PathHelper.GetBaseDirectory();
        var exportDir = Path.Combine(baseDirectory, _dataSettings.Root, _dataSettings.Finetuning, FinetuneExportsDir);
        Directory.CreateDirectory(exportDir);

        var instructPath = Path.Combine(exportDir, InstructExportFilename);
        using var writer = new StreamWriter(instructPath, false, System.Text.Encoding.GetEncoding(FileEncoding));

        foreach (var record in records)
        {
            var instructRecord = new
            {
                instruction = record.Instruction,
                input = record.Input,
                output = record.Output
            };

            var jsonLine = JsonSerializer.Serialize(instructRecord);
            await writer.WriteLineAsync(jsonLine);
        }
    }
}