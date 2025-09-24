import sys
from core.infrastructure.shared.config_loader import get_config

MODE_SERVE = "serve"
DEFAULT_PORT = 8000
DEFAULT_RELOAD = True
CONFIG_PYTHON_API = "python_api"
CONFIG_PORT = "port"
ENV_PORT = "PORT"
ENV_RELOAD = "RELOAD"
ENV_APP_MODE = "APP_MODE"


def _build_index() -> None:
    from core.application.use_cases.build_vector_index_use_case import build_index
    info = build_index()
    print(f"[INDEX] {info}")


def _serve() -> None:
    import uvicorn
    cfg = get_config()
    
    port = int(cfg.raw.get(CONFIG_PYTHON_API, {}).get(CONFIG_PORT, DEFAULT_PORT))
    reload_enabled = DEFAULT_RELOAD
    
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=reload_enabled)


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    mode = (argv[0].lower() if argv else "")
    if mode == MODE_SERVE:
        _serve()
        return 0
    _build_index()
    _serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())