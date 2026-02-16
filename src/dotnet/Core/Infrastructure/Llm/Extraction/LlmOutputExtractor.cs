using System.Text.RegularExpressions;

namespace Rag.Candidates.Core.Infrastructure.Llm.Extraction;

/// <summary>
/// Pure static helper that cleans raw LLM output and extracts JSON content.
/// Handles markdown fences, thinking blocks, and preamble/postamble text.
/// </summary>
public static partial class LlmOutputExtractor
{
    private const string NoJsonFoundMessage = "No JSON object found in LLM output";

    /// <summary>
    /// Cleans raw LLM output and extracts the outermost JSON object as a string.
    /// </summary>
    public static string ExtractJson(string rawOutput)
    {
        if (string.IsNullOrWhiteSpace(rawOutput))
            throw new FormatException(NoJsonFoundMessage);

        var cleaned = StripThinkingBlocks(rawOutput);
        cleaned = StripMarkdownFences(cleaned);

        return ExtractOutermostJsonObject(cleaned);
    }

    /// <summary>
    /// Removes &lt;think&gt;...&lt;/think&gt; blocks (e.g. DeepSeek-R1).
    /// </summary>
    internal static string StripThinkingBlocks(string input)
    {
        return ThinkBlockRegex().Replace(input, string.Empty).Trim();
    }

    /// <summary>
    /// Removes markdown code fences: ```json ... ``` or ``` ... ```
    /// </summary>
    internal static string StripMarkdownFences(string input)
    {
        return MarkdownFenceRegex().Replace(input, static m => m.Groups[1].Value).Trim();
    }

    /// <summary>
    /// Extracts the outermost balanced JSON object from the string.
    /// Uses brace-depth counting rather than IndexOf/LastIndexOf to avoid
    /// spanning across multiple disjoint JSON objects.
    /// </summary>
    internal static string ExtractOutermostJsonObject(string input)
    {
        var start = input.IndexOf('{');
        if (start == -1)
            throw new FormatException(NoJsonFoundMessage);

        var depth = 0;
        var inString = false;
        var escape = false;

        for (var i = start; i < input.Length; i++)
        {
            var c = input[i];

            if (escape)
            {
                escape = false;
                continue;
            }

            if (c == '\\' && inString)
            {
                escape = true;
                continue;
            }

            if (c == '"')
            {
                inString = !inString;
                continue;
            }

            if (inString)
                continue;

            if (c == '{')
                depth++;
            else if (c == '}')
            {
                depth--;
                if (depth == 0)
                    return input[start..(i + 1)];
            }
        }

        throw new FormatException(NoJsonFoundMessage);
    }

    [GeneratedRegex(@"<think>[\s\S]*?</think>", RegexOptions.IgnoreCase | RegexOptions.Compiled)]
    private static partial Regex ThinkBlockRegex();

    [GeneratedRegex(@"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", RegexOptions.Compiled)]
    private static partial Regex MarkdownFenceRegex();
}
