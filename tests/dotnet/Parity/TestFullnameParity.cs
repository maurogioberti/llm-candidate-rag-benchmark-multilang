using System.Net.Http.Json;
using System.Text.Json;

const string DOTNET_API_URL = "http://localhost:5000";
const string TEST_QUERY_JAVA = "who is the best candidate for java?";
const string EXPECTED_JAVA_CANDIDATE_FULLNAME = "Jan-Claudiu Crisan";
const string EXPECTED_CANDIDATE_ID_FRAGMENT = "JanClaudiuCrisan";

Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine(".NET PARITY TEST: Fullname Validation");
Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine("\nValidates that .NET API returns real human fullname, not candidate_id slug");
Console.WriteLine("This ensures Python/NET behavioral parity.\n");

using var httpClient = new HttpClient();
httpClient.Timeout = TimeSpan.FromSeconds(30);

Console.WriteLine($"Testing .NET API at {DOTNET_API_URL}");
Console.WriteLine($"Query: '{TEST_QUERY_JAVA}'");
Console.WriteLine("\n" + "-".PadRight(80, '-'));

try
{
    var response = await httpClient.PostAsJsonAsync(
        $"{DOTNET_API_URL}/chat",
        new { question = TEST_QUERY_JAVA }
    );
    
    response.EnsureSuccessStatusCode();
    var result = await response.Content.ReadFromJsonAsync<JsonElement>();
    
    var metadata = result.GetProperty("metadata");
    var selectedCandidate = metadata.GetProperty("selected_candidate");
    
    var fullname = selectedCandidate.GetProperty("fullname").GetString();
    var candidateId = selectedCandidate.GetProperty("candidate_id").GetString();
    
    Console.WriteLine("RESPONSE RECEIVED:");
    Console.WriteLine($"  fullname: {fullname}");
    Console.WriteLine($"  candidate_id: {candidateId}");
    
    Console.WriteLine("\n" + "-".PadRight(80, '-'));
    Console.WriteLine("ASSERTIONS:");
    Console.WriteLine("-".PadRight(80, '-'));
    
    if (fullname != EXPECTED_JAVA_CANDIDATE_FULLNAME)
    {
        Console.WriteLine($"❌ FAIL: Expected fullname '{EXPECTED_JAVA_CANDIDATE_FULLNAME}', got '{fullname}'");
        Environment.Exit(1);
    }
    Console.WriteLine($"[OK] fullname is correct: {fullname}");
    
    if (!candidateId.Contains(EXPECTED_CANDIDATE_ID_FRAGMENT))
    {
        Console.WriteLine($"❌ FAIL: Expected candidate_id containing '{EXPECTED_CANDIDATE_ID_FRAGMENT}', got '{candidateId}'");
        Environment.Exit(1);
    }
    Console.WriteLine($"[OK] candidate_id is correct: {candidateId}");
    
    if (fullname == candidateId)
    {
        Console.WriteLine($"❌ FAIL: fullname equals candidate_id (both '{fullname}')");
        Environment.Exit(1);
    }
    Console.WriteLine($"[OK] fullname != candidate_id");
    
    Console.WriteLine("\n" + "=".PadRight(80, '='));
    Console.WriteLine("[PASS] .NET PARITY TEST PASSED");
    Console.WriteLine("=".PadRight(80, '='));
    Console.WriteLine($"Selected Candidate: {fullname} (ID: {candidateId})");
    Console.WriteLine("=".PadRight(80, '='));
}
catch (HttpRequestException ex)
{
    Console.WriteLine($"❌ FAIL: HTTP error - {ex.Message}");
    Console.WriteLine("\nMake sure .NET API is running on http://localhost:5000");
    Environment.Exit(1);
}
catch (Exception ex)
{
    Console.WriteLine($"❌ FAIL: {ex.Message}");
    Environment.Exit(1);
}
