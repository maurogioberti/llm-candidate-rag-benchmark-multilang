from pathlib import Path
import yaml

CONFIG_PATH = "config/common.yaml"
FILE_ENCODING = "utf-8"
CONFIG_EMBEDDINGS_SERVICE = "embeddings_service"
CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_INSTRUCTION_FILE = "instruction_file"
CONFIG_DATA = "data"
CONFIG_DATA_ROOT = "root"
CONFIG_EMBEDDINGS_INSTRUCTIONS = "embeddings_instructions"

def load_config() -> dict:
    cfg_path = Path(CONFIG_PATH)
    
    if not cfg_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")
    
    with cfg_path.open("r", encoding=FILE_ENCODING) as f:
        full_config = yaml.safe_load(f)
        
    if not full_config:
        raise ValueError(f"Configuration file is empty: {cfg_path}")
    
    config = {}
    if CONFIG_EMBEDDINGS_SERVICE in full_config:
        config[CONFIG_EMBEDDINGS_SERVICE] = full_config[CONFIG_EMBEDDINGS_SERVICE]
    if CONFIG_DATA in full_config:
        config[CONFIG_DATA] = full_config[CONFIG_DATA]
    
    return config

def get_embedding_host_port(cfg: dict) -> tuple[str, int]:
    svc = cfg[CONFIG_EMBEDDINGS_SERVICE]
    return str(svc[CONFIG_HOST]), int(svc[CONFIG_PORT])

def get_instruction_file(cfg: dict, filename: str | None = None) -> Path:
    if filename:
        root = Path(cfg[CONFIG_DATA][CONFIG_DATA_ROOT])
        subdir = cfg[CONFIG_DATA][CONFIG_EMBEDDINGS_INSTRUCTIONS]
        return (root / subdir / filename).resolve()
    
    root = Path(cfg[CONFIG_DATA][CONFIG_DATA_ROOT])
    subdir = cfg[CONFIG_DATA][CONFIG_EMBEDDINGS_INSTRUCTIONS]
    instruction_file = cfg[CONFIG_EMBEDDINGS_SERVICE][CONFIG_INSTRUCTION_FILE]
    return (root / subdir / instruction_file).resolve()