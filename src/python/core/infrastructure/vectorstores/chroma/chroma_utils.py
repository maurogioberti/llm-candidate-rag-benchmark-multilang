from ...embeddings.huggingface.embedding_client import load_embeddings
from ...vector_store import chroma_from_documents, chroma_from_existing


def index_documents_with_chroma(docs: list) -> dict:
    emb = load_embeddings()
    vectorstore = chroma_from_documents(docs, emb)
    return {
        "chunks": len(docs),
        "vectorstore": vectorstore
    }


def load_existing_chroma():
    emb = load_embeddings()
    return chroma_from_existing(emb)
