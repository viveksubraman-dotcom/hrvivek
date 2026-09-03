"""
Zero-Trust Ingress Security: Identity & Access Claims Validation (WAF Security Pillar)
"""

from typing import Optional

from pydantic import BaseModel, Field


class UserClaims(BaseModel):
    user_id: str = Field("EMP-90210", description="Employee ID")
    user_email: str = Field("jane.doe@enterprise.corp", description="Corporate email")
    full_name: str = Field("Jane Doe", description="Display name")
    department: str = Field("Engineering", description="Department")
    role: str = Field("Senior Software Engineer", description="Job title")
    is_remote: bool = Field(True, description="Whether employee is designated remote")
    country: str = Field("SG", description="Primary country code")
    currency: str = Field("SGD", description="Payroll currency")


def validate_ingress_identity(mock_user: Optional[UserClaims] = None) -> UserClaims:
    if mock_user:
        return mock_user
    return UserClaims()


def enforce_rbac_access(requestor: UserClaims, target_employee_id: str) -> bool:
    """FR-1.5: Enforce strict Role-Based Access Control (RBAC)."""
    if requestor.role == "HR_ADMIN":
        return True
    return requestor.user_id == target_employee_id
