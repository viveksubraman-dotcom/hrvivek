"""
Unit Test Suite: Google ADK Golden Evalset & Config Validation
Verifies schema compliance, 4-tier stratification distribution, and configuration integrity
per Google ADK and eval-adk-skill standards.
"""

import json
import os

EVALSET_PATH = "tests/eval/datasets/golden_mas_eval.evalset.json"
CONFIG_PATH = "tests/eval/eval_config.json"


def test_evalset_file_exists():
    assert os.path.exists(EVALSET_PATH), f"Evalset not found at {EVALSET_PATH}"
    assert os.path.exists(CONFIG_PATH), f"Config not found at {CONFIG_PATH}"


def test_evalset_schema_and_tiers():
    with open(EVALSET_PATH) as f:
        data = json.load(f)

    assert "eval_set_id" in data
    assert "name" in data
    assert "eval_cases" in data
    cases = data["eval_cases"]
    assert len(cases) == 43, f"Expected 43 evaluation cases, found {len(cases)}"

    tier_counts = {}
    for case in cases:
        assert "eval_id" in case
        assert "tier" in case
        assert "conversation" in case
        assert len(case["conversation"]) >= 1
        tier = case["tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        # Verify tool uses structure
        for turn in case["conversation"]:
            assert "user_content" in turn
            assert "final_response" in turn
            assert "intermediate_data" in turn
            assert "tool_uses" in turn["intermediate_data"]

    # 4-Tier Stratification Verification
    assert tier_counts.get("Tier 1") == 18, (
        f"Tier 1 expected 18 cases, got {tier_counts.get('Tier 1')}"
    )
    assert tier_counts.get("Tier 2") == 13, (
        f"Tier 2 expected 13 cases, got {tier_counts.get('Tier 2')}"
    )
    assert tier_counts.get("Tier 3") == 6, (
        f"Tier 3 expected 6 cases, got {tier_counts.get('Tier 3')}"
    )
    assert tier_counts.get("Tier 4") == 6, (
        f"Tier 4 expected 6 cases, got {tier_counts.get('Tier 4')}"
    )


def test_eval_config_criteria():
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    assert "criteria" in config
    crit = config["criteria"]
    assert crit.get("tool_trajectory_avg_score") == 0.8
    assert crit.get("response_match_score") == 0.8
    assert crit.get("groundedness") == 1.0
    assert crit.get("abstention") == 2.0
