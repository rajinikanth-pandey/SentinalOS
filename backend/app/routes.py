# api/routes.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from schemas.request import AnalyzeRequest
from schemas.response import AnalyzeResponse
from schemas.prompt_request import PromptRequest
from schemas.prompt_reponse import PromptResponse

from orchestrator.orchestrator import SentinelOrchestrator
from gateway import gateway
from database.models import AuditModel
from analytics.analytics import AnalyticsEngine

router = APIRouter()
orchestrator = SentinelOrchestrator()
analytics = AnalyticsEngine()


# ==================== Health Check ====================

@router.get("/health")
def health():
    return {
        "status": "running",
        "service": "SentinelOS",
        "version": "2.0.0",
        "description": "AI Security Gateway with invisible security layer"
    }


# ==================== UNIFIED PROMPT ENDPOINT ====================

@router.post("/prompt", response_model=PromptResponse)
def prompt(request: PromptRequest):
    """
    SINGLE UNIFIED ENDPOINT - The only endpoint users need.
    
    Every prompt goes through:
    1. Security Analysis (Event Parser → Risk Engine → Policy Engine → AI Agents)
    2. Decision: BLOCK → Return security report
    3. Decision: ALLOW/REVIEW → Forward to AI assistant
    
    The user experiences a single assistant with invisible security.
    """
    result = gateway.process(
        prompt=request.prompt,
        user_id=request.user_id,
        session_id=request.session_id
    )
    return result


# ==================== LEGACY ANALYZE ENDPOINT (Keep for testing) ====================

@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    """
    Legacy endpoint - Direct security analysis without chat.
    Used for testing and debugging.
    """
    result = orchestrator.analyze(request.prompt)
    return result


# ==================== History Endpoints ====================

@router.get("/history")
def get_history(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    mode: Optional[str] = None,
    decision: Optional[str] = None
):
    """Get interaction history with optional filtering."""
    logs = AuditModel.get_all(limit=10000)
    
    if mode:
        logs = [log for log in logs if log.get("mode") == mode]
    if decision:
        logs = [log for log in logs if log.get("decision") == decision.upper()]
    
    total = len(logs)
    logs = logs[offset:offset + limit]
    
    return {
        "total": total,
        "logs": logs,
        "pagination": {"limit": limit, "offset": offset}
    }


@router.get("/history/{log_id}")
def get_log_by_id(log_id: str):
    """Get a specific log entry by ID."""
    log = AuditModel.get_by_id(log_id)
    if log:
        return log
    raise HTTPException(status_code=404, detail="Log not found")


@router.delete("/history")
def clear_history(confirm: bool = Query(False)):
    """Clear all history (requires confirmation)."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to clear history")
    
    from database.sqlite_db import db
    success = db.clear_all()
    if success:
        return {"message": "History cleared successfully"}
    raise HTTPException(status_code=500, detail="Failed to clear history")


# ==================== Analytics Endpoints ====================

@router.get("/analytics")
def get_analytics():
    """Get comprehensive analytics from the database."""
    logs = AuditModel.get_all(limit=10000)
    stats = analytics.generate(logs)
    stats["database_stats"] = AuditModel.get_stats()
    return stats


@router.get("/analytics/daily")
def get_daily_analytics(days: int = Query(7, ge=1, le=30)):
    """Get daily analytics for the last N days."""
    logs = AuditModel.get_all(limit=10000)
    daily_stats = analytics.generate_daily_summary(logs)
    
    if daily_stats:
        dates = sorted(daily_stats.keys(), reverse=True)[:days]
        daily_stats = {date: daily_stats[date] for date in dates}
    
    return {"days": days, "daily_stats": daily_stats}


@router.get("/analytics/trends")
def get_trends():
    """Get trend analysis."""
    logs = AuditModel.get_all(limit=10000)
    trends = analytics.generate_trends(logs)
    return trends


@router.get("/stats")
def get_stats():
    """Get database statistics."""
    return AuditModel.get_stats()


@router.get("/search")
def search_logs(query: str = Query(..., min_length=2)):
    """Search logs by prompt content."""
    logs = AuditModel.search(query)
    return {"query": query, "results": len(logs), "logs": logs}