"""
Cross-System Distributed Saga Workflows:
UC-2.1: Equipment Procurement
UC-2.2: Medical Leave & Access Delegation
UC-2.3: Relocation with Two-Phase Staging & Compensation
"""

from typing import Any, Dict

from ..connectors.service_immediately import get_service_immediately_client
from ..connectors.workweek import get_workweek_client
from ..knowledge.retriever import get_policy_retriever
from .coordinator import get_saga_coordinator


def execute_equipment_procurement_saga(employee_id: str) -> Dict[str, Any]:
    """UC-2.1: OKF Policy -> WorkWeek Profile -> ServiceImmediately Hardware Order"""
    ww = get_workweek_client()
    si = get_service_immediately_client()
    retriever = get_policy_retriever()
    saga = get_saga_coordinator()

    saga_id = saga.start_saga("EQUIPMENT_PROCUREMENT", employee_id)

    # Step 1: Policy entitlement verification
    policy_res = retriever.query_policy("home office monitor allowance remote")
    saga.log_step(saga_id, "VERIFY_POLICY", "OKF_Brain", policy_res)

    # Step 2: WorkWeek profile verification
    profile = ww.get_employee_profile(employee_id)
    saga.log_step(saga_id, "FETCH_PROFILE", "WorkWeek_HCM", profile)

    if "Remote" not in profile["work_location"]:
        saga.abort_saga(saga_id, "User is not designated remote")
        return {"status": "FAILED", "reason": "Employee is not designated remote."}

    # Step 3: ServiceImmediately hardware ticket
    ticket = si.create_incident(
        requestor_id=employee_id,
        category="Hardware-Procurement",
        short_desc=f"Standard 27in Monitor (${int(policy_res['facts']['allowance_usd'])}) for Remote Worker",
        priority="4 - Low",
        shipping_address=profile["home_address"],
    )
    saga.log_step(saga_id, "CREATE_TICKET", "ServiceImmediately", ticket)
    saga.commit_saga(saga_id)

    return {
        "status": "SUCCESS",
        "saga_id": saga_id,
        "policy_citation": policy_res["citation"],
        "policy_deep_link": policy_res["deep_link"],
        "ticket_id": ticket["ticket_id"],
        "shipping_address": profile["home_address"],
        "message": f"Verified remote status. Hardware order {ticket['ticket_id']} created for a 27in monitor shipping to {profile['home_address']} [{policy_res['citation']}].",
    }


def execute_medical_leave_saga(employee_id: str, start_date: str, days: int = 10) -> Dict[str, Any]:
    """UC-2.2: Policy -> WorkWeek Sick Leave -> ServiceImmediately Manager Access Delegation"""
    ww = get_workweek_client()
    si = get_service_immediately_client()
    retriever = get_policy_retriever()
    saga = get_saga_coordinator()

    saga_id = saga.start_saga("MEDICAL_LEAVE_SETUP", employee_id)

    # Step 1: Policy query
    policy_res = retriever.query_policy("sick leave medical certificate deadline")
    saga.log_step(saga_id, "POLICY_CHECK", "OKF_Brain", policy_res)

    # Step 2: WorkWeek leave submission
    # Calculate approximate end date
    from datetime import datetime, timedelta

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=days + 4)  # buffer for weekends
    end_str = end_dt.strftime("%Y-%m-%d")

    leave_res = ww.submit_leave_request(
        employee_id, "Sick", start_date, end_str, requested_days=days
    )
    saga.log_step(saga_id, "SUBMIT_LEAVE", "WorkWeek_HCM", leave_res)

    # Step 3: Fetch manager
    profile = ww.get_employee_profile(employee_id)
    manager_name = profile["manager"]

    # Step 4: ServiceImmediately access delegation ticket
    ticket = si.create_incident(
        requestor_id=employee_id,
        category="Access-Management",
        short_desc=f"Delegate email and workflow access to manager {manager_name} during medical leave",
        priority="3 - Moderate",
    )
    saga.log_step(saga_id, "ACCESS_DELEGATION", "ServiceImmediately", ticket)
    saga.commit_saga(saga_id)

    return {
        "status": "SUCCESS",
        "saga_id": saga_id,
        "leave_request_id": leave_res["request_id"],
        "ticket_id": ticket["ticket_id"],
        "manager": manager_name,
        "message": f"Medical leave request {leave_res['request_id']} submitted for {days} days. Access delegation ticket {ticket['ticket_id']} assigned to {manager_name}. Reminder: Submit MC within 48 hours [{policy_res['citation']}].",
    }


def execute_relocation_saga(
    employee_id: str,
    new_address: str = "10 Baker St, London, UK",
    simulate_step3_failure: bool = False,
) -> Dict[str, Any]:
    """UC-2.3: Relocation allowance -> Stage WorkWeek address -> Create London badge ticket (with compensating rollback)"""
    ww = get_workweek_client()
    si = get_service_immediately_client()
    retriever = get_policy_retriever()
    saga = get_saga_coordinator()

    saga_id = saga.start_saga("OFFICE_RELOCATION", employee_id)

    # Step 1: OKF policy check
    policy_res = retriever.query_policy("relocation allowance London UK")
    saga.log_step(saga_id, "POLICY_CHECK", "OKF_Brain", policy_res)
    allowance_gbp = policy_res["facts"]["allowance_gbp"]

    # Step 2: Stage address update in WorkWeek
    staged = ww.stage_contact_update(employee_id, new_address, status="STAGED")
    saga.log_step(saga_id, "STAGE_ADDRESS", "WorkWeek_HCM", staged)

    # Step 3: Create badge ticket in ServiceImmediately
    if simulate_step3_failure:
        # Simulate downstream failure -> execute compensation rollback
        rollback_res = ww.rollback_staged_update(employee_id, staged["staged_id"])
        saga.log_step(
            saga_id,
            "COMPENSATING_ROLLBACK",
            "WorkWeek_HCM",
            rollback_res,
            status="ROLLBACK_SUCCESS",
        )
        saga.abort_saga(saga_id, "ServiceImmediately facilities endpoint timed out")
        return {
            "status": "COMPENSATED_ROLLBACK",
            "saga_id": saga_id,
            "staged_id": staged["staged_id"],
            "message": "Downstream ticket creation timed out. Compensating transaction executed: Staged address was safely rolled back to prevent split-brain tax errors.",
        }

    ticket = si.create_incident(
        requestor_id=employee_id,
        category="Facilities-Badge",
        short_desc=f"London Canary Wharf Building Access Badge for {new_address}",
        priority="3 - Moderate",
    )
    saga.log_step(saga_id, "FACILITIES_BADGE", "ServiceImmediately", ticket)
    saga.commit_saga(saga_id)

    return {
        "status": "SUCCESS",
        "saga_id": saga_id,
        "allowance_gbp": allowance_gbp,
        "staged_id": staged["staged_id"],
        "ticket_id": ticket["ticket_id"],
        "message": f"Relocation allowance is £{int(allowance_gbp):,} GBP. Address staged in WorkWeek ({staged['staged_id']}) and London Facilities badge ticket {ticket['ticket_id']} created [{policy_res['citation']}].",
    }
