"""
DLP & Sensitive Personally Identifiable Information (SPII) Masking Pipeline.
"""
import re

NRIC_REGEX = r"\b[STFGQM]\d{7}[A-Z]\b"
CREDIT_CARD_REGEX = r"\b(?:\d{4}[ -]?){3}\d{4}\b"

def mask_spii(text: str) -> str:
    if not text:
        return text
    masked = re.sub(NRIC_REGEX, "[REDACTED_NRIC]", text)
    masked = re.sub(CREDIT_CARD_REGEX, "[REDACTED_CREDIT_CARD]", masked)
    return masked
