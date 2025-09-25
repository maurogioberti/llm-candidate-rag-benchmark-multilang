from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple
import yaml

CONFIG_PATH = Path("config/common.yaml")
FILE_ENCODING = "utf-8"

CONFIG_EMBEDDINGS_SERVICE = "embeddings_service"
CONFIG_DATA = "data"
CONFIG_VECTOR_STORAGE = "vector_storage"
CONFIG_QDRANT = "qdrant"

CONFIG_HOST = "host"
CONFIG_PORT = "port"
CONFIG_URL = "url"
CONFIG_INSTRUCTION_FILE = "instruction_file"

CONFIG_DATA_ROOT = "root"
CONFIG_DATA_INPUT = "input"
CONFIG_DATA_EMBEDDINGS_INSTRUCTIONS = "embeddings_instructions"

CONFIG_TYPE = "type"

CONFIG_QDRANT_URL = "url"

EMPTY_STRING = ""
URL_SEPARATOR = "/"


class AppConfig:

    def __init__(self, config_path: Path | str | None = None):
        self._config_path = Path(config_path) if config_path else CONFIG_PATH
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self._config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self._config_path}")
        with self._config_path.open("r", encoding=FILE_ENCODING) as fh:
            full = yaml.safe_load(fh)
        if not full:
            raise ValueError(f"Configuration file is empty: {self._config_path}")
        self._config = full

    @property
    def raw(self) -> Dict[str, Any]:
        return self._config

    def get_embeddings_base_url(self) -> str:
        svc = self._config[CONFIG_EMBEDDINGS_SERVICE]
        url = svc.get(CONFIG_URL, EMPTY_STRING).strip()
        if url:
            return url.rstrip(URL_SEPARATOR)
        host = svc[CONFIG_HOST].strip()
        port = int(svc[CONFIG_PORT])
        return f"http://{host}:{port}"

    def get_embeddings_host_port(self) -> Tuple[str, int]:
        svc = self._config[CONFIG_EMBEDDINGS_SERVICE]
        host = str(svc[CONFIG_HOST])
        port = int(svc[CONFIG_PORT])
        return host, port

    def get_instruction_file_path(self, filename: str | None = None) -> Path:
        data = self._config[CONFIG_DATA]
        root = Path(data[CONFIG_DATA_ROOT])
        subdir = data[CONFIG_DATA_EMBEDDINGS_INSTRUCTIONS]
        if filename:
            return (root / subdir / filename).resolve()
        svc = self._config[CONFIG_EMBEDDINGS_SERVICE]
        instruction_file = svc[CONFIG_INSTRUCTION_FILE]
        return (root / subdir / instruction_file).resolve()

    def get_data_root(self) -> Path:
        data = self._config[CONFIG_DATA]
        return Path(data[CONFIG_DATA_ROOT]).resolve()

    def get_input_dir(self) -> Path:
        data = self._config[CONFIG_DATA]
        return (self.get_data_root() / data[CONFIG_DATA_INPUT]).resolve()

    def get_vector_storage_type(self) -> str:
        vs = self._config[CONFIG_VECTOR_STORAGE]
        return str(vs[CONFIG_TYPE]).strip().lower()

    def get_qdrant_url(self) -> str:
        qd = self._config[CONFIG_QDRANT]
        return str(qd[CONFIG_QDRANT_URL]).rstrip(URL_SEPARATOR)


_APP_CONFIG: AppConfig | None = None


def get_config() -> AppConfig:
    global _APP_CONFIG
    if _APP_CONFIG is None:
        _APP_CONFIG = AppConfig()
    return _APP_CONFIG