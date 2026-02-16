"""Pure utility for cleaning and extracting JSON from raw LLM output."""

import re

NO_JSON_FOUND_MESSAGE = "No JSON object found in LLM output"


def extract_json(raw_output: str) -> str:
    """
    Cleans raw LLM output and extracts the outermost JSON object as a string.
    
    Handles:
    - Markdown code fences (```json ... ```)
    - <think>...</think> blocks (DeepSeek-R1)
    - Preamble/postamble text
    
    Args:
        raw_output: Raw text from LLM
        
    Returns:
        Extracted JSON string
        
    Raises:
        ValueError: If no valid JSON object found
    """
    if not raw_output or not raw_output.strip():
        raise ValueError(NO_JSON_FOUND_MESSAGE)
    
    cleaned = strip_thinking_blocks(raw_output)
    cleaned = strip_markdown_fences(cleaned)
    
    return extract_outermost_json_object(cleaned)


def strip_thinking_blocks(text: str) -> str:
    """Remove <think>...</think> blocks (e.g. DeepSeek-R1 reasoning)."""
    return re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE).strip()


def strip_markdown_fences(text: str) -> str:
    """Remove markdown code fences: ```json ... ``` or ``` ... ```."""
    return re.sub(r'```(?:json)?\s*\n?([\s\S]*?)\n?\s*```', r'\1', text).strip()


def extract_outermost_json_object(text: str) -> str:
    """
    Extract the outermost balanced JSON object using brace-depth counting.
    
    This avoids naive start/end matching that can span multiple disjoint objects.
    """
    start = text.find('{')
    if start == -1:
        raise ValueError(NO_JSON_FOUND_MESSAGE)
    
    depth = 0
    in_string = False
    escape = False
    
    for i in range(start, len(text)):
        char = text[i]
        
        if escape:
            escape = False
            continue
        
        if char == '\\' and in_string:
            escape = True
            continue
        
        if char == '"':
            in_string = not in_string
            continue
        
        if in_string:
            continue
        
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    
    raise ValueError(NO_JSON_FOUND_MESSAGE)
