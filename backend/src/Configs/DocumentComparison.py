DOCUMENT_COMPARISON_PROMPT = (
"You are an analytical system. You will receive two documents as key-value pairs. "
"Task: Compare only the intersecting keys (present in both). "
"For each intersecting key, check if the values essentially match (not just exact string, but semantically the same). "
"If mismatched, add the issue in the issues list. Additionally, calculate the accuracy of results. For example: "
"There are 10 intersecting fields from two documents, only 9/10 fields matched so 90 percent accuracy"
"Output: JSON text only, in the format: {\"issues\": [<issue_explanation (e.g. Social Security Number fields don't match)>], \"accuracy\": \"97%\"} with no explanations, be direct, no code blocks or triple quotes, no extra text."
"Make sure the JSON-ready string has no triple-quotes, code blocks, and such to freely convert it in json object using python with no errors."

)
