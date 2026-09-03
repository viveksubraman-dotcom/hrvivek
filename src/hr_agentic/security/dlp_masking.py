"""
DLP & Sensitive Personally Identifiable Information (SPII) Masking Pipeline.
"""

import re

NRIC_REGEX = r"\b[STFGQM]\d{7}[A-Z]\b"
CREDIT_CARD_REGEX = r"\b(?:\d{4}[ -]?){3}\d{4}\b"
PHONE_REGEX = r"(?<!\w)(?:\+65[-.\s]?|\b)[689]\d{3}[-.\s]?\d{4}\b|(?<!\w)(?:\+1[-.\s]?|\b)\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"

PHI_MEDICAL_PATTERNS = [
    r"(?i)\b(chemotherapy|mastectomy|radiotherapy|oncology|biopsy|cancer|tumor|malignancy)\b",
    r"(?i)\b(hiv|aids|tuberculosis|hepatitis|psychiatric|schizophrenia|bipolar)\b",
    r"(?i)\b(prescription|dosage|medication|antidepressant|insulin|codeine)\b",
]


def mask_spii(text: str) -> str:
    if not text:
        return text
    masked = re.sub(NRIC_REGEX, "[REDACTED_NRIC]", text)
    masked = re.sub(CREDIT_CARD_REGEX, "[REDACTED_CREDIT_CARD]", masked)
    masked = re.sub(PHONE_REGEX, "[REDACTED_PHONE]", masked)
    return masked


def mask_phi(text: str) -> str:
    """Masks Protected Health Information (PHI) and medical conditions (HIPAA / GDPR Art 9)."""
    if not text:
        return text
    masked = text
    for pat in PHI_MEDICAL_PATTERNS:
        masked = re.sub(pat, "[REDACTED_MEDICAL_PHI]", masked)
    return masked


def sanitize_inbound_prompt(prompt: str) -> str:
    """Pre-persistence inbound sanitization hook for session state (ARB P0-01 Remediation)."""
    if not prompt:
        return prompt
    sanitized = mask_spii(prompt)
    sanitized = mask_phi(sanitized)
    return sanitized
