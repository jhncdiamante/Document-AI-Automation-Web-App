
import os

def get_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENT_GENERAL_AUDIT_PROMPT_PATH = os.path.join(BASE_DIR, "general_auditing_prompt.txt")
DOCUMENT_COMPARISON_PROMPT_PATH = os.path.join(BASE_DIR, "comparison_prompt.txt")
DOCUMENT_FORMATTING_PROMPT_PATH = os.path.join(BASE_DIR,  "formatting.txt")
DOCUMENT_CLASSIFICATION_PROMPT_PATH = os.path.join(BASE_DIR,  "classification.txt")




DOCUMENT_GENERAL_AUDIT_PROMPT = get_prompt(DOCUMENT_GENERAL_AUDIT_PROMPT_PATH)
DOCUMENT_COMPARISON_PROMPT = get_prompt(DOCUMENT_COMPARISON_PROMPT_PATH)
DOCUMENT_FORMATTING_PROMPT = get_prompt(DOCUMENT_FORMATTING_PROMPT_PATH)
DOCUMENT_CLASSIFICATION_PROMPT = get_prompt(DOCUMENT_CLASSIFICATION_PROMPT_PATH)

