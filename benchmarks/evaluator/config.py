import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import yaml


CONFIG_COMMON_PATH = Path("config/common.yaml")
CONFIG_EVAL_PATH = Path("config/evaluation.yaml")
FILE_ENCODING = "utf-8"

DEFAULT_DOTNET_URL = "http://localhost:5000"
DEFAULT_PYTHON_PORT = 8000
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_JUDGE_PROVIDER = "ollama"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_JUDGE_RUNS = 3
DEFAULT_TEMPERATURE = 0.0
DEFAULT_TIE_TOLERANCE = 0.01
DEFAULT_HEURISTIC_TIE_TOLERANCE = 0.25
DEFAULT_OPENAI_TIMEOUT = 60.0
DEFAULT_OLLAMA_TIMEOUT = 120.0
DEFAULT_MIN_SUCCESSFUL_RUNS = 1


@dataclass
class EvaluatorConfig:
    dotnet_url: str
    python_url: str
    judge_provider: str
    openai_model: str
    openai_api_key: Optional[str]
    ollama_host: str
    ollama_model: str
    judge_runs: int = DEFAULT_JUDGE_RUNS
    temperature: float = DEFAULT_TEMPERATURE
    tie_tolerance: float = DEFAULT_TIE_TOLERANCE
    heuristic_tie_tolerance: float = DEFAULT_HEURISTIC_TIE_TOLERANCE
    openai_timeout: float = DEFAULT_OPENAI_TIMEOUT
    ollama_timeout: float = DEFAULT_OLLAMA_TIMEOUT
    min_successful_runs: int = DEFAULT_MIN_SUCCESSFUL_RUNS
    
    @classmethod
    def from_yaml(cls, common_path: Path = CONFIG_COMMON_PATH, eval_path: Path = CONFIG_EVAL_PATH) -> "EvaluatorConfig":
        if not common_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {common_path}")
        
        with common_path.open("r", encoding=FILE_ENCODING) as f:
            common_cfg = yaml.safe_load(f)
        
        if not common_cfg:
            raise ValueError(f"Configuration file is empty: {common_path}")
        
        eval_cfg = {}
        if eval_path.exists():
            with eval_path.open("r", encoding=FILE_ENCODING) as f:
                eval_cfg = yaml.safe_load(f) or {}
            
            if eval_cfg:
                cls._validate_eval_config(eval_cfg, eval_path)
        
        # Extract sections from common.yaml
        llm_provider_cfg = common_cfg.get("llm_provider", {})
        ollama_cfg = llm_provider_cfg.get("ollama", {})
        openai_cfg = llm_provider_cfg.get("openai", {})
        python_api_cfg = common_cfg.get("python_api", {})
        dotnet_api_cfg = common_cfg.get("dotnet_api", {})
        
        # Extract sections from evaluation.yaml
        judge_cfg = eval_cfg.get("judge", {})
        scoring_cfg = eval_cfg.get("scoring", {})
        timeouts_cfg = eval_cfg.get("timeouts", {})
        failure_cfg = eval_cfg.get("failure_policy", {})
        
        # Build API URLs from common.yaml
        python_url = f"http://localhost:{python_api_cfg.get('port', DEFAULT_PYTHON_PORT)}"
        dotnet_url = dotnet_api_cfg.get("urls", DEFAULT_DOTNET_URL)
        
        # Precedence: ENV > evaluation.yaml > common.yaml > defaults
        judge_provider = (
            os.getenv("JUDGE_PROVIDER")
            or judge_cfg.get("provider")
            or llm_provider_cfg.get("provider", DEFAULT_JUDGE_PROVIDER)
        ).lower()
        
        judge_runs = max(1, int(
            os.getenv("JUDGE_RUNS")
            or judge_cfg.get("runs", DEFAULT_JUDGE_RUNS)
        ))
        
        temperature = float(judge_cfg.get("temperature", DEFAULT_TEMPERATURE))
        tie_tolerance = float(scoring_cfg.get("tie_tolerance", DEFAULT_TIE_TOLERANCE))
        heuristic_tie_tolerance = float(scoring_cfg.get("heuristic_tie_tolerance", DEFAULT_HEURISTIC_TIE_TOLERANCE))
        openai_timeout = float(timeouts_cfg.get("openai_seconds", DEFAULT_OPENAI_TIMEOUT))
        ollama_timeout = float(timeouts_cfg.get("ollama_seconds", DEFAULT_OLLAMA_TIMEOUT))
        min_successful_runs = int(failure_cfg.get("min_successful_runs", DEFAULT_MIN_SUCCESSFUL_RUNS))
        
        return cls(
            dotnet_url=dotnet_url,
            python_url=python_url,
            judge_provider=judge_provider,
            openai_model=openai_cfg.get("model", DEFAULT_OPENAI_MODEL),
            openai_api_key=openai_cfg.get("api_key") or os.getenv("OPENAI_API_KEY"),
            ollama_host=ollama_cfg.get("base_url", DEFAULT_OLLAMA_BASE_URL),
            ollama_model=llm_provider_cfg.get("model", ""),
            judge_runs=judge_runs,
            temperature=temperature,
            tie_tolerance=tie_tolerance,
            heuristic_tie_tolerance=heuristic_tie_tolerance,
            openai_timeout=openai_timeout,
            ollama_timeout=ollama_timeout,
            min_successful_runs=min_successful_runs,
        )
    
    @classmethod
    def from_environment(cls) -> "EvaluatorConfig":
        judge_runs = max(1, int(os.getenv("JUDGE_RUNS", str(DEFAULT_JUDGE_RUNS))))
        
        return cls(
            dotnet_url=os.getenv("DOTNET_URL", DEFAULT_DOTNET_URL),
            python_url=os.getenv("PYTHON_URL", f"http://localhost:{DEFAULT_PYTHON_PORT}"),
            judge_provider=os.getenv("JUDGE_PROVIDER", DEFAULT_JUDGE_PROVIDER).lower(),
            openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_host=os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_BASE_URL),
            ollama_model=os.getenv("OLLAMA_MODEL", ""),
            judge_runs=judge_runs,
            temperature=DEFAULT_TEMPERATURE,
            tie_tolerance=DEFAULT_TIE_TOLERANCE,
            heuristic_tie_tolerance=DEFAULT_HEURISTIC_TIE_TOLERANCE,
            openai_timeout=DEFAULT_OPENAI_TIMEOUT,
            ollama_timeout=DEFAULT_OLLAMA_TIMEOUT,
            min_successful_runs=DEFAULT_MIN_SUCCESSFUL_RUNS,
        )
    
    def is_openai_available(self) -> bool:
        return self.judge_provider == "openai" and self.openai_api_key is not None
    
    def is_ollama_enabled(self) -> bool:
        return self.judge_provider == "ollama"
    
    def is_heuristic_mode(self) -> bool:
        return self.judge_provider == "heuristic"
    
    @staticmethod
    def _validate_eval_config(eval_cfg: dict, eval_path: Path) -> None:
        required_sections = {
            "judge": ["provider", "runs", "temperature"],
            "scoring": ["tie_tolerance", "heuristic_tie_tolerance"],
            "timeouts": ["openai_seconds", "ollama_seconds"],
            "failure_policy": ["min_successful_runs"]
        }
        
        for section, keys in required_sections.items():
            if section not in eval_cfg:
                raise ValueError(f"Missing required section '{section}' in {eval_path}")
            
            section_cfg = eval_cfg[section]
            for key in keys:
                if key not in section_cfg:
                    raise ValueError(f"Missing required key '{section}.{key}' in {eval_path}")
    
    def validate(self) -> None:
        """Validate configuration and raise errors if invalid."""
        if self.is_ollama_enabled() and not self.ollama_model:
            raise ValueError(
                "Ollama model must be configured when using judge_provider='ollama'.\n"
                "Set 'llm_provider.model' in config/common.yaml or use environment variable OLLAMA_MODEL.\n"
                f"Example: OLLAMA_MODEL=llama3:8b or update {CONFIG_COMMON_PATH}"
            )
        
        if self.is_openai_available() and not self.openai_model:
            raise ValueError(
                "OpenAI model must be configured when using judge_provider='openai'.\n"
                "Set 'llm_provider.openai.model' in config/common.yaml or use environment variable OPENAI_MODEL."
            )
        
        if self.judge_runs < 1:
            raise ValueError(f"judge_runs must be >= 1, got: {self.judge_runs}")
        
        if self.min_successful_runs < 0:
            raise ValueError(f"min_successful_runs must be >= 0, got: {self.min_successful_runs}")
        
        if self.min_successful_runs > self.judge_runs:
            raise ValueError(
                f"min_successful_runs ({self.min_successful_runs}) cannot exceed judge_runs ({self.judge_runs})"
            )
