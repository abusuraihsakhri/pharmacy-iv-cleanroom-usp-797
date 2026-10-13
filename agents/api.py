"""
FastAPI REST API Server for Pharmacy Iv Cleanroom Usp 797.
"""
import os
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastapi.responses import FileResponse
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Pharmacy Iv Cleanroom Usp 797 API",
    description="Illustrative threshold audit; not validated for clinical or USP <797> compliance decisions.",
    version="2.0.0",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/", include_in_schema=False)
def console():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "pharmacy-iv-cleanroom-usp-797", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    latest = next(reversed(supervisor.dossier_registry.values()), None)
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": latest.overall_urgency.value if latest else "NO_EVALUATIONS"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive identifier in input") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Sensitive identifier in input") from None


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: Optional[str] = Header(default=None)):
    expected = os.getenv("AUDIT_READ_TOKEN")
    if not expected or not x_audit_token or not secrets.compare_digest(x_audit_token, expected):
        raise HTTPException(status_code=403, detail="Audit log access disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
