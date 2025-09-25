from pathlib import Path
from .config_loader import get_config

CONFIG_DATA_ROOT = "root"
CONFIG_DATA_PROMPTS = "prompts"
PROMPT_ENCODING = "utf-8"

def load_prompt(name: str) -> str:
    cfg = get_config()
    data_config = cfg.raw["data"]
    data_root = Path(data_config["root"])
    prompts_dir = data_config["prompts"]
    filepath = data_root / prompts_dir / name
    
    if filepath.exists():
        try:
            content = filepath.read_text(encoding=PROMPT_ENCODING)
            return content
        except Exception as e:
            raise
    else:
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
