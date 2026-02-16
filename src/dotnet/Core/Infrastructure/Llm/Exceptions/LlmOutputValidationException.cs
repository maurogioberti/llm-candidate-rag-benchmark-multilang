namespace Rag.Candidates.Core.Infrastructure.Llm.Exceptions;

public sealed class LlmOutputValidationException : Exception
{
    private const string DefaultMessage = "Failed to extract valid structured output from LLM response";

    public string? RawOutput { get; }

    public LlmOutputValidationException(string? rawOutput = null)
        : base(DefaultMessage)
    {
        RawOutput = rawOutput;
    }

    public LlmOutputValidationException(string message, string? rawOutput = null)
        : base(message)
    {
        RawOutput = rawOutput;
    }

    public LlmOutputValidationException(string message, Exception innerException, string? rawOutput = null)
        : base(message, innerException)
    {
        RawOutput = rawOutput;
    }
}
