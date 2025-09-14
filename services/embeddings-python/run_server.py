"""
Embedding Server Launcher
Starts the HTTP embedding server using config/common.yaml
"""
import uvicorn
from .embedding_server import app
from .config_loader import load_config, get_embedding_host_port

if __name__ == "__main__":
    cfg = load_config()
    host, port = get_embedding_host_port(cfg)
    uvicorn.run(app, host=host, port=port)