"""
Global System Configuration & Constants
"""
import os

APP_ENV = os.getenv("APP_ENV", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEFAULT_USER_ID = "EMP-90210"
AUTOMATION_ORIGIN = "AI_HR_AGENT_MVP1"
