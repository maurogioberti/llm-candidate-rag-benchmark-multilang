using System.Net.Http.Json;
using System.Text.Json;

const string PYTHON_API_URL = "http://localhost:8000";
const string DOTNET_API_URL = "http://localhost:5000";
const string TEST_QUERY_JAVA = "who is the best candidate for java?";

Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine("PYTHON vs .NET API PARITY TEST");
Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine("\nValidates that Python and .NET APIs return identical behavior");
Console.WriteLine("for the same query.\n");

using var httpClient = new HttpClient();
httpClient.Timeout = TimeSpan.FromSeconds(30);

Console.WriteLine($"Test Query: '{TEST_QUERY_JAVA}'");
Console.WriteLine("\n" + "-".PadRight(80, '-'));

// Test Python API
Console.WriteLine("Testing Python API...");
JsonElement? pythonResult = null;
try
{
    var pythonResponse = await httpClient.PostAsJsonAsync(
        $"{PYTHON_API_URL}/chat",
        new { question = TEST_QUERY_JAVA }
    );
    pythonResponse.EnsureSuccessStatusCode();
    pythonResult = await pythonResponse.Content.ReadFromJsonAsync<JsonElement>();
    Console.WriteLine("✓ Python API responded");
}
catch (Exception ex)
{
    Console.WriteLine($"❌ Python API error: {ex.Message}");
}

// Test .NET API
Console.WriteLine("Testing .NET API...");
JsonElement? dotnetResult = null;
try
{
    var dotnetResponse = await httpClient.PostAsJsonAsync(
        $"{DOTNET_API_URL}/chat",
        new { question = TEST_QUERY_JAVA }
    );
    dotnetResponse.EnsureSuccessStatusCode();
    dotnetResult = await dotnetResponse.Content.ReadFromJsonAsync<JsonElement>();
    Console.WriteLine("✓ .NET API responded");
}
catch (Exception ex)
{
    Console.WriteLine($"❌ .NET API error: {ex.Message}");
}

if (pythonResult == null || dotnetResult == null)
{
    Console.WriteLine("\n❌ FAIL: One or both APIs failed to respond");
    Console.WriteLine("\nMake sure both APIs are running:");
    Console.WriteLine($"  Python: {PYTHON_API_URL}");
    Console.WriteLine($"  .NET:   {DOTNET_API_URL}");
    Environment.Exit(1);
}

Console.WriteLine("\n" + "-".PadRight(80, '-'));
Console.WriteLine("COMPARING RESULTS:");
Console.WriteLine("-".PadRight(80, '-'));

var pythonMetadata = pythonResult.Value.GetProperty("metadata");
var dotnetMetadata = dotnetResult.Value.GetProperty("metadata");

var pythonCandidate = pythonMetadata.GetProperty("selected_candidate");
var dotnetCandidate = dotnetMetadata.GetProperty("selected_candidate");

var pythonFullname = pythonCandidate.GetProperty("fullname").GetString();
var dotnetFullname = dotnetCandidate.GetProperty("fullname").GetString();

var pythonCandidateId = pythonCandidate.GetProperty("candidate_id").GetString();
var dotnetCandidateId = dotnetCandidate.GetProperty("candidate_id").GetString();

Console.WriteLine($"Python fullname:      {pythonFullname}");
Console.WriteLine($".NET fullname:        {dotnetFullname}");
Console.WriteLine($"\nPython candidate_id:  {pythonCandidateId}");
Console.WriteLine($".NET candidate_id:    {dotnetCandidateId}");

Console.WriteLine("\n" + "-".PadRight(80, '-'));
Console.WriteLine("PARITY CHECKS:");
Console.WriteLine("-".PadRight(80, '-'));

var passed = true;

if (pythonFullname != dotnetFullname)
{
    Console.WriteLine($"❌ FAIL: Fullname mismatch");
    Console.WriteLine($"  Python: {pythonFullname}");
    Console.WriteLine($"  .NET:   {dotnetFullname}");
    passed = false;
}
else
{
    Console.WriteLine($"✓ Fullname matches: {pythonFullname}");
}

if (pythonCandidateId != dotnetCandidateId)
{
    Console.WriteLine($"❌ FAIL: Candidate ID mismatch");
    Console.WriteLine($"  Python: {pythonCandidateId}");
    Console.WriteLine($"  .NET:   {dotnetCandidateId}");
    passed = false;
}
else
{
    Console.WriteLine($"✓ Candidate ID matches: {pythonCandidateId}");
}

if (pythonFullname == pythonCandidateId)
{
    Console.WriteLine($"❌ FAIL: Python fullname equals candidate_id");
    passed = false;
}
else
{
    Console.WriteLine($"✓ Python fullname != candidate_id");
}

if (dotnetFullname == dotnetCandidateId)
{
    Console.WriteLine($"❌ FAIL: .NET fullname equals candidate_id");
    passed = false;
}
else
{
    Console.WriteLine($"✓ .NET fullname != candidate_id");
}

if (!passed)
{
    Console.WriteLine("\n" + "=".PadRight(80, '='));
    Console.WriteLine("❌ PARITY TEST FAILED");
    Console.WriteLine("=".PadRight(80, '='));
    Environment.Exit(1);
}

Console.WriteLine("\n" + "=".PadRight(80, '='));
Console.WriteLine("✓ PARITY TEST PASSED");
Console.WriteLine("=".PadRight(80, '='));
Console.WriteLine("Python and .NET APIs return identical results");
Console.WriteLine("=".PadRight(80, '='));
