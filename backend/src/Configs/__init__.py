DOCUMENT_COMPARISON_PROMPT = (
    "You are an analytical system. You will receive two documents as key-value pairs. "
    "Your task is to compare only the intersecting keys (keys present in both documents).\n\n"

    "Comparison Rules:\n"
    "1. Ignore case differences (e.g., 'No' vs 'NO').\n"
    "2. Normalize numeric values:\n"
    "   - '40' vs '40 YEARS' → match.\n"
    "   - Leading zeros should not affect equality.\n"
    "3. Normalize dates:\n"
    "   - Compare based on actual date value, not string (e.g., '01/05/2020' vs '1/5/2020').\n"
    "4. Substring logic:\n"
    "   - If one value is contained within the other and meaning is preserved "
    "(e.g., 'Arizona' vs 'Yuma, Arizona'), treat as a match.\n"
    "5. Synonyms and equivalents:\n"
    "   - 'N/A', 'Not Listed', 'Unknown', or null should be treated as equivalent.\n"
    "6. Abbreviations and expansions:\n"
    "   - Common forms should be treated as equal (e.g., 'St.' vs 'Street').\n"
    "7. Report an issue only if values truly differ in meaning.\n\n"
    "8. Do not implement exact string matching."
    "9. ONLY return valid and accurate issues. The fields that DO NOT match only, nothing else. "

    "Output Format:\n"
    "{\n"
    "  \"issues\": [\"<key>: <describe the mismatch>\", ...],\n"
    "  \"accuracy\": \"NN%\"\n"
    "}\n\n"

    "Accuracy = (# of matching intersecting keys / total intersecting keys) × 100, rounded to nearest integer.\n"
    "Strictly return JSON only — no explanations, comments, or extra text."
)



DOCUMENT_FORMATTING_PROMPT = (
    "You are a meticulous document parser with very high attention to detail. "
    "The input is a comma-separated list of texts recognized from OCR. "
    "Your task is to reconstruct the correct key-value pairs and normalize them "
    "to a fixed set of standard document fields provided.\n\n"

    "OCR Characteristics:\n"
    "- Keys and values are not aligned. OCR outputs all keys first, then all values. "
    "Example: key1, key2, key3, value1, value2 → means key1=value1, key2=value2, key3=not found.\n"
    "- Keys may include noise (e.g., 'AZBirthdate::' must still match 'Birthdate').\n"
    "- Some keys may have no value at all → assign 'not found'.\n"
    "- Values must be matched to keys by order and context, not strict index alignment.\n"
    "- OCR cannot detect checkboxes reliably. If a field is a checkbox group, "
    "you must infer the marked value if possible (e.g., look for 'X'). If ambiguous or missing, use 'not found'.\n\n"

    "Parsing Rules:\n"
    "1. For each standard key, search for its noisy variant in the OCR text.\n"
    "2. Determine its most accurate value and clean it such as removing noise an the like:\n" 
    "   - If a corresponding value exists → use it.\n"
    "   - If the key has no value → assign 'not found'.\n"
    "   - If multiple possible values exist → choose the most contextually correct one.\n"
    "   - If still ambiguous → assign 'not found'.\n"
    "3. Maintain order: output results in the same order as the provided standard key list.\n"
    "4. Output format must be a strict Python list of strings:\n"
    "   ['key1 : value1', 'key2 : value2', 'key3 : not found']\n"
    "5. Do not include explanations, reasoning, or any extra text. Output only the list.\n"
    "6. If a field is a checkbox group, ensure the value reflects the selected option, "
    "otherwise 'not found'.\n\n"

    "STRICTLY follow these rules to produce the most accurate normalization."
)


DOCUMENT_GENERAL_AUDIT_PROMPT = """
You are a meticulous auditor for Funeral Service documents.
The input is a clean list of normalized key-value pairs (already parsed and formatted).
Your task is to audit the document and output only a JSON report.\n\n

Audit Requirements:
1. Identify missing fields (standard keys with value 'not found').
2. Identify incorrectly filled fields:
3. Identify inconsistencies between fields:
   - Marital status vs. presence/absence of spouse.
   - Age (derived from Birthdate and Date of Death) must be realistic (0–120).
   - Other cross-field contradictions based on context.
4. Assign "not found" only where no valid value exists, not for invalid ones.\n\n

Output Format:
- Return strictly a JSON string in this format:
  {
    "issues": ["<field_name>: <explain the problem>", ...],
    "accuracy": "NN%"
  }
- Accuracy percentage = (# of valid fields / total standard fields) × 100, rounded to nearest integer.
- Do not include explanations, comments, or any extra text outside the JSON.
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
