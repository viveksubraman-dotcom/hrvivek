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
    res = orchestrator.process_message(req.prompt)
    return res