#!/bin/bash
# Run all tests for the LLM Candidate RAG Benchmark project
# Executes both Python and .NET test suites

set +e  # Continue on error
failed=0
passed=0

echo "================================================================================"
echo "LLM CANDIDATE RAG BENCHMARK - TEST SUITE"
echo "================================================================================"
echo ""

# Python Tests
echo "Running Python Tests..."
echo "--------------------------------------------------------------------------------"

python_tests=(
    "tests/python/integration/test_best_java_candidate_returns_human_fullname.py"
    "tests/python/parity/test_fullname_parity.py"
    "tests/python/parity/test_parity.py"
    "tests/python/normalization/test_normalization.py"
)

for test in "${python_tests[@]}"; do
    echo ""
    echo "Running: $test"
    python "$test"
    if [ $? -eq 0 ]; then
        echo "✓ PASSED: $test"
        ((passed++))
    else
        echo "✗ FAILED: $test"
        ((failed++))
    fi
done

# .NET Tests
echo ""
echo "================================================================================"
echo "Running .NET Tests..."
echo "--------------------------------------------------------------------------------"

dotnet_tests=(
    "tests/dotnet/Integration/Integration.csproj"
    "tests/dotnet/Parity/TestFullnameParity.csproj"
    "tests/dotnet/Parity/TestApiParity.csproj"
    "tests/dotnet/Normalization/Normalization.csproj"
)

for test in "${dotnet_tests[@]}"; do
    echo ""
    echo "Running: $test"
    dotnet run --project "$test"
    if [ $? -eq 0 ]; then
        echo "✓ PASSED: $test"
        ((passed++))
    else
        echo "✗ FAILED: $test"
        ((failed++))
    fi
done

# Summary
echo ""
echo "================================================================================"
echo "TEST SUMMARY"
echo "================================================================================"
echo "Total tests: $((passed + failed))"
echo "Passed: $passed"
echo "Failed: $failed"
echo "================================================================================"

if [ $failed -gt 0 ]; then
    exit 1
else
    echo ""
    echo "✓ All tests passed!"
    exit 0
fi
