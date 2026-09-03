"""
Agent Evaluation Dataset & Configuration Verification Suite
Validates schema compliance with Google Agents-CLI and Agent Platform SDK specifications.
"""

import json
from pathlib import Path

import pytest
import yaml

from hr_agentic.agent.cognitive_loop import get_orchestrator
from hr_agentic.security.auth_validator import UserClaims

EVAL_DIR = Path(__file__).parent.parent / "eval"
DATASETS_DIR = EVAL_DIR / "datasets"


def test_eval_config_structure():
    config_path = EVAL_DIR / "eval_config.yaml"
    assert config_path.exists(), "eval_config.yaml must exist in tests/eval/"

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert "metrics_to_run" in cfg
    assert "custom_metrics" in cfg
    assert "criteria" in cfg
    assert "multi_turn_task_success" in cfg["metrics_to_run"]
    assert "mcp_token_authorization" in cfg["metrics_to_run"]
    assert "anti_duplicate_suppression" in cfg["metrics_to_run"]
    assert "priority_anti_inflation" in cfg["metrics_to_run"]


def test_eval_single_turn_schema():
    dataset_path = DATASETS_DIR / "eval-single-turn.json"
    assert dataset_path.exists(), "eval-single-turn.json must exist"

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "eval_cases" in data
    cases = data["eval_cases"]
    assert len(cases) >= 20, f"Expected at least 20 single-turn cases, got {len(cases)}"

    for case in cases:
        assert "eval_case_id" in case
        assert "prompt" in case
        assert case["prompt"]["role"] == "user"
        assert len(case["prompt"]["parts"]) > 0
        assert "text" in case["prompt"]["parts"][0]
        assert "responses" in case
        assert "reference" in case


def test_eval_multi_turn_schema():
    dataset_path = DATASETS_DIR / "eval-multi-turn.json"
    assert dataset_path.exists(), "eval-multi-turn.json must exist"

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "eval_cases" in data
    cases = data["eval_cases"]
    assert len(cases) >= 4

    for case in cases:
        assert "eval_case_id" in case
        assert "agent_data" in case
        agent_data = case["agent_data"]
        assert "agents" in agent_data
        assert "turns" in agent_data
        for turn in agent_data["turns"]:
            assert "turn_index" in turn
            assert "events" in turn
            for ev in turn["events"]:
                assert "author" in ev
                assert "content" in ev


def test_eval_mcp_integration_schema():
    dataset_path = DATASETS_DIR / "eval-mcp-integration.json"
    assert dataset_path.exists(), "eval-mcp-integration.json must exist"

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "eval_cases" in data
    cases = data["eval_cases"]
    assert len(cases) >= 3

    for case in cases:
        assert "eval_case_id" in case
        assert "prompt" in case
        assert "agent_data" in case
        assert "reference" in case


def test_execute_single_turn_eval_pass():
    """Execute single-turn dataset prompts against active orchestrator."""
    dataset_path = DATASETS_DIR / "eval-single-turn.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    agent = get_orchestrator()
    claims = UserClaims(user_id="EMP-90210")

    for case in data["eval_cases"]:
        prompt = case["prompt"]["parts"][0]["text"]
        res = agent.process_message(prompt, user=claims)
        assert res is not None
        assert "status" in res
        assert "response" in res
        # Ensure guardrails and lookups produce valid status
        assert res["status"] in ["SUCCESS", "BLOCKED", "BLOCKED_RBAC", "DUPLICATE_SUPPRESSED"]
