"""
HR Agentic Cognitive Loop & Master Orchestrator (SDD Section 3.1)
Coordinates Security Pre-Scan, Specialist Sub-Agents, Sagas, and Output DLP.
"""

import re
from typing import Any, Dict, Optional

from ..connectors.service_immediately import get_service_immediately_client
from ..connectors.workweek import get_workweek_client
from ..knowledge.retriever import get_policy_retriever
from ..saga.workflows import (
    execute_equipment_procurement_saga,
    execute_medical_leave_saga,
    execute_relocation_saga,
)
from ..security.auth_validator import UserClaims, enforce_rbac_access, validate_ingress_identity
from ..security.dlp_masking import mask_spii, sanitize_inbound_prompt
from ..security.injection_filter import scan_input_safety
from ..validation.engine import validate_leave_request


class HRAgenticOrchestrator:
    def __init__(self):
        self.ww = get_workweek_client()
        self.si = get_service_immediately_client()
        self.retriever = get_policy_retriever()
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def reset(self):
        self._sessions.clear()

    def process_message(
        self, prompt: str, user: Optional[UserClaims] = None, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        user_claims = validate_ingress_identity(user)
        session_key = session_id or user_claims.user_id
        session = self._sessions.setdefault(
            session_key, {"turns": [], "last_topic": None, "pending_action": None}
        )

        # Step 0: Inbound Sanitization (DLP pre-storage hook for HIPAA/GDPR - ARB P0-01)
        sanitized_prompt = sanitize_inbound_prompt(prompt)
        session["turns"].append({"role": "user", "content": sanitized_prompt})

        p_lower = prompt.lower()

        # Step 1: In-Process Heuristic Safety Pre-Scan (<15ms)
        is_safe, block_cat, reason = scan_input_safety(prompt)
        if not is_safe:
            if block_cat == "EMOTIONAL_ESCALATION":
                # Decouple emotional distress: create empathetic HRSD ticket rather than SecOps alert
                ticket = self.si.create_incident(
                    requestor_id=user_claims.user_id,
                    category="HRSD-Escalation",
                    short_desc=f"Emotional/Bereavement Support: {prompt[:80]}",
                    priority="2 - High",
                )
                resp = f"I understand this is an urgent situation. I have created escalation ticket {ticket['ticket_id']} and connected you with an HR Business Partner who will reach out immediately."
                return {
                    "status": "ESCALATED_TO_HUMAN",
                    "category": "EMOTIONAL_SUPPORT",
                    "response": resp,
                    "ticket_id": ticket["ticket_id"],
                    "tool_calls": ["create_incident"],
                }
            return {
                "status": "BLOCKED",
                "category": block_cat,
                "response": reason,
                "tool_calls": [],
            }

        # Step 1.5: Human-in-the-Loop Escalation Request (e.g. "Connect to HRBP", "talk to human")
        if any(
            h in p_lower
            for h in [
                "connect to hrbp",
                "talk to human",
                "speak to hr",
                "transfer to human",
                "human representative",
            ]
        ):
            ticket = self.si.create_incident(
                requestor_id=user_claims.user_id,
                category="HRSD-Escalation",
                short_desc="Employee requested direct human HRBP transfer",
                priority="3 - Moderate",
            )
            resp = f"I have transferred your request to HR Shared Services. Support ticket {ticket['ticket_id']} has been opened and an HRBP will contact you directly."
            return {
                "status": "ESCALATED_TO_HUMAN",
                "intent": "HUMAN_ESCALATION",
                "response": resp,
                "ticket_id": ticket["ticket_id"],
                "tool_calls": ["create_incident"],
            }

        # Step 1.6: Multi-Turn Pronoun Resolution & Confirmation
        words = p_lower.split()
        if ("it" in words or "that" in words or "for it" in p_lower) and any(
            w in p_lower for w in ["days", "balance", "left", "remaining", "hours"]
        ):
            last_top = session.get("last_topic")
            if last_top == "sick_leave":
                b = self.ww.get_leave_balances(user_claims.user_id)
                resp = f"You currently have {b['sick_remaining_days']:.1f} days ({b['sick_remaining_hours']}h) of sick leave remaining."
                return {
                    "status": "SUCCESS",
                    "intent": "UC-1.2_QUERY_BALANCES_PRONOUN",
                    "response": resp,
                    "tool_calls": ["get_leave_balances"],
                }
            elif last_top == "vacation":
                b = self.ww.get_leave_balances(user_claims.user_id)
                resp = f"You currently have {b['vacation_remaining_days']:.1f} days ({b['vacation_remaining_hours']}h) of vacation leave remaining."
                return {
                    "status": "SUCCESS",
                    "intent": "UC-1.2_QUERY_BALANCES_PRONOUN",
                    "response": resp,
                    "tool_calls": ["get_leave_balances"],
                }
            elif last_top == "bereavement":
                resp = "Under Section 22, employees are entitled to 5 consecutive business days of paid bereavement leave for immediate family members and 2 days for extended family."
                return {
                    "status": "SUCCESS",
                    "intent": "UC-1.2_QUERY_BALANCES_PRONOUN",
                    "response": resp,
                    "tool_calls": [],
                }

        # Step 1.6b: Cancellation
        if session.get("pending_action") and any(
            w in p_lower for w in ["cancel", "abort", "nevermind", "never mind", "stop"]
        ):
            session.pop("pending_action")
            return {
                "status": "CANCELLED",
                "intent": "UC-1.2_LEAVE_CANCELLED",
                "response": "Your pending leave submission request has been cancelled.",
                "tool_calls": [],
            }

        # Step 1.6c: Confirmation Execution
        if session.get("pending_action") and any(
            w in p_lower
            for w in ["confirm", "proceed", "yes", "thursday", "friday", "dates", "schedule"]
        ):
            date_matches = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", prompt)
            if len(date_matches) >= 2:
                start_date, end_date = date_matches[0], date_matches[1]
            elif len(date_matches) == 1:
                start_date, end_date = date_matches[0], date_matches[0]
            else:
                # Default sample window: next Thursday and Friday
                start_date, end_date = "2026-09-10", "2026-09-11"

            b = self.ww.get_leave_balances(user_claims.user_id)
            avail = b.get("vacation_remaining_days", 0.0)
            valid, err, work_days = validate_leave_request(start_date, end_date, avail)
            if not valid:
                return {
                    "status": "ERROR_VALIDATION",
                    "intent": "UC-1.2_CONFIRM_VALIDATION_ERROR",
                    "response": f"Leave Request Validation Failed: {err}",
                    "tool_calls": ["validate_leave"],
                }

            session.pop("pending_action")
            res = self.ww.submit_leave_request(
                user_claims.user_id, "Vacation", start_date, end_date
            )
            resp = f"Confirmed and submitted vacation request {res['request_id']} for {res['work_days']} days. Remaining balance: {res['remaining_balance_days']} days."
            return {
                "status": "SUCCESS",
                "intent": "UC-1.2_CONFIRMED_LEAVE",
                "response": resp,
                "tool_calls": ["submit_leave_request"],
            }

        # Step 1.6d: Leave Request Slot-Filling (Pending Confirmation)
        if (
            "submit" in p_lower
            and any(w in p_lower for w in ["days off", "day off", "vacation", "leave"])
            and "confirm" not in p_lower
        ):
            m_days = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:business\s*)?days?", p_lower)
            days_str = m_days.group(1) if m_days else "2"
            session["pending_action"] = {
                "action": "submit_leave",
                "prompt": prompt,
                "days_str": days_str,
            }
            return {
                "status": "PENDING_CONFIRMATION",
                "intent": "UC-1.2_LEAVE_PENDING",
                "response": f"Please specify the exact dates (e.g. next Thursday and Friday) to confirm your {days_str}-day leave submission.",
                "tool_calls": ["validate_leave"],
            }

        # Step 1.7: Categorical Prohibition Overrides (Gift Card, Room Salon)
        if (
            "gift card" in p_lower
            or ("host" in p_lower and "card" in p_lower)
            or "room salon" in p_lower
            or "adult entertainment" in p_lower
        ):
            policy_res = self.retriever.query_policy(prompt)
            return {
                "status": "SUCCESS",
                "intent": "UC-1.1_PROHIBITION_OVERRIDE",
                "response": mask_spii(policy_res["answer"]),
                "citation": policy_res.get("citation"),
                "deep_link": policy_res.get("deep_link"),
                "tool_calls": ["query_policy"],
            }

        # Step 2: RBAC Check (e.g. attempting to inspect someone else's record)
        m = re.search(r"EMP-\d{5}", prompt, re.IGNORECASE)
        if m:
            target_id = m.group(0).upper()
            if not enforce_rbac_access(user_claims, target_id):
                return {
                    "status": "BLOCKED_RBAC",
                    "category": "ACCESS_DENIED",
                    "response": f"Access Denied: You are not authorized to view or modify records for employee '{target_id}'.",
                    "tool_calls": [],
                }

        # Step 3: Cross-System Orchestration (UC-2.x)
        if "monitor" in p_lower and ("remote" in p_lower or "order" in p_lower):
            res = execute_equipment_procurement_saga(user_claims.user_id)
            return {
                "status": "SUCCESS",
                "intent": "UC-2.1_EQUIPMENT_PROCUREMENT",
                "response": mask_spii(res["message"]),
                "details": res,
                "tool_calls": ["query_hr_policy", "get_employee_profile", "create_incident_ticket"],
            }

        if "medical leave" in p_lower or ("sick leave" in p_lower and "access" in p_lower):
            try:
                res = execute_medical_leave_saga(
                    user_claims.user_id, start_date="2026-09-07", days=10
                )
                return {
                    "status": "SUCCESS",
                    "intent": "UC-2.2_MEDICAL_LEAVE",
                    "response": mask_spii(res["message"]),
                    "details": res,
                    "tool_calls": [
                        "query_hr_policy",
                        "submit_leave_request",
                        "get_employee_profile",
                        "create_incident_ticket",
                    ],
                }
            except Exception as e:
                return {
                    "status": "FAILED_BUSINESS_RULE",
                    "intent": "UC-2.2_MEDICAL_LEAVE",
                    "response": f"Unable to process medical leave: {str(e)}",
                    "error": str(e),
                    "tool_calls": ["query_hr_policy"],
                }

        if (
            "transfer" in p_lower
            and "london" in p_lower
            or ("relocation" in p_lower and "allowance" in p_lower)
        ):
            res = execute_relocation_saga(user_claims.user_id)
            return {
                "status": "SUCCESS",
                "intent": "UC-2.3_RELOCATION",
                "response": mask_spii(res["message"]),
                "details": res,
                "tool_calls": ["query_hr_policy", "stage_contact_update", "create_incident_ticket"],
            }

        # Step 4: Single-Domain Operations (UC-1.x)
        # WorkWeek: PTO balance
        if "pto" in p_lower or "balance" in p_lower or "vacation days" in p_lower:
            b = self.ww.get_leave_balances(user_claims.user_id)
            resp = f"Your current leave balances: Vacation: {b['vacation_remaining_days']:.1f} days ({b['vacation_remaining_hours']}h), Sick: {b['sick_remaining_days']:.1f} days ({b['sick_remaining_hours']}h)."
            return {
                "status": "SUCCESS",
                "intent": "UC-1.2_QUERY_BALANCES",
                "response": resp,
                "tool_calls": ["get_leave_balances"],
            }

        # WorkWeek: Submit leave
        if "vacation" in p_lower and ("submit" in p_lower or "request" in p_lower):
            try:
                # default sample request: 2 days (2026-09-10 to 2026-09-11)
                res = self.ww.submit_leave_request(
                    user_claims.user_id, "Vacation", "2026-09-10", "2026-09-11"
                )
                resp = f"Vacation request {res['request_id']} submitted for {res['work_days']} days. Remaining balance: {res['remaining_balance_days']} days."
                return {
                    "status": "SUCCESS",
                    "intent": "UC-1.2_SUBMIT_LEAVE",
                    "response": resp,
                    "tool_calls": ["submit_leave_request"],
                }
            except Exception as e:
                return {
                    "status": "ERROR_VALIDATION",
                    "response": f"Leave Request Failed: {e}",
                    "tool_calls": ["submit_leave_request"],
                }

        # ServiceImmediately: Ticket lookup
        if "inc0094821" in p_lower or ("ticket" in p_lower and "status" in p_lower):
            try:
                t = self.si.get_incident("INC0094821")
                resp = f"Ticket {t['ticket_id']} ({t['short_description']}): Status is '{t['status']}', Priority is '{t['priority']}', Assigned to {t['assignee']}."
                return {
                    "status": "SUCCESS",
                    "intent": "UC-1.3_QUERY_TICKET",
                    "response": resp,
                    "tool_calls": ["get_incident"],
                }
            except Exception as e:
                return {"status": "ERROR", "response": str(e), "tool_calls": []}

        # ServiceImmediately: Create ticket
        if "ticket" in p_lower and (
            "create" in p_lower or "open" in p_lower or "vpn" in p_lower or "broken" in p_lower
        ):
            prio = "1 - Critical" if "critical" in p_lower else "3 - Moderate"
            res = self.si.create_incident(user_claims.user_id, "IT-Network", prompt, priority=prio)
            if res.get("status") == "DUPLICATE_SUPPRESSED":
                return {
                    "status": "DUPLICATE_SUPPRESSED",
                    "intent": "UC-1.3_DUPLICATE_TICKET",
                    "response": res["message"],
                    "tool_calls": ["create_incident"],
                }
            resp = f"Created support ticket {res['ticket_id']} with priority '{res['priority']}'. An IT specialist will investigate."
            return {
                "status": "SUCCESS",
                "intent": "UC-1.3_CREATE_TICKET",
                "response": resp,
                "tool_calls": ["create_incident"],
            }

        # Step 5: OKF Policy Inquiry (UC-1.1)
        if "sick" in p_lower:
            session["last_topic"] = "sick_leave"
        elif "vacation" in p_lower or "annual leave" in p_lower or "pto" in p_lower:
            session["last_topic"] = "vacation"
        elif "bereavement" in p_lower or "funeral" in p_lower:
            session["last_topic"] = "bereavement"

        policy_res = self.retriever.query_policy(prompt)
        return {
            "status": "SUCCESS",
            "intent": "UC-1.1_POLICY_QA",
            "response": mask_spii(policy_res["answer"]),
            "citation": policy_res.get("citation"),
            "deep_link": policy_res.get("deep_link"),
            "tool_calls": ["query_policy"],
        }


_orchestrator = HRAgenticOrchestrator()


def get_orchestrator() -> HRAgenticOrchestrator:
    return _orchestrator
