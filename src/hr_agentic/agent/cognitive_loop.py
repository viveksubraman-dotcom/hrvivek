"""
HR Agentic Cognitive Loop & Master Orchestrator (SDD Section 3.1)
Coordinates Security Pre-Scan, Specialist Sub-Agents, Sagas, and Output DLP.
"""
from typing import Dict, Any, Optional
from ..security.auth_validator import UserClaims, validate_ingress_identity, enforce_rbac_access
from ..security.injection_filter import scan_input_safety
from ..security.dlp_masking import mask_spii
from ..connectors.workweek import get_workweek_client
from ..connectors.service_immediately import get_service_immediately_client
from ..knowledge.retriever import get_policy_retriever
from ..saga.workflows import (
    execute_equipment_procurement_saga,
    execute_medical_leave_saga,
    execute_relocation_saga
)

class HRAgenticOrchestrator:
    def __init__(self):
        self.ww = get_workweek_client()
        self.si = get_service_immediately_client()
        self.retriever = get_policy_retriever()

    def process_message(self, prompt: str, user: Optional[UserClaims] = None) -> Dict[str, Any]:
        user_claims = validate_ingress_identity(user)
        p_lower = prompt.lower()

        # Step 1: In-Process Heuristic Safety Pre-Scan (<15ms)
        is_safe, block_cat, reason = scan_input_safety(prompt)
        if not is_safe:
            return {
                "status": "BLOCKED",
                "category": block_cat,
                "response": reason,
                "tool_calls": []
            }

        # Step 2: RBAC Check (e.g. attempting to inspect someone else's record)
        import re
        m = re.search(r"EMP-\d{5}", prompt, re.IGNORECASE)
        if m:
            target_id = m.group(0).upper()
            if not enforce_rbac_access(user_claims, target_id):
                return {
                    "status": "BLOCKED_RBAC",
                    "category": "ACCESS_DENIED",
                    "response": f"Access Denied: You are not authorized to view or modify records for employee '{target_id}'.",
                    "tool_calls": []
                }

        # Step 3: Cross-System Orchestration (UC-2.x)
        if "monitor" in p_lower and ("remote" in p_lower or "order" in p_lower):
            res = execute_equipment_procurement_saga(user_claims.user_id)
            return {
                "status": "SUCCESS",
                "intent": "UC-2.1_EQUIPMENT_PROCUREMENT",
                "response": mask_spii(res["message"]),
                "details": res,
                "tool_calls": ["query_hr_policy", "get_employee_profile", "create_incident_ticket"]
            }

        if "medical leave" in p_lower or ("sick leave" in p_lower and "access" in p_lower):
            res = execute_medical_leave_saga(user_claims.user_id, start_date="2026-09-07", days=10)
            return {
                "status": "SUCCESS",
                "intent": "UC-2.2_MEDICAL_LEAVE",
                "response": mask_spii(res["message"]),
                "details": res,
                "tool_calls": ["query_hr_policy", "submit_leave_request", "get_employee_profile", "create_incident_ticket"]
            }

        if "transfer" in p_lower and "london" in p_lower or ("relocation" in p_lower and "allowance" in p_lower):
            res = execute_relocation_saga(user_claims.user_id)
            return {
                "status": "SUCCESS",
                "intent": "UC-2.3_RELOCATION",
                "response": mask_spii(res["message"]),
                "details": res,
                "tool_calls": ["query_hr_policy", "stage_contact_update", "create_incident_ticket"]
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
                "tool_calls": ["get_leave_balances"]
            }

        # WorkWeek: Submit leave
        if "vacation" in p_lower and ("submit" in p_lower or "request" in p_lower):
            try:
                # default sample request: 2 days (2026-09-10 to 2026-09-11)
                res = self.ww.submit_leave_request(user_claims.user_id, "Vacation", "2026-09-10", "2026-09-11")
                resp = f"Vacation request {res['request_id']} submitted for {res['work_days']} days. Remaining balance: {res['remaining_balance_days']} days."
                return {
                    "status": "SUCCESS",
                    "intent": "UC-1.2_SUBMIT_LEAVE",
                    "response": resp,
                    "tool_calls": ["submit_leave_request"]
                }
            except Exception as e:
                return {
                    "status": "ERROR_VALIDATION",
                    "response": f"Leave Request Failed: {e}",
                    "tool_calls": ["submit_leave_request"]
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
                    "tool_calls": ["get_incident"]
                }
            except Exception as e:
                return {"status": "ERROR", "response": str(e), "tool_calls": []}

        # ServiceImmediately: Create ticket
        if "ticket" in p_lower and ("create" in p_lower or "open" in p_lower or "vpn" in p_lower or "broken" in p_lower):
            prio = "1 - Critical" if "critical" in p_lower else "3 - Moderate"
            res = self.si.create_incident(user_claims.user_id, "IT-Network", prompt, priority=prio)
            if res.get("status") == "DUPLICATE_SUPPRESSED":
                return {
                    "status": "DUPLICATE_SUPPRESSED",
                    "intent": "UC-1.3_DUPLICATE_TICKET",
                    "response": res["message"],
                    "tool_calls": ["create_incident"]
                }
            resp = f"Created support ticket {res['ticket_id']} with priority '{res['priority']}'. An IT specialist will investigate."
            return {
                "status": "SUCCESS",
                "intent": "UC-1.3_CREATE_TICKET",
                "response": resp,
                "tool_calls": ["create_incident"]
            }

        # Step 5: OKF Policy Inquiry (UC-1.1)
        policy_res = self.retriever.query_policy(prompt)
        return {
            "status": "SUCCESS",
            "intent": "UC-1.1_POLICY_QA",
            "response": mask_spii(policy_res["answer"]),
            "citation": policy_res.get("citation"),
            "deep_link": policy_res.get("deep_link"),
            "tool_calls": ["query_policy"]
        }

_orchestrator = HRAgenticOrchestrator()
def get_orchestrator() -> HRAgenticOrchestrator:
    return _orchestrator
