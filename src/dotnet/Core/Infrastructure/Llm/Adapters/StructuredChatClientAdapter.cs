using System.Text.Json;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Logging;
using Rag.Candidates.Core.Application.DTOs;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Infrastructure.Llm.Exceptions;
using Rag.Candidates.Core.Infrastructure.Llm.Extraction;
using AIChatMessage = Microsoft.Extensions.AI.ChatMessage;

namespace Rag.Candidates.Core.Infrastructure.Llm.Adapters;

/// <summary>
/// Infrastructure adapter that wraps an MEAI <see cref="IChatClient"/>, extracts
/// structured JSON from the raw LLM response, and deserialises it to <typeparamref name="T"/>.
/// Retries once with a corrective prompt when parsing fails.
/// </summary>
public sealed class StructuredChatClientAdapter<T>(
    IChatClient chatClient,
    ILogger<StructuredChatClientAdapter<T>> logger) : IStructuredLlmClient<T> where T : class
{
    private const string RetryUserPrompt = "Your previous response was not valid JSON. Respond ONLY with the valid JSON object. No markdown, no explanation.";
    private const int MaxAttempts = 2;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public async Task<T> GenerateStructuredAsync(ChatContext context, CancellationToken ct = default)
    {
        var messages = BuildMessages(context);
        string? lastRawOutput = null;

        for (var attempt = 1; attempt <= MaxAttempts; attempt++)
        {
            var response = await chatClient.GetResponseAsync(messages, cancellationToken: ct);
            lastRawOutput = response.Messages.LastOrDefault()?.Text ?? string.Empty;

            if (string.IsNullOrWhiteSpace(lastRawOutput))
            {
                logger.LogWarning(
                    "Chat client returned empty response on attempt {Attempt}/{MaxAttempts}. Message count: {MessageCount}",
                    attempt, MaxAttempts, response.Messages.Count);
            }

            var result = TryParseOutput(lastRawOutput, attempt);
            if (result is not null)
                return result;

            // Append the failed response + corrective prompt for the retry
            messages.Add(new AIChatMessage(ChatRole.Assistant, lastRawOutput));
            messages.Add(new AIChatMessage(ChatRole.User, RetryUserPrompt));
        }

        throw new LlmOutputValidationException(
            $"Failed to extract valid {typeof(T).Name} from LLM output after {MaxAttempts} attempts",
            lastRawOutput);
    }

    private T? TryParseOutput(string rawOutput, int attempt)
    {
        try
        {
            var afterThink = LlmOutputExtractor.StripThinkingBlocks(rawOutput);
            var cleaned = LlmOutputExtractor.StripMarkdownFences(afterThink);
            var json = LlmOutputExtractor.ExtractOutermostJsonObject(cleaned);
            var result = JsonSerializer.Deserialize<T>(json, JsonOptions);

            if (result is null)
                throw new FormatException($"Deserialization returned null for type {typeof(T).Name}");

            return result;
        }
        catch (Exception ex) when (ex is FormatException or JsonException)
        {
            logger.LogWarning(
                ex,
                "Failed to parse structured output on attempt {Attempt}/{MaxAttempts} for type {Type}",
                attempt, MaxAttempts, typeof(T).Name);
            return null;
        }
    }

    private static List<AIChatMessage> BuildMessages(ChatContext context)
    {
        var messages = new List<AIChatMessage>
        {
            new(ChatRole.System, context.SystemPrompt)
        };

        if (!string.IsNullOrEmpty(context.Context))
        {
            messages.Add(new AIChatMessage(ChatRole.System, context.Context));
        }

        messages.Add(new AIChatMessage(ChatRole.User, context.UserMessage));
        return messages;
    }
}
