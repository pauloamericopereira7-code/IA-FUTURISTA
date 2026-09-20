# -*- coding: utf-8 -*-
"""API endpoints para automações no servidor FastAPI."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from automation_queue import AutomationTask, queue, TaskStatus
from knowledge_cache import cache

logger = logging.getLogger("api_automation")

router = APIRouter(prefix="/api/automation", tags=["automation"])


class TaskRequest(BaseModel):
    name: str
    description: str
    action: str
    params: dict
    requires_approval: bool = True


class TaskApproval(BaseModel):
    task_id: str
    approved: bool
    reason: str = ""


@router.post("/task/create")
async def create_task(req: TaskRequest):
    """Create a new automation task."""
    task = AutomationTask(
        name=req.name,
        description=req.description,
        action=req.action,
        params=req.params,
        requires_approval=req.requires_approval,
    )
    task_id = queue.enqueue(task)
    return {
        "task_id": task_id,
        "status": task.status.value,
        "requires_approval": task.requires_approval,
    }


@router.get("/tasks/pending")
async def get_pending_tasks():
    """Get tasks awaiting user approval."""
    tasks = queue.get_pending()
    return {"count": len(tasks), "tasks": [t.to_dict() for t in tasks]}


@router.post("/task/approve")
async def approve_task(req: TaskApproval):
    """Approve or reject a task."""
    try:
        if req.approved:
            queue.approve(req.task_id)
            result = queue.execute(req.task_id)
            return {"status": "executed", "result": result}
        else:
            queue.reject(req.task_id, req.reason)
            return {"status": "rejected", "task_id": req.task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/history")
async def get_task_history(limit: int = 50):
    """Get task execution history."""
    history = queue.get_history(limit)
    return {"count": len(history), "history": history}


@router.get("/cache/stats")
async def get_cache_stats():
    """Get knowledge cache statistics."""
    stats = cache.get_stats()
    return stats


@router.post("/cache/clear")
async def clear_cache():
    """Clear all cache entries."""
    try:
        import os
        db_path = cache.db_path
        if os.path.exists(db_path):
            os.remove(db_path)
        cache._init_db()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
