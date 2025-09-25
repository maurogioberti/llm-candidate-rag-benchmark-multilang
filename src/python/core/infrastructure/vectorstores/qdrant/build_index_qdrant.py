from typing import Dict, Iterable, List, Tuple, Any
from .qdrant_rest import QdrantREST


def ensure_and_upsert(
    qdrant: QdrantREST,
    collection: str,
    size: int,
    distance: str,
    items: Iterable[Tuple[str, List[float], str, Dict[str, Any]]],
) -> int:
    qdrant.ensure_collection(collection, size=size, distance=distance)
    qdrant.upsert_points(collection, items)
    return qdrant.count(collection)
