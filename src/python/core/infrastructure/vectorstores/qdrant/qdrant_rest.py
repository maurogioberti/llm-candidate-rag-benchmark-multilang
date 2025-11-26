import json
from typing import Any, Dict, Iterable, List, Optional, Tuple
import httpx
from ...shared.config_loader import get_config

DEFAULT_SIZE = 384
DEFAULT_DISTANCE = "Cosine"
DEFAULT_TIMEOUT = 60.0
DEFAULT_LIMIT = 6
DEFAULT_HNSW_EF = 128
DEFAULT_HNSW_M = 16
COLLECTION_ENDPOINT = "/collections"
POINTS_ENDPOINT = "/points"
SEARCH_ENDPOINT = "/search"
EXTERNAL_ID_KEY = "external_id"
VECTOR_KEY = "vector"
PAYLOAD_KEY = "payload"
POINTS_KEY = "points"
RESULT_KEY = "result"
POINTS_COUNT_KEY = "points_count"
MAX_COUNT = 2**31 - 1


class QdrantREST:
    def __init__(self, base_url: Optional[str] = None, client: Optional[httpx.Client] = None):
        cfg = get_config()
        default_url = cfg.get_qdrant_url()
        self.base_url = (base_url or default_url).rstrip("/")
        self.http = client or httpx.Client(base_url=self.base_url, timeout=DEFAULT_TIMEOUT)

    def ensure_collection(self, name: str, size: int = DEFAULT_SIZE, distance: str = DEFAULT_DISTANCE) -> None:
        r = self.http.get(f"{COLLECTION_ENDPOINT}/{name}")
        if r.status_code == 200:
            return
        if r.status_code != 404:
            r.raise_for_status()
        payload = {
            "vectors": {
                "size": size,
                "distance": distance,
                "hnsw_config": {
                    "m": DEFAULT_HNSW_M,
                    "ef_construct": DEFAULT_HNSW_EF
                }
            }
        }
        r = self.http.put(f"{COLLECTION_ENDPOINT}/{name}", json=payload)
        r.raise_for_status()

    def upsert_points(
        self,
        collection: str,
        points: Iterable[Tuple[str, List[float], str, Dict[str, Any]]],
        determinist_uuid=True,
    ) -> None:
        def to_uuid_deterministic(s: str) -> str:
            import hashlib, uuid
            h = hashlib.md5(s.encode("utf-8")).digest()
            return str(uuid.UUID(bytes=h))

        mapped = []
        for (pid, vec, document, metadata) in points:
            qid = pid
            try:
                import uuid
                uuid.UUID(pid)
            except Exception:
                if determinist_uuid:
                    qid = to_uuid_deterministic(pid)
                else:
                    qid = None
                    metadata = dict(metadata or {})
                    metadata[EXTERNAL_ID_KEY] = pid

            payload = {"document": document}
            if metadata:
                payload.update(metadata)

            mapped.append({"id": qid, VECTOR_KEY: vec, PAYLOAD_KEY: payload} if qid else
                          {VECTOR_KEY: vec, PAYLOAD_KEY: payload})

        body = {POINTS_KEY: mapped}
        r = self.http.put(f"{COLLECTION_ENDPOINT}/{collection}{POINTS_ENDPOINT}", json=body)
        if r.status_code >= 400:
            raise RuntimeError(f"Qdrant upsert error: {r.status_code} {r.text}")

    def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = DEFAULT_LIMIT,
        qfilter: Optional[Dict[str, Any]] = None,
        with_payload: bool = True,
        with_vector: bool = False,
    ):
        body = {
            VECTOR_KEY: query_vector,
            "limit": limit,
            "with_payload": with_payload,
            "with_vector": with_vector,
            "params": {
                "hnsw_ef": DEFAULT_HNSW_EF
            }
        }
        if qfilter:
            body["filter"] = qfilter
        
        # Diagnostic logging for benchmarking
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[QDRANT_SEARCH] Collection: {collection}, Limit: {limit}, Filter: {qfilter}")
        
        r = self.http.post(f"{COLLECTION_ENDPOINT}/{collection}{POINTS_ENDPOINT}{SEARCH_ENDPOINT}", json=body)
        if r.status_code >= 400:
            raise RuntimeError(f"Qdrant search error: {r.status_code} {r.text}")
        data = r.json()
        results = data.get(RESULT_KEY, [])
        
        # Diagnostic logging for benchmarking
        if results:
            logger.info(f"[QDRANT_RESULTS] Count: {len(results)}, Top score: {results[0].get('score', 0):.4f}")
            for idx, result in enumerate(results[:3]):  # Log top 3
                logger.info(f"[QDRANT_RESULT_{idx}] ID: {result.get('id')}, Score: {result.get('score', 0):.4f}")
        
        return results

    def count(self, collection: str) -> int:
        r = self.http.get(f"{COLLECTION_ENDPOINT}/{collection}")
        r.raise_for_status()
        info = r.json()[RESULT_KEY]
        return min(info.get(POINTS_COUNT_KEY, 0), MAX_COUNT)
