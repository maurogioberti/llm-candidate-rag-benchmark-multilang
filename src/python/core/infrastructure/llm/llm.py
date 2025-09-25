from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import json


LLM_INSTRUCTION_FILE = "llm.jsonl"
FILE_ENCODING = "utf-8"
FIELD_INSTRUCTION = "instruction"
FIELD_INPUT = "input"
FIELD_OUTPUT = "output"
FIELD_ROW_ID = "_row_id"

def load_llm_instruction_records(path: str | Path) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    records: List[Dict[str, Any]] = []
    for i, line in enumerate(p.read_text(encoding=FILE_ENCODING).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if FIELD_INSTRUCTION in rec and FIELD_INPUT in rec and FIELD_OUTPUT in rec:
            rec[FIELD_ROW_ID] = i
            records.append(rec)
    return records