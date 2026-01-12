# Tests

This directory contains tests for the multi-language RAG benchmark.

## Structure

- **python/** - Python implementation tests
  - `integration/` - Integration tests (indexing, query execution)
  - `parity/` - Python/NET behavior parity tests
  - `normalization/` - Technology normalization validation
  
- **dotnet/** - .NET implementation tests
  - `Integration/` - Integration tests (indexing, query execution)
  - `Parity/` - Python/NET behavior parity tests
  - `Normalization/` - Technology normalization validation

## Philosophy

This is a **benchmark repository** designed to validate RAG implementation quality and cross-stack parity. Tests focus on:

- **Integration testing** - End-to-end behavior validation
- **Parity checking** - Ensuring Python and .NET behave identically
- **High-signal validation** - Focused tests that verify core functionality

**Python and .NET test suites are intentionally balanced** to ensure:
- Same behaviors are validated in both stacks
- Conceptual parity, not line-by-line equality
- Confidence that both implementations work identically

Design principles:
- Test real integration points rather than mocked dependencies
- Lightweight test infrastructure aligned with benchmark goals
- Clear, maintainable tests that validate core behaviors

## Running Tests

### Prerequisites

1. **Python environment** - Python 3.10+ with dependencies installed (`pip install -e .`)
2. **Running services** - Embeddings service and vector database must be running
3. **.NET SDK** - .NET 8.0+ SDK installed
4. **APIs running** (for parity tests) - Both Python and .NET APIs must be accessible

### Python Tests

Run from the repository root:

```bash
# Integration test
python tests/python/integration/test_best_java_candidate_returns_human_fullname.py

# Parity tests
python tests/python/parity/test_fullname_parity.py
python tests/python/parity/test_parity.py

# Normalization test
python tests/python/normalization/test_normalization.py
```

### .NET Tests

Run from the repository root:

```bash
# Integration test
dotnet run --project tests/dotnet/Integration/Integration.csproj

# Parity tests
dotnet run --project tests/dotnet/Parity/TestFullnameParity.csproj
dotnet run --project tests/dotnet/Parity/TestApiParity.csproj

# Normalization test
dotnet run --project tests/dotnet/Normalization/Normalization.csproj
```

### Run All Tests

Use the provided scripts to run all tests at once:

```bash
# Windows (PowerShell)
.\tests\run-tests.ps1

# Unix/Linux/macOS
./tests/run-tests.sh
```

## Test Coverage Matrix

| Category | Python | .NET | Balance |
|----------|--------|------|----------|
| **Integration** | 1 test | 1 test | ✓ Equal |
| **Parity** | 2 tests | 2 tests | ✓ Equal |
| **Normalization** | 1 test | 1 test | ✓ Equal |
| **TOTAL** | **4 tests** | **4 tests** | ✓ **Perfect Parity** |

### Behaviors Validated in Both Stacks

| Behavior | Python | .NET |
|----------|--------|------|
| Java query returns correct candidate | ✓ | ✓ |
| fullname != candidate_id | ✓ | ✓ |
| fullname from GeneralInfo.Fullname | ✓ | ✓ |
| Technology normalization rules | ✓ | ✓ |
| Python/NET API parity | ✓ | ✓ |

## Key Tests

**Python:**
- `integration/test_best_java_candidate_returns_human_fullname.py` - Validates fullname correctness
- `parity/test_fullname_parity.py` - Ensures Python returns real human fullname
- `parity/test_parity.py` - Compares Python vs .NET API responses
- `normalization/test_normalization.py` - Technology normalization (Java 8→Java, Spring Boot→Spring, etc.)

**.NET:**
- `Integration/TestJavaCandidateReturnsHumanFullname.cs` - Validates fullname correctness
- `Parity/TestFullnameParity.cs` - Ensures .NET returns real human fullname
- `Parity/TestApiParity.cs` - Compares Python vs .NET API responses
- `Normalization/TestNormalization.cs` - Technology normalization (identical rules to Python)
