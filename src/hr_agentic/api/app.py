"""
FastAPI Application Entrypoint (WAF System Design Pillar)
Serves Web Chat UI and REST API.
"""
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ..agent.cognitive_loop import get_orchestrator
from ..security.auth_validator import UserClaims

app = FastAPI(title="Enterprise HR Agentic Solution API", version="2.2.0")

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class ChatRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = "EMP-90210"

@app.get("/", response_class=HTMLResponse)
def get_web_ui():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return "<h1>Enterprise HR Agentic Solution API</h1><p>Visit /api/v1/health</p>"

@app.get("/api/v1/health")
def health():
    return {"status": "HEALTHY", "version": "2.2.0", "framework": "Google Cloud WAF & OKF"}

@app.post("/api/v1/chat")
def chat(req: ChatRequest):
    orchestrator = get_orchestrator()
    claims = UserClaims(user_id=req.user_id or "EMP-90210", user_email=f"{req.user_id or 'EMP-90210'}@altostrat.com")
    try:
        res = orchestrator.process_message(req.prompt, user=claims)
        return res
    except Exception as e:
        return {
            "status": "ERROR",
            "category": "VALIDATION_ERROR",
            "response": str(e),
            "tool_calls": []
        }

@app.post("/api/v1/reset")
def reset_state():
    get_orchestrator().reset()
    from ..connectors.workweek import get_workweek_client
    from ..connectors.service_immediately import get_service_immediately_client
    from ..saga.coordinator import get_saga_coordinator
    get_workweek_client().reset()
    get_service_immediately_client().reset()
    get_saga_coordinator().reset()
    return {"status": "RESET_COMPLETE"}

class FeedbackRequest(BaseModel):
    score: int
    deflected: bool
    comments: Optional[str] = None

@app.post("/api/v1/conversations/{conversation_id}/feedback")
def submit_feedback(conversation_id: str, feedback: FeedbackRequest):
    return {
        "status": "SUCCESS",
        "conversation_id": conversation_id,
        "recorded_score": feedback.score,
        "deflected": feedback.deflected,
        "comments": feedback.comments
    }