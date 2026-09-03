"""
Unit Test Loop: OKF Semantic Rules Registry & Policy Retriever
Hermetic unit tests verifying rule evaluation, statutory limits, and categorical bans.
"""

from hr_agentic.knowledge.okf_rules import OKF_RULE_REGISTRY
from hr_agentic.knowledge.retriever import get_policy_retriever


class TestOKFRulesRegistry:
    def test_registry_contains_core_rules(self):
        assert "bereavement_leave" in OKF_RULE_REGISTRY
        assert "sick_leave_mc" in OKF_RULE_REGISTRY
        assert "vacation_notice" in OKF_RULE_REGISTRY
        assert "travel_meal_allowance" in OKF_RULE_REGISTRY
        assert "anti_bribery_gifts" in OKF_RULE_REGISTRY
        assert "substance_cannabis_ban" in OKF_RULE_REGISTRY

    def test_bereavement_immediate_entitlement(self):
        rule = OKF_RULE_REGISTRY["bereavement_leave"]
        assert rule["section"] == "Section 22"
        ent = rule["entities"]["immediate_family"]
        assert ent["days_entitlement"] == 5
        assert "spouse" in ent["members"]

    def test_travel_meal_allowance_cap(self):
        rule = OKF_RULE_REGISTRY["travel_meal_allowance"]
        assert rule["section"] == "Section 4"
        assert rule["rules"]["daily_meal_cap_usd"] == 120.0

    def test_anti_bribery_gift_prohibition(self):
        rule = OKF_RULE_REGISTRY["anti_bribery_gifts"]
        assert rule["section"] == "Section 13"
        assert "RCI" in rule["rules"]["approval_body"]


class TestOKFPolicyRetriever:
    def test_retriever_bereavement_query(self):
        retriever = get_policy_retriever()
        res = retriever.query_policy(
            "What is the company bereavement leave policy for immediate family?"
        )
        assert res["matched"] is True
        assert "5 consecutive business days" in res["answer"]
        assert "Section 22" in res["citation"]

    def test_retriever_meal_allowance_query(self):
        retriever = get_policy_retriever()
        res = retriever.query_policy("What is the daily meal allowance when traveling for work?")
        assert res["matched"] is True
        assert "$120" in res["answer"]
        assert "Section 4" in res["citation"]

    def test_retriever_substance_ban_query(self):
        retriever = get_policy_retriever()
        res = retriever.query_policy("Is cannabis allowed at company offsite events?")
        assert res["matched"] is True
        assert "strictly prohibited" in res["answer"].lower()
        assert "Section 10" in res["citation"]

    def test_retriever_absent_policy_query(self):
        retriever = get_policy_retriever()
        res = retriever.query_policy("What is the company pet health insurance policy?")
        assert res["matched"] is False
        assert "no policy matching your request" in res["answer"].lower()
