#!/bin/bash

# Benchmark runner script for .NET vs Python chatbot comparison
# Usage: ./run-benchmarks.sh [dotnet|python|both]

set -e

# Configuration
DOTNET_URL="http://localhost:5000"
PYTHON_URL="http://localhost:8000"
RESULTS_DIR="benchmarks/results"
K6_SCRIPTS_DIR="benchmarks/k6"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    
    print_status "Checking if $service_name is running at $url..."
    
    if curl -s -f "$url/health" > /dev/null 2>&1; then
        print_success "$service_name is running"
        return 0
    else
        print_error "$service_name is not running at $url"
        return 1
    fi
}

# Function to run K6 performance tests
run_k6_tests() {
    local service_url=$1
    local service_name=$2
    local output_dir="$RESULTS_DIR/$service_name"
    
    print_status "Running K6 performance tests for $service_name..."
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Run smoke test
    print_status "Running smoke test..."
    k6 run --env BASE_URL="$service_url" "$K6_SCRIPTS_DIR/smoke-test.js" --out json="$output_dir/smoke-test.json"
    
    # Run load test
    print_status "Running load test..."
    k6 run --env BASE_URL="$service_url" "$K6_SCRIPTS_DIR/load-test.js" --out json="$output_dir/load-test.json"
    
    # Run stress test
    print_status "Running stress test..."
    k6 run --env BASE_URL="$service_url" "$K6_SCRIPTS_DIR/stress-test.js" --out json="$output_dir/stress-test.json"
    
    print_success "K6 tests completed for $service_name"
}

# Function to generate comparison report
generate_comparison_report() {
    print_status "Generating comparison report..."
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    # Generate report (placeholder for now)
    cat > "$RESULTS_DIR/benchmark-comparison.md" << EOF
# Benchmark Comparison Report

## Performance Tests (K6)

### Smoke Test Results
- **.NET**: See \`$RESULTS_DIR/dotnet/smoke-test.json\`
- **Python**: See \`$RESULTS_DIR/python/smoke-test.json\`

### Load Test Results
- **.NET**: See \`$RESULTS_DIR/dotnet/load-test.json\`
- **Python**: See \`$RESULTS_DIR/python/load-test.json\`

### Stress Test Results
- **.NET**: See \`$RESULTS_DIR/dotnet/stress-test.json\`
- **Python**: See \`$RESULTS_DIR/python/stress-test.json\`

## Quality Evaluation (LLM-as-a-Judge)
- **Report**: See \`$RESULTS_DIR/evaluation_report.md\`
- **Raw Results**: See \`$RESULTS_DIR/evaluation_results.json\`

## Summary
*Detailed analysis will be added after running all tests*
EOF
    
    print_success "Comparison report generated"
}

# Main execution
main() {
    local target=${1:-"both"}
    
    print_status "Starting benchmark comparison: $target"
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"
    
    case $target in
        "dotnet")
            if check_service "$DOTNET_URL" ".NET API"; then
                run_k6_tests "$DOTNET_URL" "dotnet"
            else
                print_error "Cannot run benchmarks - .NET API not available"
                exit 1
            fi
            ;;
        "python")
            if check_service "$PYTHON_URL" "Python API"; then
                run_k6_tests "$PYTHON_URL" "python"
            else
                print_error "Cannot run benchmarks - Python API not available"
                exit 1
            fi
            ;;
        "both")
            # Check both services
            dotnet_available=false
            python_available=false
            
            if check_service "$DOTNET_URL" ".NET API"; then
                dotnet_available=true
            fi
            
            if check_service "$PYTHON_URL" "Python API"; then
                python_available=true
            fi
            
            if [ "$dotnet_available" = true ]; then
                run_k6_tests "$DOTNET_URL" "dotnet"
            fi
            
            if [ "$python_available" = true ]; then
                run_k6_tests "$PYTHON_URL" "python"
            fi
            ;;
        *)
            print_error "Invalid target: $target. Use 'dotnet', 'python', or 'both'"
            exit 1
            ;;
    esac
    
    # Generate comparison report
    generate_comparison_report
    
    print_success "Benchmark comparison completed!"
    print_status "Results available in: $RESULTS_DIR"
}

# Run main function
main "$@"
