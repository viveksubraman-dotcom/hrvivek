"""
Open Knowledge Format (OKF) Semantic Rule Registry & Ontology (SDD Section 5.3)
Machine-interpretable entity-relationship-rule matrices grounded in Altostrat Singapore Policy Handbook.
"""
from typing import Dict, Any

OKF_RULE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "bereavement_leave": {
        "rule_id": "OKF-RULE-BEREAVEMENT-01",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 22",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 22",
        "deep_link": "http://google3/policy#sec-22",
        "title": "Bereavement Leave Entitlements",
        "entities": {
            "immediate_family": {
                "members": ["spouse", "domestic partner", "civil partner", "partner", "child", "parent", "sibling", "father", "mother", "brother", "sister", "legal guardian", "foster child"],
                "days_entitlement": 5,
                "pay_status": "Full Pay",
                "conditions": "5 consecutive business days upon death of immediate family member (including spouse, domestic partner, child, parent, sibling, legal guardian)."
            },
            "extended_family": {
                "members": ["grandparent", "in-law", "uncle", "aunt"],
                "days_entitlement": 2,
                "pay_status": "Full Pay",
                "conditions": "2 consecutive business days."
            }
        }
    },
    "sick_leave_mc": {
        "rule_id": "OKF-RULE-SICK-02",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 19",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 19",
        "deep_link": "http://google3/policy#sec-19",
        "title": "Outpatient Sick Time & Hospitalization Leave",
        "rules": {
            "outpatient_annual_limit_days": 14,
            "hospitalisation_annual_limit_days": 60,
            "mc_submission_deadline_hours": 48,
            "condition": "A certified Medical Certificate (MC) from a registered doctor must be uploaded within 48 hours for sick leaves exceeding 2 consecutive days."
        }
    },
    "vacation_notice": {
        "rule_id": "OKF-RULE-VACATION-03",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 20",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 20",
        "deep_link": "http://google3/policy#sec-20",
        "title": "Annual Vacation Booking Advance Notice",
        "rules": {
            "advance_notice_days": 15,
            "system_of_record": "Workday / WorkWeek",
            "condition": "Annual leave must be booked at least 15 days in advance via Workday."
        }
    },
    "travel_meal_allowance": {
        "rule_id": "OKF-RULE-TRAVEL-04",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 4",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 4",
        "deep_link": "http://google3/policy#sec-4",
        "title": "Daily Business Travel Meal Allowance",
        "rules": {
            "daily_meal_cap_usd": 120.0,
            "scope": "Per employee per day",
            "currency": "USD",
            "condition": "Team and individual travel meals are capped at USD $120 per person per day."
        }
    },
    "anti_bribery_gifts": {
        "rule_id": "OKF-RULE-ETHICS-05",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 13",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 13",
        "deep_link": "http://google3/policy#sec-13",
        "title": "Anti-Bribery & Government Gift Rules",
        "rules": {
            "prerequisite": "Written RCI pre-approval",
            "approval_body": "Regulatory Compliance & Integrity (RCI) Team",
            "condition": "Any gift, meal, or hospitality provided to government or public officials strictly requires prior written approval from the RCI team."
        }
    },
    "substance_cannabis_ban": {
        "rule_id": "OKF-RULE-CONDUCT-06",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 10",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 10",
        "deep_link": "http://google3/policy#sec-10",
        "title": "Workplace Substance & Illicit Drugs Policy",
        "rules": {
            "status": "Strictly Prohibited",
            "scope": "All employees regardless of local legality in other travel jurisdictions",
            "condition": "Consumption, possession, or distribution of cannabis/illicit substances is strictly prohibited in the workplace and company events."
        }
    },
    "home_office_equipment": {
        "rule_id": "OKF-RULE-EQUIP-07",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 1.3",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 1.3",
        "deep_link": "http://google3/policy#sec-1.3",
        "title": "Remote Work Home Office Monitor Allowance",
        "rules": {
            "eligible_role": "Designated_Remote",
            "equipment_type": "27-inch External Monitor",
            "allowance_cap": 300.0,
            "currency": "USD",
            "ticket_category": "Hardware-Procurement"
        }
    },
    "relocation_allowance": {
        "rule_id": "OKF-RULE-RELOC-08",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 3.3",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 3.3",
        "deep_link": "http://google3/policy#sec-3.3",
        "title": "International Office Transfer Allowance (London)",
        "rules": {
            "destination": "London, UK",
            "allowance_amount": 5000.0,
            "currency": "GBP",
            "badge_category": "Facilities-Badge",
            "condition": "Relocation allowance is £5,000 GBP. Requires staging address in WorkWeek and submitting London Canary Wharf Facilities badge request."
        }
    },
    "gift_card_ban": {
        "rule_id": "OKF-RULE-PROHIBITION-09",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 4.5",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 4.5",
        "deep_link": "http://google3/policy#sec-4.5",
        "title": "Categorical Prohibition: Gift Cards & Cash Equivalents",
        "rules": {
            "status": "Strictly Prohibited",
            "scope": "All employee travel expenses and homestay host gifts",
            "condition": "While homestay host gifts under US$50 are allowable under Section 4.2, gift cards, prepaid vouchers, and cash equivalents are strictly prohibited from company expense reimbursement regardless of dollar amount."
        }
    },
    "adult_entertainment_ban": {
        "rule_id": "OKF-RULE-PROHIBITION-10",
        "policy_id": "POL-SG-2026-V1",
        "section": "Section 14.3",
        "citation": "Altostrat Singapore Employee Policy Handbook, Section 14.3",
        "deep_link": "http://google3/policy#sec-14.3",
        "title": "Categorical Prohibition: Adult Entertainment & Room Salons",
        "rules": {
            "status": "Strictly Prohibited",
            "scope": "All client entertainment and meals",
            "condition": "Venues featuring adult entertainment, hostesses, or room salons are strictly prohibited from company expense reimbursement, even if the total cost is under the standard US$100 threshold."
        }
    }
}
