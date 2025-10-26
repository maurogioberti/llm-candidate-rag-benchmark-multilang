from pathlib import Path
from typing import List, Tuple, Dict, Any
import json

FILE_ENCODING = "utf-8"
FIELD_QUERY = "query"
FIELD_POSITIVE = "positive"
FIELD_NEGATIVE = "negative"
FIELD_TYPE = "type"
FIELD_PAIR_ID = "pair_id"
FIELD_QUERY_REF = "query"
TYPE_QUERY = "query"
TYPE_POSITIVE = "positive"
TYPE_NEGATIVE = "negative"


def load_instruction_pairs(path: str | Path) -> List[Tuple[str, Dict[str, Any]]]:
    p = Path(path)
    if not p.exists():
        return []
    out: List[Tuple[str, Dict[str, Any]]] = []
    for i, line in enumerate(p.read_text(encoding=FILE_ENCODING).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        q = rec.get(FIELD_QUERY)
        pos = rec.get(FIELD_POSITIVE)
        neg = rec.get(FIELD_NEGATIVE)
        if q:
            out.append((q, {FIELD_TYPE: TYPE_QUERY, FIELD_PAIR_ID: i}))
        if pos:
            out.append((pos, {FIELD_TYPE: TYPE_POSITIVE, FIELD_PAIR_ID: i, FIELD_QUERY_REF: q}))
        if neg:
            out.append((neg, {FIELD_TYPE: TYPE_NEGATIVE, FIELD_PAIR_ID: i, FIELD_QUERY_REF: q}))
    return out