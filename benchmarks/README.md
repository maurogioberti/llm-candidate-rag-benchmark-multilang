# Benchmark Suite: .NET vs Python Chatbot Comparison

This benchmark suite compares performance and quality of two chatbot implementations for CV processing: .NET with Semantic Kernel vs Python with LangChain.

## Structure

```
benchmarks/
├── evaluator/                   # LLM Judge Evaluator module
│   ├── config.py               # Configuration management
│   ├── http_client.py          # HTTP communication
│   ├── judge.py                # Core evaluation logic
│   ├── scoring.py              # Scoring strategies
│   └── README.md               # Detailed evaluator documentation
├── k6/                          # K6 scripts for performance testing
│   ├── smoke-test.js           # Basic functionality test
│   ├── load-test.js            # Load test
│   └── stress-test.js          # Stress test
├── quality-prompts.json        # HR prompts for quality evaluation
├── llm-judge-evaluator.py      # Legacy evaluator (deprecated - use run_evaluation.py)
├── run_evaluation.py           # New: Entry point for evaluator
├── run-benchmarks.ps1          # PowerShell script for Windows
├── run-benchmarks.sh           # Bash script for Linux/macOS
└── results/                    # Benchmark results
```

## Prerequisites

### K6 (Performance Testing)
```bash
# Windows (PowerShell)
winget install k6

# macOS
brew install k6

# Linux
sudo apt-get install k6
```

### Python Dependencies
```bash
pip install aiohttp asyncio
```

## Usage

### Windows (PowerShell)
```powershell
# Run all benchmarks
.\benchmarks\run-benchmarks.ps1 both

# Run only .NET
.\benchmarks\run-benchmarks.ps1 dotnet

# Run only Python
.\benchmarks\run-benchmarks.ps1 python
```

### Linux/macOS (Bash)
```bash
# Run all benchmarks
./benchmarks/run-benchmarks.sh both

# Run only .NET
./benchmarks/run-benchmarks.sh dotnet

# Run only Python
./benchmarks/run-benchmarks.sh python
```

### Quality Evaluation

```bash
# From benchmarks/ directory
python run_evaluation.py

# With custom judge provider
export JUDGE_PROVIDER=openai
export OPENAI_API_KEY=your_key_here
python run_evaluation.py
```

See [`evaluator/README.md`](evaluator/README.md) for detailed documentation.

## Performance Tests (K6)

### Smoke Test
- **Goal**: Verify basic functionality
- **Config**: 1 user, 30 seconds
- **Metrics**: p95 < 500ms, error rate < 1%

### Load Test
- **Goal**: Performance under normal load
- **Config**: 10-20 users, 14 minutes
- **Metrics**: p95 < 1s, error rate < 5%, throughput > 10 req/s

### Stress Test
- **Goal**: Find breaking point
- **Config**: 10-100 users, 21 minutes
- **Metrics**: p95 < 2s, error rate < 10%

## Quality Evaluation (LLM-as-a-Judge)

### HR Prompts
- Senior candidate selection
- Experience and skills filtering
- Diversity analysis
- Certification evaluation

### Evaluation Criteria
1. **Accuracy**: Is the response accurate and relevant?
2. **Completeness**: Does it include all expected criteria?
3. **Clarity**: Is it clear and easy to understand?
4. **Actionability**: Does it provide actionable information?
5. **Ranking Quality**: Is the ordering logical?

### Scoring Scale
- **0-2**: Very poor
- **3-4**: Poor
- **5-6**: Acceptable
- **7-8**: Good
- **9-10**: Excellent

## Expected Results

### Performance
- **.NET**: Higher speed and stability
- **Python**: More flexibility in responses

### Quality
- **.NET**: More concise and factual responses
- **Python**: Richer and more detailed explanations

## Results Interpretation

### Performance Metrics
- **p95 Latency**: Response time for 95% of requests
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests

### Quality Metrics
- **Average Score**: Mean score per stack
- **Win Rate**: Percentage of victories per stack
- **Judge Comments**: Detailed analysis of each response

## Customization

### Add new prompts
Edit `quality-prompts.json` to add new HR use cases.

### Modify K6 tests
Adjust scripts in `k6/` to change load configurations.

### Configure URLs
Modify URLs in `run-benchmarks.sh` according to your setup.

## Troubleshooting

### Error: "Service not running"
- Check that APIs are running
- .NET: `http://localhost:5000`
- Python: `http://localhost:8000`

### Error: "K6 not found"
- Install K6 following instructions above
- Verify it's in PATH

### Error: "Python dependencies missing"
```bash
pip install -r requirements.txt
```
