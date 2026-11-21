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
    acceptance_criteria: List[str] = Field(default_factory=list)
    required_tests: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


DAY_ROADMAP = {
    1: "Day 1: Foundation & Baseline Health - User entity, Role enum, base auth endpoints, security configuration",
    2: "Day 2: Candidate Profile & Resume Ingestion - CandidateProfile entity, Skill entity, Resume parser model, profile API",
    3: "Day 3: AI Service & ATS Matching Engine - FastAPI / Groq integration, ATS scoring engine, Job-Candidate matcher",
    4: "Day 4: Job Discovery & Scraping Connectors - JobPosting entity, Naukri/LinkedIn/Indeed connectors with CAPTCHA/anti-bot compliance, approval gate",
    5: "Day 5: Resume Engineering & Tailoring - Tailored resume generator, cover letter generator, keyword optimizer",
    6: "Day 6: Candidate Dashboard & Application Tracker - JobApplication entity, Kanban state tracker, Daily notifications, React UI integration",
    7: "Day 7: End-to-End Integration, Verification & Final Sprint Report - Multi-stack health verification, end-to-end flow test, final sprint report"
}


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
        max_tasks: int = 2
    ) -> List[TaskRecord]:
        """Generate deduplicated tasks up to the daily execution ceiling (max 2 tasks/day)."""
        sprint = self.db.get_or_create_active_sprint()
        if sprint.is_finished or sprint.current_day > 7:
            return []

        current_day = sprint.current_day
        day_roadmap_goal = DAY_ROADMAP.get(current_day, f"Day {current_day} Sprint Goals")

        completed_titles = self.db.get_completed_task_titles()
        today_completed = self.db.get_today_completed_count()
        # Strictly cap daily execution limit at 2 tasks
        daily_cap = min(max_tasks, 2)
        remaining_budget = max(0, daily_cap - today_completed)

        if remaining_budget <= 0:
            return []

        prompt = self.prompt_template.replace("{max_tasks}", str(remaining_budget))

        vision_block = f"\nUSER PRODUCT VISION & ROADMAP:\n{arch.product_vision}\n" if arch.product_vision else ""

        context_text = (
            f"Project Root: {arch.root_path}\n"
            f"7-DAY SPRINT CONTEXT: Day {current_day}/7 ({day_roadmap_goal})\n"
            f"{vision_block}"
            f"Controllers: {[c.relative_path for c in arch.controllers]}\n"
            f"Services: {[s.relative_path for s in arch.services]}\n"
            f"DTOs: {[d.relative_path for d in arch.dtos]}\n"
            f"Missing Tests: {arch.missing_test_targets}\n"
            f"Technical Debt Identified: {findings.technical_debt}\n"
            f"Improvement Areas: {findings.improvement_areas}\n"
            f"Frontend Present: {arch.has_frontend} (Path: {arch.frontend_path})\n"
            f"AI Microservice Present: {arch.has_ai_service}\n"
            f"Previously Completed Task Titles (DO NOT DUPLICATE): {list(completed_titles)[:20]}\n"
        )

        user_prompt = (
            f"Plan up to {remaining_budget} meaningful coding tasks for Day {current_day} ({day_roadmap_goal}):\n\n"
            f"{context_text}"
        )
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
                status=TaskStatus.PENDING,
                sprint_day=current_day,
                acceptance_criteria=t.acceptance_criteria,
                required_tests=t.required_tests,
                dependencies=t.dependencies
            )
            self.db.create_task(record)
            task_records.append(record)

            if len(task_records) >= remaining_budget:
                break

        # Sort by priority descending
        task_records.sort(key=lambda x: x.priority, reverse=True)
        return task_records
