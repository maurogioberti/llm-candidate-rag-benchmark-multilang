from .qdrant_rest import QdrantREST
from .build_index_qdrant import ensure_and_upsert

DEFAULT_COLLECTION = "candidates"
DEFAULT_SIZE = 384
DEFAULT_DISTANCE = "Cosine"
CANDIDATE_ID_KEY = "candidate_id"
DOC_PREFIX = "doc_"


def index_documents_with_qdrant(
    docs: list,
    emb,
    qdrant: QdrantREST,
    collection: str = DEFAULT_COLLECTION,
    size: int = DEFAULT_SIZE,
    distance: str = DEFAULT_DISTANCE,
) -> int:
    items = []
    for i, doc in enumerate(docs):
        vec = emb.embed_query(doc.page_content)
        pid = doc.metadata.get(CANDIDATE_ID_KEY) or f"{DOC_PREFIX}{i}"
        items.append((pid, vec, doc.page_content, doc.metadata))
    return ensure_and_upsert(qdrant, collection, size, distance, items)
