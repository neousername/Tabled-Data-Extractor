prompt = """
Extract all data from the table in this image into a JSON format.

Mandatory Keys (Headers):
Ensure every object in the JSON array has exactly these keys. Map the visible columns in the screenshot to these corresponding keys:
1. "NAME"
2. "EMAIL"
3. "PHONE NUMBER"
4. "CONTACT -> DEALS"
5. "LAST ACTIVITY DATE (G..."
6. "NUMBER OF CLOSED WO..."
7. "AREA OF ACTIVITY"
8. "AREA LABA"

Guidelines:
- Return a list of JSON objects (dictionaries).
- Map the visual columns to the mandatory keys above. Even if the visual header is slightly different or fully written out (e.g., "Last Activity"), map it to the requested key (e.g., "LAST A...").
- If a value is missing or the column is not present, use an empty string "" as the value.
- STRICTLY use the exact key names provided above.
- Provide ONLY the raw JSON output.
- No markdown formatting (no ```json), no explanations, no preamble.
"""
