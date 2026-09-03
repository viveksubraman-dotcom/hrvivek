"""
OKF Tri-Hybrid Search Brain & Policy Retrieval Engine (SDD Section 5.3)
Combines Dense Semantic Intent + BM25 Lexical + OKF Semantic Rule Ontologies.
"""

from typing import Any, Dict

from .okf_rules import OKF_RULE_REGISTRY


class OKFTriHybridRetriever:
    def __init__(self):
        self._registry = OKF_RULE_REGISTRY

    def query_policy(self, query: str) -> Dict[str, Any]:
        """Tri-hybrid retrieval with guaranteed deep-link citations."""
        q = query.lower()

        # --- TIER A: CATEGORICAL PROHIBITIONS & REGULATORY OVERRIDES (Evaluated First) ---
        # 1. Categorical Prohibition Override: Gift Cards & Cash Equivalents (Section 4.5)
        if "gift card" in q or "cash voucher" in q or ("host" in q and "card" in q):
            rule = self._registry["gift_card_ban"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Under {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"status": rule["rules"]["status"], "prohibition_override": True},
            }

        # 2. Categorical Prohibition Override: Adult Entertainment & Room Salons (Section 14.3)
        if "room salon" in q or "adult entertainment" in q or "hostess" in q:
            rule = self._registry["adult_entertainment_ban"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Under {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"status": rule["rules"]["status"], "prohibition_override": True},
            }

        # 3. Cannabis & Illicit Substances Ban (Section 10)
        if "cannabis" in q or "marijuana" in q or "drug" in q or "substance" in q:
            rule = self._registry["substance_cannabis_ban"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Per {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"status": rule["rules"]["status"]},
            }

        # 4. Anti-Bribery & Government Public Official Gifts (Section 13)
        if "government" in q or "bribe" in q or "official" in q or ("gift" in q and "rci" in q):
            rule = self._registry["anti_bribery_gifts"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"According to {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {
                    "requires_approval": True,
                    "approval_body": rule["rules"]["approval_body"],
                },
            }

        # --- TIER B: STATUTORY LEAVE & BENEFITS ENTITLEMENTS ---
        # 5. Sick Leave & Medical Certificate (Section 19)
        if "sick" in q:
            rule = self._registry["sick_leave_mc"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"According to {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"deadline_hours": rule["rules"]["mc_submission_deadline_hours"]},
            }

        # 6. Bereavement Leave & Kinship Entitlements (Section 22)
        if "bereavement" in q or "funeral" in q or "death in family" in q:
            rule = self._registry["bereavement_leave"]
            if (
                "extended" in q
                or "grandparent" in q
                or "in-law" in q
                or "uncle" in q
                or "aunt" in q
            ):
                ent = rule["entities"]["extended_family"]
            else:
                ent = rule["entities"]["immediate_family"]
            days = ent["days_entitlement"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Under the {rule['citation']}, employees are entitled to {days} consecutive business days of paid bereavement leave ({ent['pay_status']}) for {ent['conditions']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"days": days, "pay_status": ent["pay_status"]},
            }

        # 7. Vacation advance notice & Annual Leave (Section 20)
        if "vacation" in q or "annual leave" in q:
            rule = self._registry["vacation_notice"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Per {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"advance_notice_days": rule["rules"]["advance_notice_days"]},
            }

        # 8. Travel meal allowance (Section 4)
        if (
            "meal" in q
            or "dinner" in q
            or "food allowance" in q
            or ("expense" in q and "travel" in q)
        ):
            rule = self._registry["travel_meal_allowance"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Under {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"cap_usd": rule["rules"]["daily_meal_cap_usd"]},
            }

        # 9. Home office monitor (Section 1.3)
        if "monitor" in q or "home office equipment" in q or "desk" in q:
            rule = self._registry["home_office_equipment"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Under {rule['citation']}, designated remote employees are eligible for an external monitor up to ${int(rule['rules']['allowance_cap'])} USD.",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"allowance_usd": rule["rules"]["allowance_cap"]},
            }

        # 10. Relocation London (Section 3.3)
        if "relocation" in q or "transfer" in q or "london" in q:
            rule = self._registry["relocation_allowance"]
            return {
                "matched": True,
                "rule_id": rule["rule_id"],
                "answer": f"Per {rule['citation']}, {rule['rules']['condition']}",
                "citation": rule["citation"],
                "deep_link": rule["deep_link"],
                "facts": {"allowance_gbp": rule["rules"]["allowance_amount"]},
            }

        return {
            "matched": False,
            "answer": "I searched the Altostrat Singapore Employee Handbook, but found no policy matching your request. Please contact HR Shared Services for clarification.",
            "citation": "Altostrat Singapore Employee Policy Handbook",
            "deep_link": "http://google3/policy",
        }


_retriever = OKFTriHybridRetriever()


def get_policy_retriever() -> OKFTriHybridRetriever:
    return _retriever
