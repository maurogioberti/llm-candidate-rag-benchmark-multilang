# Benchmark runner script for .NET vs Python chatbot comparison
# Usage: .\run-benchmarks.ps1 [dotnet|python|both]

param(
    [Parameter(Position=0)]
    [ValidateSet("dotnet", "python", "both")]
    [string]$Target = "both"
)

# Configuration
$DOTNET_URL = "http://localhost:5000"
$PYTHON_URL = "http://localhost:8000"

# Use $PSScriptRoot to make paths relative to script location (benchmarks/)
$SCRIPT_DIR = $PSScriptRoot
$RESULTS_DIR = Join-Path $SCRIPT_DIR "results"
$K6_SCRIPTS_DIR = Join-Path $SCRIPT_DIR "k6"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if service is running
function Test-Service {
    param(
        [string]$Url,
        [string]$ServiceName
    )
    
    Write-Status "Checking if $ServiceName is running at $Url..."
    
    try {
        $response = Invoke-WebRequest -Uri "$Url/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "$ServiceName is running"
            return $true
        }
    }
    catch {
        Write-Error "$ServiceName is not running at $Url"
        return $false
    }
    
    return $false
}

# Function to run K6 performance tests
function Invoke-K6Tests {
    param(
        [string]$ServiceUrl,
        [string]$ServiceName
    )
    
    $outputDir = "$RESULTS_DIR\$ServiceName"
    
    Write-Status "Running K6 performance tests for $ServiceName..."
    
    # Create output directory
    if (!(Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # Check if K6 is installed
    try {
        # Try to find k6 in common locations
        $k6Path = $null
        if (Get-Command k6 -ErrorAction SilentlyContinue) {
            $k6Path = "k6"
        } elseif (Test-Path "C:\Program Files\k6\k6.exe") {
            $k6Path = "C:\Program Files\k6\k6.exe"
            # Add to PATH for this session
            $env:PATH += ";C:\Program Files\k6"
        } else {
            throw "K6 not found"
        }
        
        $k6Version = & $k6Path version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "K6 not working"
        }
        Write-Status "K6 version: $($k6Version -split "`n" | Select-Object -First 1)"
    }
    catch {
        Write-Error "K6 is not installed or not in PATH. Please install K6 first."
        Write-Status "Install K6: winget install k6"
        Write-Status "After installation, restart PowerShell or run: `$env:PATH += `";C:\Program Files\k6`""
        return $false
    }
    
    # Run smoke test
    Write-Status "Running smoke test..."
    $env:BASE_URL = $ServiceUrl
    & $k6Path run --out json="$outputDir\smoke-test.json" "$K6_SCRIPTS_DIR\smoke-test.js"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test failed for $ServiceName"
        return $false
    }
    
    # Run load test
    Write-Status "Running load test..."
    & $k6Path run --out json="$outputDir\load-test.json" "$K6_SCRIPTS_DIR\load-test.js"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Load test failed for $ServiceName"
        return $false
    }
    
    # Run stress test
    Write-Status "Running stress test..."
    & $k6Path run --out json="$outputDir\stress-test.json" "$K6_SCRIPTS_DIR\stress-test.js"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Stress test failed for $ServiceName"
        return $false
    }
    
    Write-Success "K6 tests completed for $ServiceName"
    return $true
}

# Function to generate comparison report
function New-ComparisonReport {
    Write-Status "Generating comparison report..."
    
    # Create results directory
    if (!(Test-Path $RESULTS_DIR)) {
        New-Item -ItemType Directory -Path $RESULTS_DIR -Force | Out-Null
    }
    
    # Generate report
    $reportContent = @"
# Benchmark Comparison Report

## Performance Tests (K6)

### Smoke Test Results
- **.NET**: See ``$RESULTS_DIR\dotnet\smoke-test.json``
- **Python**: See ``$RESULTS_DIR\python\smoke-test.json``

### Load Test Results
- **.NET**: See ``$RESULTS_DIR\dotnet\load-test.json``
- **Python**: See ``$RESULTS_DIR\python\load-test.json``

### Stress Test Results
- **.NET**: See ``$RESULTS_DIR\dotnet\stress-test.json``
- **Python**: See ``$RESULTS_DIR\python\stress-test.json``

## Quality Evaluation (LLM-as-a-Judge)
- **Report**: See ``$RESULTS_DIR\evaluation_report.md``
- **Raw Results**: See ``$RESULTS_DIR\evaluation_results.json``

## Summary
*Detailed analysis will be added after running all tests*

## How to Run
``````powershell
# Run all benchmarks
.\run-benchmarks.ps1 both

# Run only .NET
.\run-benchmarks.ps1 dotnet

# Run only Python
.\run-benchmarks.ps1 python
``````
"@
    
    $reportPath = "$RESULTS_DIR\benchmark-comparison.md"
    $reportContent | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Success "Comparison report generated: $reportPath"
}

# Main execution
function Main {
    Write-Status "Starting benchmark comparison: $Target"
    
    # Create results directory
    if (!(Test-Path $RESULTS_DIR)) {
        New-Item -ItemType Directory -Path $RESULTS_DIR -Force | Out-Null
    }
    
    $dotnetAvailable = $false
    $pythonAvailable = $false
    
    switch ($Target) {
        "dotnet" {
            if (Test-Service -Url $DOTNET_URL -ServiceName ".NET API") {
                $dotnetAvailable = $true
                if (!(Invoke-K6Tests -ServiceUrl $DOTNET_URL -ServiceName "dotnet")) {
                    Write-Error "Failed to run .NET benchmarks"
                    exit 1
                }
            } else {
                Write-Error "Cannot run benchmarks - .NET API not available"
                exit 1
            }
        }
        "python" {
            if (Test-Service -Url $PYTHON_URL -ServiceName "Python API") {
                $pythonAvailable = $true
                if (!(Invoke-K6Tests -ServiceUrl $PYTHON_URL -ServiceName "python")) {
                    Write-Error "Failed to run Python benchmarks"
                    exit 1
                }
            } else {
                Write-Error "Cannot run benchmarks - Python API not available"
                exit 1
            }
        }
        "both" {
            # Check both services
            if (Test-Service -Url $DOTNET_URL -ServiceName ".NET API") {
                $dotnetAvailable = $true
            }
            
            if (Test-Service -Url $PYTHON_URL -ServiceName "Python API") {
                $pythonAvailable = $true
            }
            
            # Run performance tests
            if ($dotnetAvailable) {
                if (!(Invoke-K6Tests -ServiceUrl $DOTNET_URL -ServiceName "dotnet")) {
                    Write-Error "Failed to run .NET benchmarks"
                    exit 1
                }
            }
            
            if ($pythonAvailable) {
                if (!(Invoke-K6Tests -ServiceUrl $PYTHON_URL -ServiceName "python")) {
                    Write-Error "Failed to run Python benchmarks"
                    exit 1
                }
            }
        }
    }
    
    # Generate comparison report
    New-ComparisonReport
    
    Write-Success "Benchmark comparison completed!"
    Write-Status "Results available in: $RESULTS_DIR"
    
    # Show summary
    if (Test-Path "$RESULTS_DIR\benchmark-comparison.md") {
        Write-Status "Open the report: $RESULTS_DIR\benchmark-comparison.md"
    }
}

# Run main function
try {
    Main
}
catch {
    Write-Error "Benchmark execution failed: $($_.Exception.Message)"
    exit 1
}
