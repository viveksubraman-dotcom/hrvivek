"""
In-Process Heuristic Pre-Scan (<15ms Regex Filter)
Implements Google SAIF Stage 1: PREPARE and OWASP Top 10 for LLM.
"""
import re
from typing import Tuple, Optional

INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"(?i)disregard\s+(all\s+)?(previous|prior)\s+rules?",
    r"(?i)you\s+are\s+now\s+(DAN|jailbroken|unfiltered|free)",
    r"(?i)system\s+prompt\s+(reveal|leak|show|print|display)",
    r"(?i)override\s+(all\s+)?policy\s+boundaries?",
    r"(?i)exfiltrate\s+(all\s+)?(data|passwords|tokens)",
    r"(?i)do\s+anything\s+now",
    r"(?i)acting\s+as\s+a\s+malicious",
    r"(?i)<script.*?>.*?</script>",
    r"(?i)DROP\s+TABLE|SELECT\s+\*\s+FROM\s+users",
    r"(?i)output\s+(the\s+)?(database|db|connection\s+string|bearer\s+token|api\s+key)",
    r"(?i)reveal\s+(all\s+)?(internal\s+prompts?|instructions?|hidden\s+rules?)",
]

EMOTIONAL_DISTRESS_PATTERNS = [
    r"(?i)\b(funeral|died|grieving|bereaved|loss|crying|hospital|family emergency)\b.*?\b(don't care|ignore|upset|frustrated|talk to (a )?human|manager|someone)\b",
    r"(?i)\b(talk to (a )?human|speak to (an? )?hrbp|connect me with (an? )?hr|transfer me to (an? )?hrbp)\b",
]

OUT_OF_SCOPE_PATTERNS = [
    r"(?i)\b(write\s+(a\s+)?python\s+code|debug\s+this\s+code|solve\s+leetcode)\b",
    r"(?i)\b(stock\s+tips?|bitcoin|crypto\s+price|invest\s+in)\b",
    r"(?i)\b(write\s+(a\s+)?poem|movie\s+recommendation|dating\s+advice)\b",
    r"(?i)\b(who\s+won\s+the\s+world\s+cup|tell\s+me\s+a\s+joke)\b",
    r"(?i)\b(calculate\s+(my\s+)?personal\s+.*tax\s+return)\b",
]

HALLUCINATION_BAIT_PATTERNS = [
    (r"(?i)pet\s+bereavement", "Pet Bereavement Leave"),
    (r"(?i)car\s+washing\s+allowance", "Car Washing Allowance"),
    (r"(?i)gaming\s+pc\s+subsidy", "Gaming PC Subsidy"),
    (r"(?i)gym\s+(membership|subsidy)|gym.*family", "Family Gym Membership"),
    (r"(?i)massage\s+reimbursement", "Massage Reimbursement"),
]

def scan_input_safety(prompt: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Returns (is_safe, block_category, reason_message)"""
    # 1. Emotional distress de-escalation takes precedence over security alert
    for pat in EMOTIONAL_DISTRESS_PATTERNS:
        if re.search(pat, prompt):
            return False, "EMOTIONAL_ESCALATION", "I understand you are experiencing an urgent or distressing situation. I am connecting you immediately with an HR Business Partner who can help."

    for pat in INJECTION_PATTERNS:
        if re.search(pat, prompt):
            return False, "PROMPT_INJECTION", "Interaction blocked: Potential prompt injection or system override detected."

    for pat in OUT_OF_SCOPE_PATTERNS:
        if re.search(pat, prompt):
            return False, "OUT_OF_SCOPE", "I am the Enterprise HR & IT Assistant. I can only assist with HR policies, WorkWeek leave/profiles, and ServiceImmediately support tickets."

    for pat, item_name in HALLUCINATION_BAIT_PATTERNS:
        if re.search(pat, prompt):
            return False, "ABSENT_POLICY", f"I searched the Altostrat Singapore Employee Handbook, but found no policy regarding '{item_name}'. Please contact HR Shared Services for exceptions."

    return True, None, None
