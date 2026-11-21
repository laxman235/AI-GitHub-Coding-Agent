"""Agent 3: Developer Agent."""
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from agent.core.llm import LLMClient
from agent.services.repository_service import RepositoryService
from agent.database.models import TaskRecord


class FileOperation(BaseModel):
    path: str
    action: str = "MODIFY"  # MODIFY or CREATE
    content: str


class DeveloperSolution(BaseModel):
    files: List[FileOperation] = Field(default_factory=list)
    explanation: str = ""


class DeveloperAgent:
    """Generates focused Java 21 / Spring Boot 3 code modifications and fixes."""

    def __init__(self, llm: LLMClient, repo_service: RepositoryService):
        self.llm = llm
        self.repo_service = repo_service
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "developer.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Implement Java Spring Boot changes following clean code and SOLID standards."

    def implement_task(self, task: TaskRecord) -> DeveloperSolution:
        """Generate initial code changes for a task."""
        # Read existing target files content to provide context
        file_contexts = []
        for rel_path in task.target_files:
            try:
                content = self.repo_service.read_file_safe(rel_path)
                file_contexts.append(f"--- File: {rel_path} ---\n{content}\n")
            except Exception:
                file_contexts.append(f"--- File: {rel_path} (New file to create) ---\n")

        user_prompt = (
            f"TASK DETAILS:\n"
            f"Title: {task.title}\n"
            f"Category: {task.category.value}\n"
            f"Description: {task.description}\n"
            f"Target Files: {task.target_files}\n\n"
            f"EXISTING FILE CONTEXTS:\n"
            f"{''.join(file_contexts)}\n\n"
            f"Implement the complete solution including any necessary JUnit 5 tests. "
            f"Return full file contents for all modified/created files."
        )

        return self.llm.generate_structured(self.prompt_template, user_prompt, DeveloperSolution)

    def repair_code(
        self,
        task: TaskRecord,
        error_log: str,
        previous_solution: DeveloperSolution
    ) -> DeveloperSolution:
        """Generate repaired solution following compilation or test failure."""
        previous_files_context = "\n".join(
            [f"--- File: {f.path} ---\n{f.content}" for f in previous_solution.files]
        )

        user_prompt = (
            f"A previous implementation of the task failed Maven compilation or tests.\n\n"
            f"TASK: {task.title}\n"
            f"DESCRIPTION: {task.description}\n\n"
            f"PREVIOUSLY GENERATED FILES:\n{previous_files_context}\n\n"
            f"MAVEN FAILURE LOG:\n{error_log}\n\n"
            f"Analyze the exact error above and provide a corrected, working version of the files."
        )

        return self.llm.generate_structured(self.prompt_template, user_prompt, DeveloperSolution)
