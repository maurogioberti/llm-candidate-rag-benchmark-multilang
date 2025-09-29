using Rag.Candidates.Core.Application.DTOs.Embeddings;
using Rag.Candidates.Core.Application.Interfaces;
using Rag.Candidates.Core.Domain.Configuration;

namespace Rag.Candidates.Core.Infrastructure.Embeddings;

public sealed class HttpEmbeddingsClient : IEmbeddingsClient
{
    private readonly HttpClient _http;
    private readonly string _base;

    private const string EmbedEndpoint = "/embed";
    private const string InstructionPairsEndpoint = "/instruction-pairs";

    private const string InvalidEmbeddingsResponse = "Invalid embeddings response";
    private const string InvalidInstructionPairsResponse = "Invalid instruction-pairs response";

    public HttpEmbeddingsClient(IHttpClientFactory f, EmbeddingsServiceSettings settings)
    {
        _http = f.CreateClient(nameof(HttpEmbeddingsClient));
        _base = settings.Url;
    }

    public async Task<float[][]> EmbedAsync(IEnumerable<string> texts, CancellationToken ct = default)
    {
        var req = new { texts = texts.ToArray() };
        using var resp = await _http.PostAsJsonAsync($"{_base.TrimEnd('/')}{EmbedEndpoint}", req, ct);
        resp.EnsureSuccessStatusCode();
        var payload = await resp.Content.ReadFromJsonAsync<EmbeddingsResponse>(cancellationToken: ct)
                      ?? throw new InvalidOperationException(InvalidEmbeddingsResponse);
        return payload.Vectors;
    }

    public async Task<(string text, Dictionary<string, object> metadata)[]> GetInstructionPairsAsync(string? path = null, CancellationToken ct = default)
    {
        var url = $"{_base.TrimEnd('/')}{InstructionPairsEndpoint}";
        if (!string.IsNullOrWhiteSpace(path))
        {
            url = $"{url}?path={Uri.EscapeDataString(path)}";
        }
        using var resp = await _http.GetAsync(url, ct);
        resp.EnsureSuccessStatusCode();
        var payload = await resp.Content.ReadFromJsonAsync<InstructionPairsResponse>(cancellationToken: ct)
                      ?? throw new InvalidOperationException(InvalidInstructionPairsResponse);
        return payload.Pairs.Select(p => (p.Text, p.Metadata)).ToArray();
    }
}