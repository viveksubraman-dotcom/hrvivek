"""
WorkWeek (HCM) Connector & Mock Store (FR-3.1 ~ FR-3.4)
"""
from typing import Dict, Any, Optional
from datetime import datetime
from ..validation.engine import validate_leave_request, validate_phone_e164

class WorkWeekConnector:
    def __init__(self):
        self._employees: Dict[str, Dict[str, Any]] = {
            "EMP-90210": {
                "employee_id": "EMP-90210",
                "name": "Jane Doe",
                "email": "jane.doe@enterprise.corp",
                "department": "Engineering",
                "role": "Senior Software Engineer",
                "manager": "Sarah Jenkins",
                "manager_id": "MGR-5002",
                "hire_date": "2023-03-15",
                "work_location": "Remote - US",
                "home_address": "123 Tech Lane, Austin TX 78701",
                "phone_number": "+1 512 555 0199",
                "balances": {
                    "vacation_accrued": 80.0, # hours (10 days)
                    "vacation_used": 40.0,
                    "vacation_remaining": 40.0, # hours (5 days)
                    "sick_accrued": 112.0,
                    "sick_used": 16.0,
                    "sick_remaining": 96.0, # hours (12 days)
                },
                "leave_requests": [],
                "staged_updates": {}
            }
        }

    def get_employee_profile(self, employee_id: str) -> Dict[str, Any]:
        """GET /api/v1/employees/{id}"""
        emp = self._employees.get(employee_id)
        if not emp:
            raise ValueError(f"Employee {employee_id} not found in WorkWeek")
        return {
            "employee_id": emp.get("employee_id", employee_id),
            "name": emp.get("name", "Unknown"),
            "email": emp.get("email", ""),
            "department": emp.get("department", ""),
            "role": emp.get("role", ""),
            "manager": emp.get("manager", "Sarah Jenkins"),
            "manager_id": emp.get("manager_id", "MGR-5002"),
            "hire_date": emp.get("hire_date", "2023-01-01"),
            "work_location": emp.get("work_location", "Office"),
            "home_address": emp.get("home_address", ""),
            "phone_number": emp.get("phone_number", ""),
        }

    def update_contact(self, employee_id: str, home_address: Optional[str] = None, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """PUT /api/v1/employees/{id}/contact"""
        emp = self._employees.get(employee_id)
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")
            
        if phone_number:
            if not validate_phone_e164(phone_number):
                raise ValueError(f"Validation Error: Phone number '{phone_number}' does not comply with E.164 international format.")
            emp["phone_number"] = phone_number

        if home_address:
            emp["home_address"] = home_address

        return {
            "status": "SUCCESS",
            "updated_timestamp": datetime.utcnow().isoformat(),
            "employee_id": employee_id,
            "home_address": emp["home_address"],
            "phone_number": emp["phone_number"]
        }

    def get_leave_balances(self, employee_id: str) -> Dict[str, Any]:
        """GET /api/v1/leave/balances (FR-3.4: Real-time fetch)"""
        emp = self._employees.get(employee_id)
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")
        b = emp["balances"]
        return {
            "employee_id": employee_id,
            "vacation_accrued_hours": b["vacation_accrued"],
            "vacation_remaining_hours": b["vacation_remaining"],
            "vacation_remaining_days": b["vacation_remaining"] / 8.0,
            "sick_accrued_hours": b["sick_accrued"],
            "sick_remaining_hours": b["sick_remaining"],
            "sick_remaining_days": b["sick_remaining"] / 8.0,
        }

    def submit_leave_request(self, employee_id: str, leave_type: str, start_date: str, end_date: str, requested_days: Optional[float] = None) -> Dict[str, Any]:
        """POST /api/v1/leave/requests"""
        emp = self._employees.get(employee_id)
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")

        b_key = "vacation_remaining" if leave_type.lower() == "vacation" else "sick_remaining"
        avail_days = emp["balances"][b_key] / 8.0

        is_valid, err_msg, calc_days = validate_leave_request(start_date, end_date, avail_days)
        if not is_valid:
            raise ValueError(err_msg)

        req_days = requested_days if requested_days is not None else calc_days
        hours_deducted = req_days * 8.0
        emp["balances"][b_key] -= hours_deducted
        emp["balances"][b_key.replace("remaining", "used")] += hours_deducted

        req_id = f"LR-{len(emp['leave_requests']) + 101}"
        record = {
            "request_id": req_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "work_days": req_days,
            "hours": hours_deducted,
            "status": "SUBMITTED",
            "submitted_at": datetime.utcnow().isoformat()
        }
        emp["leave_requests"].append(record)

        return {
            "status": "SUBMITTED",
            "request_id": req_id,
            "leave_type": leave_type,
            "work_days": req_days,
            "remaining_balance_days": emp["balances"][b_key] / 8.0,
            "remaining_balance_hours": emp["balances"][b_key]
        }

    def stage_contact_update(self, employee_id: str, address: str, status: str = "STAGED") -> Dict[str, Any]:
        """Two-phase commit: Stages address update without immediate tax commit."""
        emp = self._employees.get(employee_id)
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")
        staged_id = f"STAGE-{datetime.utcnow().strftime('%M%S')}"
        emp["staged_updates"][staged_id] = {
            "new_address": address,
            "previous_address": emp["home_address"],
            "status": status,
            "staged_at": datetime.utcnow().isoformat()
        }
        return {"staged_id": staged_id, "status": status, "address": address}

    def rollback_staged_update(self, employee_id: str, staged_id: str) -> Dict[str, Any]:
        """Compensating action: Reverts staged update."""
        emp = self._employees.get(employee_id)
        if emp and staged_id in emp["staged_updates"]:
            del emp["staged_updates"][staged_id]
        return {"status": "ABORTED_ROLLBACK_COMPLETE", "staged_id": staged_id}

_ww_client = WorkWeekConnector()
def get_workweek_client() -> WorkWeekConnector:
    return _ww_client
