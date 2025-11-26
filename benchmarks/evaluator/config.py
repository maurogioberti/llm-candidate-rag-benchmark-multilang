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
        
        return cls(
            dotnet_url=dotnet_url,
            python_url=python_url,
            judge_provider=judge_provider,
            openai_model=openai_cfg.get("model", DEFAULT_OPENAI_MODEL),
            openai_api_key=openai_cfg.get("api_key") or os.getenv("OPENAI_API_KEY"),
            ollama_host=ollama_cfg.get("base_url", DEFAULT_OLLAMA_BASE_URL),
            ollama_model=llm_provider_cfg.get("model", ""),
        )
    
    @classmethod
    def from_environment(cls) -> "EvaluatorConfig":
        return cls(
            dotnet_url=os.getenv("DOTNET_URL", DEFAULT_DOTNET_URL),
            python_url=os.getenv("PYTHON_URL", f"http://localhost:{DEFAULT_PYTHON_PORT}"),
            judge_provider=os.getenv("JUDGE_PROVIDER", DEFAULT_JUDGE_PROVIDER).lower(),
            openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            ollama_host=os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_BASE_URL),
            ollama_model=os.getenv("OLLAMA_MODEL", ""),
        )
    
    def is_openai_available(self) -> bool:
        return self.judge_provider == "openai" and self.openai_api_key is not None
    
    def is_ollama_enabled(self) -> bool:
        return self.judge_provider == "ollama"
    
    def is_heuristic_mode(self) -> bool:
        return self.judge_provider == "heuristic"
