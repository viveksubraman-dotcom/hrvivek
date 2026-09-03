"""
MCP (Model Context Protocol) Integration Test Suite
Validates JSON-RPC 2.0 MCP server, token authentication, and HRMS/ITMS tool invocation.
"""

import pytest

from hr_agentic.connectors.mcp_client import MCPClient
from hr_agentic.mcp.server import MCPServer, get_mcp_server

VALID_MCP_TOKEN = "mcp_WW-RBifouI0mJwWeUcfMa7mbF6SMxqdR4iU_Ey1BKOo"
INVALID_MCP_TOKEN = "mcp_INVALID-TOKEN-99999"


@pytest.fixture(autouse=True)
def reset_mcp_environment():
    server = get_mcp_server()
    server.reset()
    yield
    server.reset()


def test_mcp_server_initialize():
    server = MCPServer(token=VALID_MCP_TOKEN)
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    res = server.handle_jsonrpc(req, auth_token=VALID_MCP_TOKEN)
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == 1
    assert "result" in res
    assert res["result"]["protocolVersion"] == "2024-11-05"
    assert "tools" in res["result"]["capabilities"]
    assert res["result"]["serverInfo"]["name"] == "hrms-itms-mcp-server"


def test_mcp_server_auth_failure_missing_token():
    server = MCPServer(token=VALID_MCP_TOKEN)
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    res = server.handle_jsonrpc(req, auth_token=None)
    assert "error" in res
    assert res["error"]["code"] == -32000
    assert "Unauthorized" in res["error"]["message"]


def test_mcp_server_auth_failure_invalid_token():
    server = MCPServer(token=VALID_MCP_TOKEN)
    req = {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}}
    res = server.handle_jsonrpc(req, auth_token=INVALID_MCP_TOKEN)
    assert "error" in res
    assert res["error"]["code"] == -32000


def test_mcp_server_tools_list():
    server = MCPServer(token=VALID_MCP_TOKEN)
    req = {"jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": {}}
    res = server.handle_jsonrpc(req, auth_token=f"Bearer {VALID_MCP_TOKEN}")
    assert "result" in res
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "workweek_get_employee_profile" in tool_names
    assert "workweek_get_leave_balances" in tool_names
    assert "workweek_update_contact" in tool_names
    assert "workweek_submit_leave_request" in tool_names
    assert "service_immediately_get_incident" in tool_names
    assert "service_immediately_create_incident" in tool_names
    assert "service_immediately_add_comment" in tool_names
    assert "service_immediately_update_status" in tool_names


def test_mcp_client_workweek_profile_lookup():
    client = MCPClient(token=VALID_MCP_TOKEN)
    prof = client.get_employee_profile("EMP-90210")
    assert prof["employee_id"] == "EMP-90210"
    assert prof["name"] == "Jane Doe"
    assert prof["department"] == "Engineering"


def test_mcp_client_workweek_leave_balances():
    client = MCPClient(token=VALID_MCP_TOKEN)
    bal = client.get_leave_balances("EMP-90210")
    assert bal["vacation_remaining_days"] == 5.0
    assert bal["sick_remaining_days"] == 12.0


def test_mcp_client_workweek_update_contact():
    client = MCPClient(token=VALID_MCP_TOKEN)
    res = client.update_contact(
        "EMP-90210", phone_number="+1 512 555 9999", home_address="789 Congress Ave, Austin TX"
    )
    assert res["status"] == "SUCCESS"
    assert res["phone_number"] == "+1 512 555 9999"
    assert "Congress Ave" in res["home_address"]


def test_mcp_client_service_immediately_incident_ops():
    client = MCPClient(token=VALID_MCP_TOKEN)
    # 1. Create incident
    ticket = client.create_incident(
        requestor_id="EMP-90210",
        category="IT-Hardware",
        short_desc="External 4K Monitor flickering via USB-C dock",
        priority="3 - Moderate",
    )
    ticket_id = ticket["ticket_id"]
    assert ticket["status"] == "New"
    assert "INC-" in ticket_id

    # 2. Get incident
    fetched = client.get_incident(ticket_id)
    assert fetched["short_description"] == "External 4K Monitor flickering via USB-C dock"

    # 3. Add comment
    comm = client.add_comment(ticket_id, "EMP-90210", "Swapped HDMI cable, still persists.")
    assert comm["status"] == "SUCCESS"

    # 4. Update status
    up = client.update_status(ticket_id, "In-Progress")
    assert up["status"] == "SUCCESS"
    assert up["new_status"] == "In-Progress"


def test_mcp_client_auth_error_raised():
    bad_client = MCPClient(token=INVALID_MCP_TOKEN)
    with pytest.raises(PermissionError, match="MCP Authorization Failed"):
        bad_client.get_employee_profile("EMP-90210")


def test_mcp_client_unknown_tool_error():
    client = MCPClient(token=VALID_MCP_TOKEN)
    with pytest.raises(ValueError, match="Unknown MCP tool"):
        client.call_tool("non_existent_tool", {"foo": "bar"})
