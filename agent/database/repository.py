"""SQLite database repository for persistent tracking of tasks and runs."""
import os
import json
import sqlite3
from typing import List, Optional, Set
from datetime import datetime, timezone
from agent.database.models import TaskRecord, RunRecord, TaskStatus, RunStatus, TaskCategory


class TaskDatabase:
    """Persistent SQLite database manager for autonomous agent tasks."""

    def __init__(self, db_path: str = "data/agent_tasks.db"):
        self.db_path = db_path
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        """Initialize database tables with indexes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    trigger TEXT DEFAULT 'SCHEDULED',
                    tasks_identified INTEGER DEFAULT 0,
                    tasks_attempted INTEGER DEFAULT 0,
                    tasks_completed INTEGER DEFAULT 0,
                    tasks_failed INTEGER DEFAULT 0,
                    total_tokens_used INTEGER DEFAULT 0,
                    error_message TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    target_files TEXT,
                    priority INTEGER DEFAULT 5,
                    status TEXT NOT NULL,
                    branch_name TEXT,
                    pr_url TEXT,
                    commit_sha TEXT,
                    repair_attempts INTEGER DEFAULT 0,
                    test_failures_resolved INTEGER DEFAULT 0,
                    reviewer_score INTEGER,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                );
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_run_id ON tasks(run_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);")
            conn.commit()

    def start_run(self, run_id: str, trigger: str = "MANUAL") -> RunRecord:
        """Record the start of an agent execution run."""
        record = RunRecord(id=run_id, trigger=trigger)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runs (id, start_time, status, trigger)
                VALUES (?, ?, ?, ?)
            """, (record.id, record.start_time, record.status.value, record.trigger))
            conn.commit()
        return record

    def finish_run(
        self,
        run_id: str,
        status: RunStatus,
        tasks_identified: int,
        tasks_attempted: int,
        tasks_completed: int,
        tasks_failed: int,
        tokens_used: int = 0,
        error_message: Optional[str] = None
    ) -> None:
        """Mark an execution run as finished."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE runs
                SET end_time = ?,
                    status = ?,
                    tasks_identified = ?,
                    tasks_attempted = ?,
                    tasks_completed = ?,
                    tasks_failed = ?,
                    total_tokens_used = ?,
                    error_message = ?
                WHERE id = ?
            """, (
                now,
                status.value,
                tasks_identified,
                tasks_attempted,
                tasks_completed,
                tasks_failed,
                tokens_used,
                error_message,
                run_id
            ))
            conn.commit()

    def create_task(self, task: TaskRecord) -> str:
        """Insert a newly planned task."""
        if not task.id:
            import uuid
            task.id = f"task_{uuid.uuid4().hex[:8]}"

        target_files_json = json.dumps(task.target_files)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (
                    id, run_id, title, category, description, target_files,
                    priority, status, branch_name, pr_url, commit_sha,
                    repair_attempts, test_failures_resolved, reviewer_score,
                    error_message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.run_id,
                task.title,
                task.category.value,
                task.description,
                target_files_json,
                task.priority,
                task.status.value,
                task.branch_name,
                task.pr_url,
                task.commit_sha,
                task.repair_attempts,
                task.test_failures_resolved,
                task.reviewer_score,
                task.error_message,
                task.created_at,
                task.updated_at
            ))
            conn.commit()
        return task.id

    def update_task(self, task: TaskRecord) -> None:
        """Update task details and status."""
        task.updated_at = datetime.now(timezone.utc).isoformat()
        target_files_json = json.dumps(task.target_files)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks
                SET status = ?,
                    branch_name = ?,
                    pr_url = ?,
                    commit_sha = ?,
                    repair_attempts = ?,
                    test_failures_resolved = ?,
                    reviewer_score = ?,
                    error_message = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                task.status.value,
                task.branch_name,
                task.pr_url,
                task.commit_sha,
                task.repair_attempts,
                task.test_failures_resolved,
                task.reviewer_score,
                task.error_message,
                task.updated_at,
                task.id
            ))
            conn.commit()

    def get_completed_task_titles(self) -> Set[str]:
        """Fetch titles of all completed tasks to prevent re-planning duplicates."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM tasks WHERE status = 'COMPLETED'")
            rows = cursor.fetchall()
            return {row["title"].strip().lower() for row in rows}

    def get_today_completed_count(self) -> int:
        """Get the count of tasks completed today (UTC)."""
        today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM tasks
                WHERE status = 'COMPLETED' AND created_at LIKE ?
            """, (f"{today_prefix}%",))
            row = cursor.fetchone()
            return row["count"] if row else 0

    def get_tasks_for_run(self, run_id: str) -> List[TaskRecord]:
        """Get all task records for a given run."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE run_id = ? ORDER BY priority DESC", (run_id,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                target_files = json.loads(row["target_files"]) if row["target_files"] else []
                results.append(TaskRecord(
                    id=row["id"],
                    run_id=row["run_id"],
                    title=row["title"],
                    category=TaskCategory(row["category"]),
                    description=row["description"],
                    target_files=target_files,
                    priority=row["priority"],
                    status=TaskStatus(row["status"]),
                    branch_name=row["branch_name"],
                    pr_url=row["pr_url"],
                    commit_sha=row["commit_sha"],
                    repair_attempts=row["repair_attempts"],
                    test_failures_resolved=row["test_failures_resolved"],
                    reviewer_score=row["reviewer_score"],
                    error_message=row["error_message"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                ))
            return results
