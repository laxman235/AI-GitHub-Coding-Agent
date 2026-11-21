"""Data models for persistence and agent workflow."""
from enum import Enum
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _get_utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BUILD_FAILED = "BUILD_FAILED"
    TEST_FAILED = "TEST_FAILED"
    REVIEW_REJECTED = "REVIEW_REJECTED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class RunStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class TaskCategory(str, Enum):
    FEATURE = "FEATURE"
    BUG_FIX = "BUG_FIX"
    TEST_IMPROVEMENT = "TEST_IMPROVEMENT"
    REFACTORING = "REFACTORING"
    SECURITY = "SECURITY"


class TaskRecord(BaseModel):
    id: Optional[str] = None
    run_id: str
    title: str
    category: TaskCategory = TaskCategory.FEATURE
    description: str
    target_files: List[str] = Field(default_factory=list)
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    branch_name: Optional[str] = None
    pr_url: Optional[str] = None
    commit_sha: Optional[str] = None
    repair_attempts: int = 0
    test_failures_resolved: int = 0
    reviewer_score: Optional[int] = None
    error_message: Optional[str] = None
    sprint_day: Optional[int] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    required_tests: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=_get_utc_now_iso)
    updated_at: str = Field(default_factory=_get_utc_now_iso)


class SprintRecord(BaseModel):
    sprint_id: str
    start_date: str = Field(default_factory=_get_utc_now_iso)
    current_day: int = 1
    completed_days: List[int] = Field(default_factory=list)
    pending_tasks: List[str] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    failed_tasks: List[str] = Field(default_factory=list)
    pr_urls: List[str] = Field(default_factory=list)
    commit_shas: List[str] = Field(default_factory=list)
    test_results: dict = Field(default_factory=dict)
    blockers: List[str] = Field(default_factory=list)
    is_finished: bool = False
    updated_at: str = Field(default_factory=_get_utc_now_iso)


class RunRecord(BaseModel):
    id: str
    start_time: str = Field(default_factory=_get_utc_now_iso)
    end_time: Optional[str] = None
    status: RunStatus = RunStatus.RUNNING
    trigger: str = "SCHEDULED"
    tasks_identified: int = 0
    tasks_attempted: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tokens_used: int = 0
    error_message: Optional[str] = None
