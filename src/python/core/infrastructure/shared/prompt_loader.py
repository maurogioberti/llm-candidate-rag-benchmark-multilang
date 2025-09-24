from pathlib import Path
from .config_loader import get_config

CONFIG_DATA_ROOT = "root"
CONFIG_DATA_PROMPTS = "prompts"
PROMPT_ENCODING = "utf-8"

def load_prompt(name: str) -> str:
    cfg = get_config()
    data_root = Path(cfg.raw[CONFIG_DATA_ROOT])
    prompts_dir = cfg.raw[CONFIG_DATA_PROMPTS]
    filepath = data_root / prompts_dir / name
    if filepath.exists():
        return filepath.read_text(encoding=PROMPT_ENCODING)
