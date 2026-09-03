"""
Global System Configuration & Constants
"""

import os

APP_ENV = os.getenv("APP_ENV", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_USER_ID = "EMP-90210"
AUTOMATION_ORIGIN = "AI_HR_AGENT_MVP1"

# Model Context Protocol (MCP) Configuration
MCP_TOKEN = os.getenv("MCP_TOKEN", "mcp_WW-RBifouI0mJwWeUcfMa7mbF6SMxqdR4iU_Ey1BKOo")
USE_MCP_CONNECTORS = os.getenv("USE_MCP_CONNECTORS", "true").lower() in ("true", "1", "yes")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/api/v1/mcp/rpc")
