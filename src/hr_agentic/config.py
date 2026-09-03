"""
Global System Configuration & Constants
"""

import os
import sys
from pathlib import Path

# Load .env file if present in workspace root
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    try:
        with open(_env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("\"'"))
    except Exception:
        pass

_is_pytest = "pytest" in sys.modules or bool(os.getenv("PYTEST_CURRENT_TEST"))
_default_env = "test" if _is_pytest else "production"
APP_ENV = os.getenv("APP_ENV", _default_env)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_USER_ID = "EMP-90210"
AUTOMATION_ORIGIN = "AI_HR_AGENT_MVP1"

# Model Context Protocol (MCP) Configuration
# Decoupled from cleartext code; loaded securely from environment / Secret Manager
MCP_TOKEN = os.getenv("MCP_TOKEN", "")
# For hermetic unit testing, fall back to safe ephemeral test token if unconfigured
if not MCP_TOKEN and APP_ENV in ("test", "testing"):
    MCP_TOKEN = "mcp_test_ephemeral_token_00000000"

USE_MCP_CONNECTORS = os.getenv("USE_MCP_CONNECTORS", "true").lower() in ("true", "1", "yes")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/api/v1/mcp/rpc")

# Mock SaaS Integration URL (Aish Prabhat Elevate Module 3)
MOCK_SAAS_URL = os.getenv("MOCK_SAAS_URL", "https://mock-saas.aishprabhat.demo.altostrat.com")

# Vertex AI & Gemini Foundation Model Configuration
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() in (
    "true",
    "1",
    "yes",
)
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "genial-union-475913-i7")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Cloud Firestore Native Persistence Configuration
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID", GOOGLE_CLOUD_PROJECT)
FIRESTORE_DATABASE = os.getenv("FIRESTORE_DATABASE", "(default)")
