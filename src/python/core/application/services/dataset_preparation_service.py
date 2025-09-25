import json
from pathlib import Path
from ...infrastructure.llm import load_llm_instruction_records
from ...infrastructure.shared.config_loader import get_config


CONFIG_DATA_ROOT = "root"
CONFIG_DATA_INSTRUCTIONS = "instructions"
CONFIG_DATA_FINETUNING = "instructions"

LLM_INSTRUCTION_FILE = "llm.jsonl"
OPENAI_EXPORT_FILENAME = "openai_chat.jsonl"
INSTRUCT_EXPORT_FILENAME = "instruct_generic.jsonl"
FILE_ENCODING = "utf-8"
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"

def main():
    cfg = get_config()
    data_config = cfg.raw["data"]
    
    data_root = Path(data_config[CONFIG_DATA_ROOT])
    instructions_dir = data_config[CONFIG_DATA_INSTRUCTIONS]
    finetuning_dir = data_config[CONFIG_DATA_FINETUNING]
    
    source_path = data_root / instructions_dir / LLM_INSTRUCTION_FILE
    export_dir = data_root / finetuning_dir / "finetune_exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    records = load_llm_instruction_records(source_path)
    if not records:
        print(f"[WARN] No records loaded from {source_path}")
        return

    openai_path = export_dir / OPENAI_EXPORT_FILENAME
    with open(openai_path, "w", encoding=FILE_ENCODING) as f:
        for r in records:
            f.write(f"{json.dumps({
                "messages": [
                    {"role": ROLE_SYSTEM, "content": r["instruction"]},
                    {"role": ROLE_USER, "content": json.dumps(r["input"], ensure_ascii=False)},
                    {"role": ROLE_ASSISTANT, "content": json.dumps(r["output"], ensure_ascii=False)}
                ]
            }, ensure_ascii=False)}\n")

    instruct_path = export_dir / INSTRUCT_EXPORT_FILENAME
    with open(instruct_path, "w", encoding=FILE_ENCODING) as f:
        for r in records:
            f.write(f"{json.dumps({
                "instruction": r["instruction"],
                "input": r["input"],
                "output": r["output"]
            }, ensure_ascii=False)}\n")

    print(f"[OK] Loaded {len(records)} records")
    print(f"[OK] Wrote: {openai_path}")
    print(f"[OK] Wrote: {instruct_path}")

if __name__ == "__main__":
    main()
