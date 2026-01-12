#!/usr/bin/env pwsh
# Run all tests for the LLM Candidate RAG Benchmark project
# Executes both Python and .NET test suites

$ErrorActionPreference = "Continue"
$failed = 0
$passed = 0

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "LLM CANDIDATE RAG BENCHMARK - TEST SUITE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Python Tests
Write-Host "Running Python Tests..." -ForegroundColor Yellow
Write-Host "-" * 80 -ForegroundColor Gray

$pythonTests = @(
    "tests/python/integration/test_best_java_candidate_returns_human_fullname.py",
    "tests/python/parity/test_fullname_parity.py",
    "tests/python/parity/test_parity.py",
    "tests/python/normalization/test_normalization.py"
)

foreach ($test in $pythonTests) {
    Write-Host "`nRunning: $test" -ForegroundColor Cyan
    python $test
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PASSED: $test" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "✗ FAILED: $test" -ForegroundColor Red
        $failed++
    }
}

# .NET Tests
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "Running .NET Tests..." -ForegroundColor Yellow
Write-Host "-" * 80 -ForegroundColor Gray

$dotnetTests = @(
    "tests/dotnet/Integration/Integration.csproj",
    "tests/dotnet/Parity/TestFullnameParity.csproj",
    "tests/dotnet/Parity/TestApiParity.csproj",
    "tests/dotnet/Normalization/Normalization.csproj"
)

foreach ($test in $dotnetTests) {
    Write-Host "`nRunning: $test" -ForegroundColor Cyan
    dotnet run --project $test
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PASSED: $test" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "✗ FAILED: $test" -ForegroundColor Red
        $failed++
    }
}

# Summary
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Total tests: $($passed + $failed)"
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "=" * 80 -ForegroundColor Cyan

if ($failed -gt 0) {
    exit 1
} else {
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
    exit 0
}
