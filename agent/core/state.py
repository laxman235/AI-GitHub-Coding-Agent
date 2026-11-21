"""Execution state definitions for the agent workflow."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from agent.database.models import TaskRecord, RunRecord


class TaskExecutionContext(BaseModel):
    """Context state for a single task execution turn."""
    task: TaskRecord
    branch_name: str
    repair_count: int = 0
    modified_files: List[str] = Field(default_factory=list)
    maven_test_output: str = ""
    is_compiled: bool = False
    is_tested: bool = False
    is_reviewed: bool = False
    is_committed: bool = False
    is_pushed: bool = False
    diff_text: str = ""


class AgentRunState(BaseModel):
    """Overall execution state for the entire daily run."""
    run_record: RunRecord
    tasks_to_execute: List[TaskRecord] = Field(default_factory=list)
    completed_tasks: List[TaskRecord] = Field(default_factory=list)
    failed_tasks: List[TaskRecord] = Field(default_factory=list)
    tokens_consumed: int = 0
