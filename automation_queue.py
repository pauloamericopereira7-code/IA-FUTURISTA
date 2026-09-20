# -*- coding: utf-8 -*-
"""Sistema de automações com fila, aprovação e auditoria completa."""

import json
import logging
import sqlite3
import subprocess
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger("automation")
logger.setLevel(logging.DEBUG)

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
DB_PATH = CACHE_DIR / "automations.db"


class TaskStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class AutomationTask:
    """Tarefa de automação com auditoria completa."""

    def __init__(
        self,
        name: str,
        description: str,
        action: str,
        params: dict,
        requires_approval: bool = True,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.action = action
        self.params = params
        self.status = TaskStatus.PENDING
        self.requires_approval = requires_approval
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.logs = []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "params": self.params,
            "status": self.status.value,
            "requires_approval": self.requires_approval,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "logs": self.logs,
        }


class AutomationQueue:
    """Fila de automações com aprovação do usuário."""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.tasks: dict[str, AutomationTask] = {}
        self._init_db()
        self._load_tasks()

    def _init_db(self):
        """Initialize automation database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                action TEXT NOT NULL,
                params TEXT,
                status TEXT DEFAULT 'pending',
                requires_approval BOOLEAN DEFAULT 1,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                result TEXT,
                error TEXT,
                logs TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY,
                task_id TEXT,
                event TEXT,
                timestamp TEXT,
                details TEXT,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
            """
        )
        conn.commit()
        conn.close()
        logger.info("Automation DB initialized")

    def _load_tasks(self):
        """Load tasks from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tasks")

        for row in c.fetchall():
            task = AutomationTask(
                name=row["name"],
                description=row["description"],
                action=row["action"],
                params=json.loads(row["params"] or "{}"),
                requires_approval=bool(row["requires_approval"]),
            )
            task.id = row["id"]
            task.status = TaskStatus(row["status"])
            task.created_at = row["created_at"]
            task.started_at = row["started_at"]
            task.completed_at = row["completed_at"]
            task.result = row["result"]
            task.error = row["error"]
            task.logs = json.loads(row["logs"] or "[]")
            self.tasks[task.id] = task

        conn.close()
        logger.info(f"Loaded {len(self.tasks)} tasks from DB")

    def _save_task(self, task: AutomationTask):
        """Persist task to database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            INSERT OR REPLACE INTO tasks 
            (id, name, description, action, params, status, requires_approval, 
             created_at, started_at, completed_at, result, error, logs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.name,
                task.description,
                task.action,
                json.dumps(task.params),
                task.status.value,
                int(task.requires_approval),
                task.created_at,
                task.started_at,
                task.completed_at,
                task.result,
                task.error,
                json.dumps(task.logs),
            ),
        )
        conn.commit()
        conn.close()

    def _audit_log(self, task_id: str, event: str, details: str = ""):
        """Log audit event."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO audit_log (task_id, event, timestamp, details)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, event, datetime.now().isoformat(), details),
        )
        conn.commit()
        conn.close()
        logger.info(f"Audit: {event} for task {task_id}")

    def enqueue(self, task: AutomationTask) -> str:
        """Add task to queue."""
        self.tasks[task.id] = task
        self._save_task(task)
        self._audit_log(task.id, "ENQUEUED", f"Task: {task.name}")
        logger.info(f"Task enqueued: {task.id} ({task.name})")
        return task.id

    def approve(self, task_id: str):
        """Approve a pending task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task_id} is not pending")

        task.status = TaskStatus.APPROVED
        self._save_task(task)
        self._audit_log(task_id, "APPROVED")
        logger.info(f"Task approved: {task_id}")

    def reject(self, task_id: str, reason: str = ""):
        """Reject a pending task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        task.status = TaskStatus.REJECTED
        self._save_task(task)
        self._audit_log(task_id, "REJECTED", reason)
        logger.info(f"Task rejected: {task_id}")

    def get_pending(self) -> list[AutomationTask]:
        """Get all pending tasks awaiting approval."""
        return [
            t for t in self.tasks.values()
            if t.status == TaskStatus.PENDING and t.requires_approval
        ]

    def get_approved(self) -> list[AutomationTask]:
        """Get approved tasks ready to run."""
        return [t for t in self.tasks.values() if t.status == TaskStatus.APPROVED]

    def get_history(self, limit: int = 50) -> list[dict]:
        """Get task execution history."""
        return sorted(
            [t.to_dict() for t in self.tasks.values()],
            key=lambda x: x["created_at"],
            reverse=True,
        )[:limit]

    def execute(self, task_id: str, executor: Optional[Callable] = None) -> dict:
        """Execute an approved task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        if task.status != TaskStatus.APPROVED:
            raise ValueError(f"Task {task_id} is not approved")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self._save_task(task)
        self._audit_log(task_id, "STARTED")

        try:
            if executor:
                result = executor(task)
            else:
                result = self._execute_default(task)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.logs.append(f"✓ Completed: {result}")
            self._audit_log(task_id, "COMPLETED", json.dumps(result))
            logger.info(f"Task completed: {task_id}")

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.logs.append(f"✗ Error: {e}")
            self._audit_log(task_id, "FAILED", str(e))
            logger.error(f"Task failed: {task_id} - {e}")

        self._save_task(task)
        return task.to_dict()

    def _execute_default(self, task: AutomationTask) -> str:
        """Default executor for common actions."""
        if task.action == "run_command":
            cmd = task.params.get("command")
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            return result.stdout or result.stderr

        elif task.action == "run_script":
            script = task.params.get("script")
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout or result.stderr

        elif task.action == "write_file":
            path = task.params.get("path")
            content = task.params.get("content")
            Path(path).write_text(content)
            return f"File written: {path}"

        else:
            raise ValueError(f"Unknown action: {task.action}")


# Singleton instance
queue = AutomationQueue()
