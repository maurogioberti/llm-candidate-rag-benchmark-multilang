
import uvicorn
from services.embeddings_python.embeddings_api import app
from services.embeddings_python.config_loader import load_config, get_embedding_host_port


if __name__ == "__main__":
    cfg = load_config()
    host, port = get_embedding_host_port(cfg)
    uvicorn.run(app, host=host, port=port)