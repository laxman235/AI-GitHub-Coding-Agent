"""Agent 2: Task Planner Agent."""
import os
import uuid
from typing import List, Set
from pydantic import BaseModel, Field
from agent.core.llm import LLMClient
from agent.database.models import TaskRecord, TaskCategory, TaskStatus
from agent.database.repository import TaskDatabase
from agent.services.repository_service import RepositoryArchitecture
from agent.agents.repository_analyst import AnalystFindings


class PlannedTask(BaseModel):
    title: str
    category: TaskCategory = TaskCategory.FEATURE
    description: str
    target_files: List[str] = Field(default_factory=list)
    priority: int = Field(default=5, ge=1, le=10)
    risk_level: str = "LOW"


class TaskPlannerOutput(BaseModel):
    tasks: List[PlannedTask] = Field(default_factory=list)


class TaskPlannerAgent:
    """Plans meaningful, non-duplicate, high-priority coding tasks."""

    def __init__(self, llm: LLMClient, db: TaskDatabase):
        self.llm = llm
        self.db = db
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "planner.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Generate up to {max_tasks} actionable Java Spring Boot tasks."

    def plan_tasks(
        self,
        arch: RepositoryArchitecture,
        findings: AnalystFindings,
        run_id: str,
        max_tasks: int = 10
    ) -> List[TaskRecord]:
        """Generate deduplicated tasks up to the daily execution ceiling."""
        completed_titles = self.db.get_completed_task_titles()
        today_completed = self.db.get_today_completed_count()
        remaining_budget = max(0, max_tasks - today_completed)

        if remaining_budget <= 0:
            return []

        prompt = self.prompt_template.replace("{max_tasks}", str(min(remaining_budget, 10)))

        context_text = (
            f"Project Root: {arch.root_path}\n"
            f"Controllers: {[c.relative_path for c in arch.controllers]}\n"
            f"Services: {[s.relative_path for s in arch.services]}\n"
            f"DTOs: {[d.relative_path for d in arch.dtos]}\n"
            f"Missing Tests: {arch.missing_test_targets}\n"
            f"Technical Debt Identified: {findings.technical_debt}\n"
            f"Improvement Areas: {findings.improvement_areas}\n"
            f"Previously Completed Task Titles (DO NOT DUPLICATE): {list(completed_titles)[:20]}\n"
        )

        user_prompt = f"Plan up to {remaining_budget} meaningful coding tasks based on this architecture:\n\n{context_text}"
        output = self.llm.generate_structured(prompt, user_prompt, TaskPlannerOutput)

        task_records: List[TaskRecord] = []
        for t in output.tasks:
            # Skip duplicates
            if t.title.strip().lower() in completed_titles:
                continue

            record = TaskRecord(
                id=f"task_{uuid.uuid4().hex[:8]}",
                run_id=run_id,
                title=t.title,
                category=t.category,
                description=t.description,
                target_files=t.target_files,
                priority=t.priority,
                status=TaskStatus.PENDING
            )
            self.db.create_task(record)
            task_records.append(record)

            if len(task_records) >= remaining_budget:
                break

        # Sort by priority descending
        task_records.sort(key=lambda x: x.priority, reverse=True)
        return task_records
