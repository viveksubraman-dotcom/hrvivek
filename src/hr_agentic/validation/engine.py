"""
Deterministic Validation Middleware (WAF Operational Excellence Pillar)
Enforces mathematical, temporal, and lifecycle constraints without LLM non-determinism.
"""
import re
from datetime import datetime, date, timedelta
from typing import Tuple, Optional

ALLOWED_LIFECYCLE_TRANSITIONS = {
    "New": ["In-Progress", "Assigned", "Cancelled"],
    "Assigned": ["In-Progress", "Cancelled"],
    "In-Progress": ["Resolved", "On-Hold", "Cancelled"],
    "On-Hold": ["In-Progress", "Cancelled"],
    "Resolved": ["Closed", "In-Progress"],
    "Closed": [],
    "Cancelled": [],
}

TRIVIAL_INCIDENT_KEYWORDS = ["coffee", "snack", "water cooler", "keyboard", "mouse pad", "chair adjustment"]

def calculate_working_days(start_str: str, end_str: str) -> int:
    """Calculates working business days (Mon-Fri) inclusive."""
    start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()
    
    if start_dt > end_dt:
        raise ValueError(f"Temporal validity violation: start_date ({start_str}) cannot be after end_date ({end_str})")
        
    cur = start_dt
    days = 0
    while cur <= end_dt:
        if cur.weekday() < 5: # 0=Mon, 4=Fri
            days += 1
        cur += timedelta(days=1)
    return days

def validate_leave_request(start_str: str, end_str: str, available_days: float) -> Tuple[bool, Optional[str], int]:
    """Validates chronological consistency and leave balance limits."""
    try:
        start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()
    except Exception as e:
        return False, f"Invalid date format: {e}. Expected YYYY-MM-DD.", 0

    if start_dt > end_dt:
        return False, f"Invalid date range: start_date ({start_str}) is after end_date ({end_str}).", 0

    working_days = calculate_working_days(start_str, end_str)
    if working_days == 0:
        return False, "Invalid leave request: Selected dates contain 0 working business days (e.g., weekends only).", 0

    if working_days > available_days:
        return False, f"Insufficient leave balance: requested {working_days} working days, but accrued balance is only {available_days} days.", working_days

    return True, None, working_days

def validate_leave_increment(requested_days: float) -> Tuple[bool, Optional[str]]:
    """Enforces minimum 0.5 day (half-day) increment boundary condition."""
    if requested_days <= 0:
        return False, f"Invalid duration: Requested leave days must be greater than 0 (got {requested_days})."
    if (requested_days * 2) % 1 != 0:
        return False, f"Invalid increment: Leave must be requested in full or half-day increments (0.5 days), got {requested_days}."
    return True, None

def validate_employee_id(employee_id: str) -> bool:
    """Validates Employee ID format (^EMP-\\d{5}$)."""
    if not employee_id or not isinstance(employee_id, str):
        return False
    return bool(re.match(r"^EMP-\d{5}$", employee_id.strip()))

def validate_phone_e164(phone: str) -> bool:
    """Validates E.164 international phone number format."""
    # Matches e.g. +65 9123 4567, +6591234567, +14155552671
    pattern = r"^\+?[1-9]\d{1,14}$"
    clean = re.sub(r"[\s\-\(\)]", "", phone)
    return bool(re.match(pattern, clean))

def validate_ticket_transition(current_status: str, target_status: str) -> Tuple[bool, Optional[str]]:
    """FR-4.3: Validates incident state machine transition."""
    allowed = ALLOWED_LIFECYCLE_TRANSITIONS.get(current_status, [])
    if target_status not in allowed:
        return False, f"Illegal lifecycle transition: Cannot transition incident directly from '{current_status}' to '{target_status}'. Allowed transitions: {allowed}."
    return True, None

def validate_ticket_priority(short_desc: str, priority: str) -> str:
    """FR-4.3 / TC-INTG-06: Priority anti-inflation guardrail."""
    desc_lower = short_desc.lower()
    for kw in TRIVIAL_INCIDENT_KEYWORDS:
        if kw in desc_lower and priority in ["1", "1 - Critical", "2", "2 - High"]:
            # Auto-downgrade trivial issue to Low
            return "4 - Low"
    return priority
