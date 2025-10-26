from fastapi import FastAPI, Query
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

from .embeddings_utils import load_instruction_pairs
from .config_loader import load_config, get_instruction_file

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_DEVICE = "cpu"
ENDPOINT_EMBED = "/embed"
ENDPOINT_INSTRUCTION_PAIRS = "/instruction-pairs"
RESPONSE_VECTORS_KEY = "vectors"
RESPONSE_PAIRS_KEY = "pairs"
RESPONSE_TEXT_KEY = "text"
RESPONSE_METADATA_KEY = "metadata"
QUERY_PARAM_DESCRIPTION = "Full path or filename (.jsonl) within Data.EmbInstructions directory"


app = FastAPI()

CFG = load_config()

emb = HuggingFaceEmbeddings(
    model_name=DEFAULT_MODEL_NAME,
    model_kwargs={"device": DEFAULT_DEVICE},
    encode_kwargs={"normalize_embeddings": True}
)


class Req(BaseModel):
    texts: list[str]


@app.post(ENDPOINT_EMBED)
def embed(r: Req):
    vectors = emb.embed_documents(r.texts)
    return {RESPONSE_VECTORS_KEY: vectors}


@app.get(ENDPOINT_INSTRUCTION_PAIRS)
def instruction_pairs(path: str | None = Query(default=None, description=QUERY_PARAM_DESCRIPTION)):
    p = Path(path) if path else get_instruction_file(CFG)
    pairs = load_instruction_pairs(p)
    return {RESPONSE_PAIRS_KEY: [{RESPONSE_TEXT_KEY: t, RESPONSE_METADATA_KEY: m} for t, m in pairs]}