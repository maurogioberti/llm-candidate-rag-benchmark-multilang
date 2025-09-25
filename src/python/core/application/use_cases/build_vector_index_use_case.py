import json
from pathlib import Path
from typing import List
from langchain_core.documents import Document

from ...domain.entities.candidate_record import CandidateRecord
from ...infrastructure.embeddings.huggingface.embedding_client import load_embeddings
from ...infrastructure.embeddings.http_embeddings_client import HttpEmbeddingsClient
from ...infrastructure.llm.llm import load_llm_instruction_records
from ...infrastructure.shared.vector_provider_factory import VectorProviderFactory
from ...infrastructure.shared.config_loader import get_config
from ..services.candidate_factory import CandidateFactory

INPUT_SUBDIR = "input"
EMBEDDING_INSTRUCTION_FILE = "embedings.jsonl"
LLM_INSTRUCTION_FILE = "llm.jsonl"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 60
ENGLISH_LEVEL_MAP = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
FIELD_INSTRUCTION = "instruction"
FIELD_INPUT = "input"
FIELD_OUTPUT = "output"
FIELD_ROW_ID = "_row_id"
LLM_PREFIX = "[LLMInstruction]"
UNKNOWN_VALUE = "unknown"
TYPE_KEY = "type"
TYPE_CANDIDATE = "candidate"
TYPE_LLM_INSTRUCTION = "llm_instruction"
CANDIDATE_ID_KEY = "candidate_id"
ENGLISH_LEVEL_KEY = "english_level"
ENGLISH_LEVEL_NUM_KEY = "english_level_num"
SUMMARY_PREFIX = "Summary: "
STRENGTHS_PREFIX = "Strengths: "
AREAS_TO_IMPROVE_PREFIX = "Areas to Improve: "
SKILLS_PREFIX = "Skills: "
SKILL_LEVEL_FORMAT = " ({})"
EVIDENCE_FORMAT = ": {}"
SEMICOLON_SEPARATOR = "; "
JSON_FILE_PATTERN = "*.json"
EMPTY_STRING = ""
DEFAULT_UNKNOWN_LEVEL = "UNK"

cfg = get_config()
DATA_DIR = cfg.get_data_root()
INPUT_DIR = cfg.get_input_dir()

__all__ = ["to_documents", "load_candidate_records", "build_index", "build_index_from_records"]


def _english_to_num(level: str) -> int:
    return ENGLISH_LEVEL_MAP.get((level or DEFAULT_UNKNOWN_LEVEL).upper(), 0)


def load_candidate_records() -> list:
    return _load_candidate_records_from_dir(INPUT_DIR)


def _load_candidate_records_from_dir(input_dir: Path) -> list:
    candidate_records = []
    factory = CandidateFactory(validate_schema=True)
    
    for file_path in sorted(input_dir.glob(JSON_FILE_PATTERN)):
        try:
            candidate_record = factory.from_json_file(file_path)
            candidate_records.append(candidate_record)
        except Exception as e:
            print(f"Error loading {file_path} (schema validation failed): {e}")
            continue
            
    return candidate_records


def to_documents(records: list) -> list:
    docs = []
    for record in records:
        docs.extend(_candidate_to_documents(record))
    return _split_documents(docs)


def _candidate_to_documents(candidate: CandidateRecord) -> list:
    documents = []
    
    candidate_id = UNKNOWN_VALUE
    english_level = UNKNOWN_VALUE
    
    if candidate.GeneralInfo:
        candidate_id = candidate.GeneralInfo.CandidateId or UNKNOWN_VALUE
        english_level = candidate.GeneralInfo.EnglishLevel or UNKNOWN_VALUE
    
    text_blocks = []
    
    if candidate.Summary:
        text_blocks.append(f"{SUMMARY_PREFIX}{candidate.Summary}")
    
    if candidate.CleanedResumeText:
        text_blocks.append(candidate.CleanedResumeText)
    
    if candidate.Strengths:
        text_blocks.append(f"{STRENGTHS_PREFIX}{SEMICOLON_SEPARATOR.join(candidate.Strengths)}")
    
    if candidate.AreasToImprove:
        text_blocks.append(f"{AREAS_TO_IMPROVE_PREFIX}{SEMICOLON_SEPARATOR.join(candidate.AreasToImprove)}")
    
    if candidate.SkillMatrix:
        skills_text = []
        for skill in candidate.SkillMatrix:
            skill_desc = skill.SkillName
            if skill.SkillLevel:
                skill_desc += SKILL_LEVEL_FORMAT.format(skill.SkillLevel)
            if skill.Evidence:
                skill_desc += EVIDENCE_FORMAT.format(skill.Evidence)
            skills_text.append(skill_desc)
        text_blocks.append(f"{SKILLS_PREFIX}{SEMICOLON_SEPARATOR.join(skills_text)}")
    
    for block in text_blocks:
        if block.strip():
            documents.append(Document(
                page_content=block,
                metadata={
                    TYPE_KEY: TYPE_CANDIDATE,
                    CANDIDATE_ID_KEY: candidate_id,
                    ENGLISH_LEVEL_KEY: english_level,
                    ENGLISH_LEVEL_NUM_KEY: _english_to_num(english_level),
                }
            ))
    
    return documents


def _split_documents(documents: list) -> list:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except Exception:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(documents)


def build_index() -> dict:
    records = load_candidate_records()
    docs = to_documents(records)

    instr_path = DATA_DIR / "instructions" / EMBEDDING_INSTRUCTION_FILE
    if instr_path.exists():
        docs += _load_and_split_instruction_docs(instr_path)

    llm_instr_path = DATA_DIR / "instructions" / LLM_INSTRUCTION_FILE
    if llm_instr_path.exists():
        docs += _load_and_split_llm_instruction_docs(llm_instr_path)

    provider = VectorProviderFactory.create_provider()
    result = provider.index_documents(docs)
    
    print(f"✅ Indexed {result.get('chunks', len(docs))} documents using {provider.get_provider_name()}")
    
    return {
        "candidates": len(records), 
        "chunks": len(docs), 
        "provider": provider.get_provider_name(),
        **result
    }


def _load_and_split_instruction_docs(instr_path: Path) -> list:
    cfg = get_config()
    http_client = HttpEmbeddingsClient(base_url=cfg.get_embeddings_base_url())
    pairs = http_client.get_instruction_pairs()
    extra_docs = [Document(page_content=text, metadata=meta) for (text, meta) in pairs]
    return _split_documents(extra_docs)


def _load_and_split_llm_instruction_docs(path: Path) -> list:
    records = load_llm_instruction_records(path)
    docs = []
    for r in records:
        content = f"{LLM_PREFIX} Instruction: {r.get(FIELD_INSTRUCTION, EMPTY_STRING)}\nInput:\n{json.dumps(r.get(FIELD_INPUT, EMPTY_STRING), ensure_ascii=False)}\nOutput:\n{json.dumps(r.get(FIELD_OUTPUT, EMPTY_STRING), ensure_ascii=False)}"
        meta = {TYPE_KEY: TYPE_LLM_INSTRUCTION, FIELD_ROW_ID: r.get(FIELD_ROW_ID)}
        docs.append(Document(page_content=content, metadata=meta))
    return _split_documents(docs)


def build_index_from_records(records: list):
    docs = to_documents(records)
    
    provider = VectorProviderFactory.create_provider()
    result = provider.index_documents(docs)
    
    return {
        "candidates": len(records), 
        "chunks": len(docs), 
        "provider": provider.get_provider_name(),
        **result
    }
