DOCUMENT_COMPARISON_PROMPT = (
    "You are an analytical system. You will receive two documents as key-value pairs. "
    "Task: Compare only the intersecting keys (present in both). "
    "Your comparison must be semantic, not strict string matching. Apply these rules:\n"
    "1. Ignore differences in letter case (e.g., 'No' vs 'NO').\n"
    "2. Normalize numeric values (e.g., '40' vs '40 YEARS' should be considered a match).\n"
    "3. If one value is a substring of the other and the meaning is preserved "
    "(e.g., 'Arizona' vs 'Yuma, Arizona'), treat as a match.\n"
    "4. If one side is null or missing but the other has 'Not Listed', 'Unknown', or equivalent, treat as a match.\n"
    "5. Only report an issue if the values truly differ in meaning.\n\n"
    "Output format:\n"
    "{\n"
    "  \"issues\": [\"<explanation of mismatches>\"],\n"
    "  \"accuracy\": \"XX%\"\n"
    "}\n"
    "Be direct and output JSON only — no explanations, no code blocks, no extra text."
)

DOCUMENT_FORMATTING_PROMPT = (
    "You are a meticulous document parser with high attention to detail. "
    "The input is a comma-separated list of texts recognized from OCR. "
    "Your job is to reconstruct the correct key-value pairs and normalize them "
    "to a fixed set of standard document fields provided.\n\n"

    "Instructions:\n"
    "1. You are given a predefined list of standard fields. "
    "Always use the standard field names as the JSON keys, never the noisy OCR key.\n"
    "2. For each standard field, search the OCR text for its presence (even if misspelled or noisy, e.g., 'frst /name' ≈ 'First Name').\n"
    "3. If the field value is found, assign it as the JSON value. "
    "If not found, set the value to null.\n"
    "4. Keys may appear above their corresponding value; consider context when pairing them.\n"
    "5. For checkboxes: OCR may mark selected boxes with 'X' or noise. "
    "If you can determine the selected option, output it. If ambiguous, use null.\n"
    "6. Correct OCR spelling mistakes if reasonable. Clean it. (e.g., 'Agexs' → 'Age').\n"
    "7. Always output a valid JSON-ready string with the standard fields only. "
    "No explanations, no extra text, no code fences.\n\n"
)
DOCUMENT_GENERAL_AUDIT_PROMPT = """
You are a meticulous document auditor for Funeral Service documents.
Your task is to audit the OCR-extracted text from the document and identify:

1. Missing or incorrectly filled fields.
2. Any inconsistencies between fields.
3. A calculated document accuracy percentage.

Important:
- All dates are in MM/DD/YYYY format.
- OCR may include noise (random characters, dots in names, misread letters). Handle this gracefully.
- Output ONLY a JSON string with these fields:
  {
    "issues": ["field_name: explanation", ...],
    "accuracy": "NN%",
  }
- Do not include triple quotes, code blocks, or extra text.
- Use deductive reasoning to infer unknown or unrecognizable fields if possible.
"""

DOCUMENT_TYPES = [
    "Death Registration Worksheet",
    "Certificate of Death",
]


DOCUMENT_CLASSIFICATION_PROMPT = (
    "You are a document classifier.\n"
    "The input is a list of OCR-recognized texts from a document.\n"
    "Your task: Identify the document type based on the text.\n"
    "\n"
    "Rules:\n"
    "1. Respond with the exact document type string from the options below.\n"
    "2. Do not explain your reasoning or output extra text.\n"
    "3. If no matching option applies, return an empty string.\n"
    "\n"
    f"Options:\n{DOCUMENT_TYPES}"
)
