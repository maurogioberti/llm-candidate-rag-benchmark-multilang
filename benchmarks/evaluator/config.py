import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import yaml


CONFIG_FILE_PATH = "config/common.yaml"
DEFAULT_DOTNET_URL = "http://localhost:5000"
DEFAULT_PYTHON_PORT = 8000
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_JUDGE_PROVIDER = "ollama"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


@dataclass
class EvaluatorConfig:
    dotnet_url: str
    python_url: str
    judge_provider: str
    openai_model: str
    openai_api_key: Optional[str]
    ollama_host: str
    ollama_model: str
    judge_runs: int = 1
    
    @classmethod
    def from_yaml(cls, config_path: str = CONFIG_FILE_PATH) -> "EvaluatorConfig":
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        if not config:
            raise ValueError(f"Configuration file is empty: {path}")
        
        llm_provider_cfg = config.get("llm_provider", {})
        ollama_cfg = llm_provider_cfg.get("ollama", {})
        openai_cfg = llm_provider_cfg.get("openai", {})
        
        python_api_cfg = config.get("python_api", {})
        dotnet_api_cfg = config.get("dotnet_api", {})
        
        python_url = f"http://localhost:{python_api_cfg.get('port', DEFAULT_PYTHON_PORT)}"
        dotnet_url = dotnet_api_cfg.get("urls", DEFAULT_DOTNET_URL)
        
        judge_provider = llm_provider_cfg.get("provider", DEFAULT_JUDGE_PROVIDER)
        judge_runs = max(1, int(os.getenv("JUDGE_RUNS", "1")))
        
        return cls(
            dotnet_url=dotnet_url,
            python_url=python_url,
            judge_provider=judge_provider,
            openai_model=openai_cfg.get("model", DEFAULT_OPENAI_MODEL),
            openai_api_key=openai_cfg.get("api_key") or os.getenv("OPENAI_API_KEY"),
            ollama_host=ollama_cfg.get("base_url", DEFAULT_OLLAMA_BASE_URL),
            ollama_model=llm_provider_cfg.get("model", ""),
            judge_runs=judge_runs,
        )
    
    @classmethod
    def from_environment(cls) -> "EvaluatorConfig":
        judge_runs = max(1, int(os.getenv("JUDGE_RUNS", "1")))
        
        return cls(
            dotnet_url=os.getenv("DOTNET_URL", DEFAULT_DOTNET_URL),
            python_url=os.getenv("PYTHON_URL", f"http://localhost:{DEFAULT_PYTHON_PORT}"),
            judge_provider=os.getenv("JUDGE_PROVIDER", DEFAULT_JUDGE_PROVIDER).lower(),
            openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_host=os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_BASE_URL),
            ollama_model=os.getenv("OLLAMA_MODEL", ""),
            judge_runs=judge_runs,
        )
    
    def is_openai_available(self) -> bool:
        return self.judge_provider == "openai" and self.openai_api_key is not None
    
    def is_ollama_enabled(self) -> bool:
        return self.judge_provider == "ollama"
    
    def is_heuristic_mode(self) -> bool:
        return self.judge_provider == "heuristic"
    
    def validate(self) -> None:
        """Validate configuration and raise errors if invalid."""
        if self.is_ollama_enabled() and not self.ollama_model:
            raise ValueError(
                "Ollama model must be configured when using judge_provider='ollama'.\n"
                "Set 'llm_provider.model' in config/common.yaml or use environment variable OLLAMA_MODEL.\n"
                f"Example: OLLAMA_MODEL=llama3:8b or update {CONFIG_FILE_PATH}"
            )
        
        if self.is_openai_available() and not self.openai_model:
            raise ValueError(
                "OpenAI model must be configured when using judge_provider='openai'.\n"
                "Set 'llm_provider.openai.model' in config/common.yaml or use environment variable OPENAI_MODEL."
            )
        
        if self.judge_runs < 1:
            raise ValueError(f"judge_runs must be >= 1, got: {self.judge_runs}")
