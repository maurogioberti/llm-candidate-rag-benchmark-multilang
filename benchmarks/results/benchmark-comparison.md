# Benchmark Comparison Report

## Performance Tests (K6)

### Smoke Test Results
- **.NET**: See `results\dotnet\smoke-test.json`
- **Python**: See `results\python\smoke-test.json`

### Load Test Results
- **.NET**: See `results\dotnet\load-test.json`
- **Python**: See `results\python\load-test.json`

### Stress Test Results
- **.NET**: See `results\dotnet\stress-test.json`
- **Python**: See `results\python\stress-test.json`

## Quality Evaluation (LLM-as-a-Judge)
- **Report**: See `results\evaluation_report.md`
- **Raw Results**: See `results\evaluation_results.json`

## Summary
*Detailed analysis will be added after running all tests*

## How to Run
```powershell
# Run all benchmarks
.\run-benchmarks.ps1 both

# Run only .NET
.\run-benchmarks.ps1 dotnet

# Run only Python
.\run-benchmarks.ps1 python
```
