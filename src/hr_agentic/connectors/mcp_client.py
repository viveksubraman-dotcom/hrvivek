"""
Model Context Protocol (MCP) Client Connector
Connects the HR Agentic Orchestrator to HRMS and ITMS MCP Services.
"""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

import httpx

from ..config import MCP_SERVER_URL, MCP_TOKEN
from ..mcp.server import get_mcp_server

logger = logging.getLogger("hr_agentic.connectors.mcp_client")


class MCPClient:
    """
    Client for Model Context Protocol (MCP) tool invocation with Bearer Token Authorization.
    Supports in-process direct dispatch and HTTP remote dispatch.
    """

    def __init__(
        self, token: Optional[str] = None, server_url: Optional[str] = None, use_http: bool = False
    ):
        self.token = token or MCP_TOKEN
        self.server_url = server_url or MCP_SERVER_URL
        self.use_http = use_http

    def _build_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": f"mcp-req-{uuid.uuid4().hex[:8]}",
            "method": method,
            "params": {**params, "_auth_token": self.token},
        }

    def _dispatch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch JSON-RPC payload via HTTP or in-process server."""
        if self.use_http and self.server_url:
            headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            try:
                res = httpx.post(self.server_url, json=payload, headers=headers, timeout=10.0)
                if res.status_code == 401:
                    raise PermissionError(
                        "MCP Authorization Failed (HTTP 401): Invalid or missing token."
                    )
                res.raise_for_status()
                return res.json()
            except httpx.HTTPError as e:
                logger.error(f"HTTP transport failure to MCP server {self.server_url}: {e}")
                raise RuntimeError(f"MCP server communication failed: {e}")

        # In-process direct dispatch
        server = get_mcp_server()
        return server.handle_jsonrpc(payload, auth_token=self.token)

    def initialize(self) -> Dict[str, Any]:
        """Send MCP initialize handshake."""
        req = self._build_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hr-agentic-orchestrator", "version": "2.2.0"},
            },
        )
        res = self._dispatch(req)
        if "error" in res:
            raise PermissionError(f"MCP Initialize Error: {res['error']['message']}")
        return res.get("result", {})

    def list_tools(self) -> List[Dict[str, Any]]:
        """Query available tools from MCP server."""
        req = self._build_request("tools/list", {})
        res = self._dispatch(req)
        if "error" in res:
            raise PermissionError(f"MCP Tools List Error: {res['error']['message']}")
        return res.get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with arguments."""
        req = self._build_request("tools/call", {"name": tool_name, "arguments": arguments})
        res = self._dispatch(req)
        if "error" in res:
            err = res["error"]
            if err.get("code") == -32000:
                raise PermissionError(f"MCP Authorization Failed: {err.get('message')}")
            raise RuntimeError(f"MCP Tool Call Failed: {err.get('message')}")

        result_data = res.get("result", {})
        if result_data.get("isError"):
            error_msg = result_data.get("error") or "Unknown tool execution error"
            raise ValueError(f"MCP tool '{tool_name}' execution error: {error_msg}")

        # Return structured content if present, else parse text
        if "structuredContent" in result_data:
            return result_data["structuredContent"]

        content = result_data.get("content", [])
        if content and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except json.JSONDecodeError:
                return {"text": content[0]["text"]}

        return result_data

    # --------------------------------------------------------------------------
    # WorkWeek (HRMS) MCP Operations
    # --------------------------------------------------------------------------
    def get_employee_profile(self, employee_id: str) -> Dict[str, Any]:
        return self.call_tool("workweek_get_employee_profile", {"employee_id": employee_id})

    def get_leave_balances(self, employee_id: str) -> Dict[str, Any]:
        return self.call_tool("workweek_get_leave_balances", {"employee_id": employee_id})

    def update_contact(
        self,
        employee_id: str,
        home_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        args = {"employee_id": employee_id}
        if home_address:
            args["home_address"] = home_address
        if phone_number:
            args["phone_number"] = phone_number
        return self.call_tool("workweek_update_contact", args)

    def submit_leave_request(
        self, employee_id: str, leave_type: str, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        return self.call_tool(
            "workweek_submit_leave_request",
            {
                "employee_id": employee_id,
                "leave_type": leave_type,
                "start_date": start_date,
                "end_date": end_date,
            },
        )

    # --------------------------------------------------------------------------
    # ServiceImmediately (ITMS) MCP Operations
    # --------------------------------------------------------------------------
    def get_incident(self, ticket_id: str) -> Dict[str, Any]:
        return self.call_tool("service_immediately_get_incident", {"ticket_id": ticket_id})

    def create_incident(
        self,
        requestor_id: str,
        category: str,
        short_desc: str,
        priority: str = "3 - Moderate",
        shipping_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        args = {
            "requestor_id": requestor_id,
            "category": category,
            "short_description": short_desc,
            "priority": priority,
        }
        if shipping_address:
            args["shipping_address"] = shipping_address
        return self.call_tool("service_immediately_create_incident", args)

    def add_comment(self, ticket_id: str, author_id: str, comment_text: str) -> Dict[str, Any]:
        return self.call_tool(
            "service_immediately_add_comment",
            {"ticket_id": ticket_id, "author_id": author_id, "comment_text": comment_text},
        )

    def update_status(
        self, ticket_id: str, new_status: str, resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        args = {"ticket_id": ticket_id, "new_status": new_status}
        if resolution_notes:
            args["resolution_notes"] = resolution_notes
        return self.call_tool("service_immediately_update_status", args)

    def reset(self):
        """Reset MCP server mock state."""
        get_mcp_server().reset()


_mcp_client: Optional[MCPClient] = None


def get_mcp_client(token: Optional[str] = None) -> MCPClient:
    global _mcp_client
    if _mcp_client is None or (token and token != _mcp_client.token):
        _mcp_client = MCPClient(token=token)
    return _mcp_client
