using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Application.Configuration;

public static class PathHelper
{
    public static string GetBaseDirectory()
    {
        var currentDirectory = Directory.GetCurrentDirectory();
        var directory = new DirectoryInfo(currentDirectory);
        directory = directory.Parent?.Parent;
        return directory?.FullName!;
    }

    public static string CleanRelativePath(string path)
    {
        return path.StartsWith("./") ? path.Substring(2) : path;
    }

    public static string GetAbsolutePath(string relativePath)
    {
        var baseDirectory = GetBaseDirectory();
        var cleanPath = CleanRelativePath(relativePath);
        return Path.Combine(baseDirectory, cleanPath);
    }

    public static string GetDataPath(DataSettings dataSettings, params string[] subPaths)
    {
        var baseDirectory = GetBaseDirectory();
        var dataRoot = CleanRelativePath(dataSettings.Root);
        
        var pathParts = new[] { baseDirectory, dataRoot }.Concat(subPaths).ToArray();
        return Path.Combine(pathParts);
    }

    public static string GetInputDirectory(DataSettings dataSettings)
    {
        return GetDataPath(dataSettings, dataSettings.Input);
    }

    public static string GetSchemaPath(DataSettings dataSettings, string schemaFileName = "candidate_record.schema.json")
    {
        return GetDataPath(dataSettings, dataSettings.Schema, schemaFileName);
    }

    public static string GetPromptsDirectory(DataSettings dataSettings)
    {
        return GetDataPath(dataSettings, dataSettings.Prompts);
    }

    public static string GetEmbeddingsInstructionsDirectory(DataSettings dataSettings)
    {
        return GetDataPath(dataSettings, dataSettings.EmbInstructions);
    }
}
